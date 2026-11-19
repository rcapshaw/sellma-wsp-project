This file contains my notes/scribbles around thoughts after reading the linked blog post.

## Notes:
 1. For a blog post that uses a bit too much hype language in places, it is fairly well-scoped with clear limitations. The future-facing ideas are boisterous, which makes sense in this context, but need to be understood simply as possibilities, not necessarily capabilities that are present now. 
 1. The NNs used seem to range from simple FF ones to more complex attention/transformer-based architecxtures.
 1. Success cases were for **well-known** things. Well-known test games, well-known fail cases, so on.
 1. Experiment 1 leans into there being many games to choose from. Is this true? There are definitely many games used in "arenas", but they make it sound like it could be *any* game at all. MinAtar has only five games. 
 1. Experiment 2 is odd. The model gets it "wrong" but the authors argue that it's correct because getting it actually correct would require a forward pass... I don't really buy that argument. The prompt clearly says "images" not "shapes".
 1. The most important bit of support for me is the section at the very end detailing many cases of other authors reproducing the works, especially in other areas. I don't doubt that Astra is able to do the tasks that are claimed. I only wonder how much it needs to have been exposed to already-correct answers. *Novelty* of Astra's output is in question. Even then, being able to skip the initial training for a model is massive.
1. I really don't like the argument about editing "only" 0.016% of the weights avoids catastrophic forgetting. Two reasons: First, consider an 8B model. 0.016% of the weights is 128,000,000 weights, to say nothing of the magnitude of the edits. Second, this assumes a single application. Likely, real-world applications will want to edit a model many times, where the drift from the original model will compound with each application. However, in their favor, it is clearly far better than editing all of the weights.

### Proceduralizable updates
It is extremely important to notice that the results were almost exclusively for *procedurizable* components of the NNs. Loosely, I mean that these components all reflect something that mimics classical programming.
- Experiment 1: The model's reasoning output describes how the different layers process information, such as focusing on the position of the paddle and the exclusive use of left/right output commands rather than up/down/no-op.
- Experiment 2: Similarly, Astra found geometry in the weights.
- Experiment 3: It differentiated the languages based on two parts: components that capture repetition (copy), which hints at a programming language if present in larger numbers, and the number of unique output tokens (despite the final layer being hidden). Astra was informed that there were three possible choices for language, so this seems like a proccess-of-elimination-style solution.
- Experiment 4 and 5: The authors describe the results as Astra literally programming behaviors into the neural networks. Looking at the reasoning, the way that the weights are assigned is extremely regular, and looks very different from how a learned set of weights would look, which does seem to support that argument.
- Experiment 6: This one is slightly too hard to interpret in the time alotted.
- Experiment 7: Sycophancy manifested as copying.
- Experiment 8: Succeeded by removing an unwanted behavior: looping.
- Experiment 9: Failed because the issue was more fundamental in the *knowledge* learned by the model, not the syntax of the output or the trace of the information through the network. 
 

Biggest open questions after reading:
 1. Do the results rely on the model having seen the answer in its training data? Can this be shown analytically? Is there a similar task to weight-space programming that might be giving the models these results? Most results seem very similar to control theory...
 2. How can this relate to Swedish language models? Or LLMs for less-dominant languages in general? It seems like maybe this capability is not (yet) suited for editing more complex behaviors, especially those focused on knowledge rather than procedure.