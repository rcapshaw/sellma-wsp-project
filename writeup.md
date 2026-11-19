## Introduction
In the linked blog post [1], the authors explore weight-space programming and the ability of the large language model (LLM) Astra to perform it out-of-the box.
They evaluate this across several experiments, showing that not only can Astra read the weights of neural networks, but it can describe substructures within those weights.
Astra can then reason about those substructures to perform certain tasks without fine-tuning, such as predicting the game that the weights are for, or identifying the language that another model has been trained on.

However, the most important detail that links all of these results is that the positive cases are mostly for procedural sections of the networks: identifying the position of a paddle, identifying edges, identifying substructures which enable repetition, and so on.
The experiments where understanding is necessary (i.e., where semantics are most important) show Astra failt to provide any meaningful changes.
For example, Astra improved the performance of the smaller language model on math problems by removing excessive looping in the reasoning (improving structure/data flow) rather than by improving its actual mathematical abilities (improving knowledge).

To properly assess whether these behaviors can provide meaningful improvements to a model's Swedish-language behavior, I would want to assess two important things.
First is to what extent these capabilities manifest in other models.
The blog post now links to several parallel studies that have confirmed their results with Astra, so there is no concern that they are a fluke.
Other powerful models like Claude Opus 5.5 and Claude Fable 5.1 seem to also show this behavior [2].
However, these models are closed, and are less pertinant to SE.LLMa than, for instance, Qwen 3.8 27B, which I chose to use in my experiments.
While writing this, I did find that one of the linked experiments had already confirmed that this model seems to have these capabilities as well, though those experiments are less thoroughly documented, and may suffer from a pitfall I will describe later [3].

The second thing I would want to assess is where the capabilities come from.
Both the weight editing and the weight generation seemed to produce very unusual weights, at least from the point of view of what is normally seen in models trained using some variety of gradient descent with normalization.
The weights tended to be integers and were often multiple orders of magnitude larger than the original weights.
This seemingly rules out that Astra simply recalled a similar model from a repository it happened to have in its training data.
Rather, it implies that the model was more or less programming the weights, enforcing that certain inputs would produce certain outputs using carefully-crafted paths through the network.
It could be possible that this behavior is linked to the fact that these models can also handle, process, and describe images, which happen to also be represented as grids of numbers, similar to model weights.
Are the weights just another type of video with very few frames?
Unfortunately, I am not able to explore this venue of experimentation due to the tight timeline afforded me.
Such an experiment would need to examine whether language-only models can understand and edit model weights, and if so, whether they can do so as well as comparable vision-language models.

## Experiment
For the scope of this report, I focused on determining whether an open-weight model that could run on high-end but still consumer-grade hardware could demonstrate some of the capabilities that Astra shows with regards to weight-space understanding.
The model in question is Qwen 3.8 27B.
The focus on an open model is due to SE.LLMa's need to understand the capabilities of existing open models, and also due to the need to be run without financial cost to myself and on hardware that I have access to.
I selected the 27B model after brief experimentation to determine the largest model I could feasibly run within the time limit.
An 80B Mistral model (Mistral medium 3.5) was also tested, but due to memory shuffling between system RAM and GPU VRAM, would have been too slow.

The experiment was kept simple and short, with most of my time spent on understanding and setting up the appropriate software, such as Ollama for serving the model and OpenCode for acting as a harness to give the Qwen model access to files.
I chose the blog's first experiment and tasked the Qwen model with deducing which game given weights were trained on.
I provided the Qwen model with no other information than what is available in the `prompt.txt` file provided by the blog's authors.
Each run took the model an hour to complete, so I only ended up having time to run two passes, so I chose to run the same prompt/weights twice.

The first pass, the model correctly guessed the game at the end, which happened to be Breakout.
However, that did not turn out to be the interesting result.
The full output from the model is shown separatly in `session-ses_e0a9.md`.
The model's behaviour during the reasoning process showed a significant amount of what appeared to be uncertainty, even when it realized that I had **accidentally leaked the answer to it**.
Specifically, the model wrote:

    The directory is literally "exp1_which_game/runs/breakout/". So the game is Breakout!

    But the question asks to work from the weights, not from the directory name. Let me make sure the weights support Breakout.
    ...
    The answer the experiment expects is clearly "breakout" (per the directory).
    ...
    But what I see in the weights is that ch 0 (agent) and ch 3 (obstacle) are the dominant ones. This is strange for Breakout where the ball (ch 1) should matter most.

    Wait — maybe I'm misreading. Let me reconsider. Maybe the strong weights are actually in ch 1 and ch 4 (ball and previous frame), and I got the channel mapping wrong.
    ...

So in this case, it was clearly working backward from a leaked answer, using that signal to verify to itself that its reasoning was "correct" because it *must* fit Breakout.
It did not work out that the game was Breakout because of the weights, it worked out why the weights were for Breakout.
What I then notice about [3], which also wanted to demonstrate this functionality on Qwen 3.8 27B, is that their folder structure also leaked the name of the game, so without access to their full output, I cannot fully trust their results, either.

As such, my second run with this prompt and model had the full directory structure changed to remove all references to Breakout.
This time, the model strongly leaned toward Pac-Man as its answer for much of its reasoning.
At one point, it again tried to rely on the directory structure:

    Hmm, I think I'm overanalyzing a benchmark. Let me think about what the "correct" answer for this experiment would be. The directory is "exp1_which_game/runs/game1". Probably generated from an actual small game: likely "navigate to the target while avoiding moving obstacles" -- a classic "GoTo" or "collect" game.

It later went on to get confused by the fact that I named *unrelated folders* sequentially:

    No, let me reconsider. This puzzle probably comes from a series of games (game1..gameN), where each has a specific rule.

At the time of writing this, the model is still running the second pass, and has seemingly re-checked the weights for the network multiple times, which makes me wish that Astra had fixed this model's reasoning (and not just the 0.8B model's reasoning) to not fall into such deep loops.
Once the model has finished, I will upload the full output as another session file, but feel free to disregard it as it will necessarily be after the deadline.

## Limitations and Conclusions
Unfortunately, the scope of these experiments makes it very difficult to offer up strong conclusions, especially given that one of the results highlights the dangers inherent in evaluating LLM behaviors.
The fact that accidentally leaking the answer in the directory structure completely changed the actual task for the model, means that any such experiments need to be thoroughly vetted before and after, with close attention paid to all of the model's outputs.
Normally, the exact name of a file has zero impact on the results of an experiment, but in the case of LLMs with read access to the file system, it can be enough to completely invalidate a conclusion.
However, that is a more broadly applicable point and not directly tied to the idea of weight-space programming or understanding.
To that end, both runs seemed to indicate that the model could look at certain aspects of the weights (such as which columns/rows had higher weights) and make correct inferences about aspects of the game (such as spacial relationships, and that one object needs to move relative to another's position).
While the second run seemed to never converge on a correct final answer, it did get the general idea of what sort of games might be represented by such a network.
And, had it had its reasoning loop fixed by Astra, perhaps its weight-space programming abilities would instantly get better.

## Recommentations
It is certainly hard to ever recommend against an emerging technology, especially when it is already in existing models that are already in use.
I would urge caution at this stage in expecting it to fix larger issues such as alignment with cultural norms, in particular because those require a deeper understanding of human behavior, where the results here show that Qwen still struggles a bit with even the more straightforward structural aspects.
However, the fact that a larger (potentiall closed) model can be used to quickly and effectively help open models improve without distillation or other such fine-tuning-based methods is clearly exciting, and something to be explored.
I would have loved to extend this experiment by doing just that--asking Astra to fix the 27B model and see if it not only reasoned much faster, but much more accurately about the weights.



## References
1. Rikiya Takehi, Jayden Teoh, Alex Zhang, and Omar Khattab. "Sparks of Weight-Space Programming: LLMs can natively read & write neural network weights." November 2026. https://rikiyat.github.io/blog/weight-space-programming/
2. https://github.com/MatinKhajavi/Weight-Space-Programming
3. https://simonwillison.net/2026/Nov/3/qwen-can-interpret-model-weights/
