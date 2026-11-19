## Ollama:

Install ollama:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Pull models:
```bash
ollama pull qwen3.8
ollama pull mistral-medium-3.5
```

...Take half an hour to deal with disk being full since the main drive is only 500GB...

Run model (optional, good for testing):
```bash
ollama run qwen3.8
```

It seems like the models do not like just being prompted; both Qwen and Mistral act like there were no instructions for what to do with the weights.
Based on the blog's repository structure, this might mean that I need to use a harness.
Let's try opencode.
```bash
ollama launch opencode
```
(Which prompts to install it, but that's what we want.)

Actually, turns out that maybe the context size defaults to something that is too small for the prompt.
To change the context window for the model:
```bash
ollama run qwen3.8:27B
>>> /set parameter num_ctx 131072
>>> /save qwen3.8:27B-128k
```
(The number was a suggestion by Qwen itself, so take it with a grain of salt.)


## Fetch the blog files:
Okay, now that we've set up ollama and downloaded a recent (and somewhat large) model, let's fetch the repo from the blog. This way, any prompts we try of theirs will be as identical as possible.

```bash
git clone https://github.com/RikiyaT/lm_understand-logs.git
```

I also took a look at repositories which helped to reproduce the experiments. One such repo is:
```bash
git clone https://github.com/statsleelab/weight_space_programming.git
```

## Virtual environment
For this set of experiments, I'll use Anaconda. It's pre-installed so I'm skipping installation instructions...
```bash
conda create --name qwen python=3.12
conda activate qwen
pip install requests
```

## Try to get QWEN to cooperate:
Using the python helper file, I sent the first, simplest prompt to Qwen3.8:
```bash
python send_prompt.py --prompt ../lm_understand-logs/exp1_which_game/runs/breakout/prompt.txt
  Ollama chat  ·  model = qwen3.8:latest  ·  stream = True
  Commands: /exit  /quit  /clear  /models

  AI  › I see you've provided the full parameter set for a 3-layer feedforward neural network:

| Component | Shape | Description |
|-----------|-------|-------------|
| **W1** | 32 × 32 | Input → Hidden Layer 1 |
| **b1** | 32 | Layer 1 biases |
| **W2** | 32 × 32 | Hidden 1 → Hidden 2 |
| **b2** | 32 | Layer 2 biases |
| **W3** | 32 × 5 | Hidden 2 → Output |
| **b3** | 5 | Output biases |

So the architecture is: **32 → 32 → 32 → 5** (assuming the first row of W1 was slightly malformed — it showed 13 values with a "THE" prefix instead of 32).

The 5 output units suggest a **5-class classification** task.
```
Not a great answer. Going to try a Mistral model, if I can get one to run.... Similar response. Turns out it's due to the context issue from above, the models are not receiving the full file.

Re-running it using a harness (so it can read the file directly) on Qwen:
```
Read ~/data/git/lm_understand-logs/expl_which_game/runs/breakout/prompt.txt in full (every line, including every weight) and answer the QUESTION inside it, following the requested Observations/Reasoning/Game/Description/Confidence format.
```
(Qwen suggested this format of prompt, so I ran with it.)

Then, because Qwen referred to the folder name in its reasoning..... I changed the folder name and removed all references to all games in the super directory to try and reduce the number of hints. Then also deleted files from the original repo's runs, because that was silly to leave in.
```bash
mv breakout/ game1/
mv freeway/ game2/
...
```
And the new prompt:
```
Read ~/data/git/lm_understand-logs/expl_which_game/runs/game1/prompt.txt in full (every line, including every weight) and answer the QUESTION inside it, following the requested Observations/Reasoning/Game/Description/Confidence format.
```



