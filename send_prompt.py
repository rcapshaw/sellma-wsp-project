#!/usr/bin/env python3
"""
ollama_chat.py – Interactive CLI chat with a local Ollama model.

Prerequisites:
    pip install requests          # (standard HTTP approach)
    # OR
    pip install ollama            # (official SDK)

Usage:
    python ollama_chat.py                          # interactive chat
    python ollama_chat.py --model mistral          # pick a model
    python ollama_chat.py --no-stream              # disable streaming
"""

import argparse
import sys
import requests
import os

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL   = "qwen3.8:latest"


# ──────────────────────────────────────────────
# Core API helpers
# ──────────────────────────────────────────────
def is_ollama_running(base_url: str) -> bool:
    """Return True if the Ollama server responds on the base URL."""
    try:
        r = requests.get(f"{base_url}/api/tags", timeout=3)
        return r.status_code == 200
    except requests.ConnectionError:
        return False


def list_models(base_url: str) -> list[str]:
    """Return the names of all locally-pulled models."""
    r = requests.get(f"{base_url}/api/tags", timeout=5)
    r.raise_for_status()
    return [m["name"] for m in r.json().get("models", [])]


def chat(
    base_url: str,
    model: str,
    messages: list[dict],
    stream: bool = True,
) -> str:
    """
    Send a chat request to Ollama and return the assistant's reply.
    If *stream* is True, tokens are printed as they arrive.
    """
    url  = f"{base_url}/api/chat"
    payload = {
        "model":    model,
        "messages": messages,
        "stream":   stream,
    }

    if not stream:
        r = requests.post(url, json=payload)
        r.raise_for_status()
        content = r.json()["message"]["content"]
        print(content)
        return content

    # ── streaming path ──
    r = requests.post(url, json=payload, stream=True)
    r.raise_for_status()

    full_text = ""
    print(end="")
    for line in r.iter_lines(decode_unicode=True):
        if not line:
            continue
        # Each line is a JSON object: {"message":{"content":"…"},"done":false}
        import json
        chunk = json.loads(line)
        token = chunk.get("message", {}).get("content", "")
        if token:
            print(token, end="", flush=True)
            full_text += token
        if chunk.get("done"):
            break
    print()  # newline after stream ends
    return full_text


# ──────────────────────────────────────────────
# Interactive loop
# ──────────────────────────────────────────────
def run(base_url: str, model: str, file:str, stream: bool) -> None:
    # Verify the server is up
    if not is_ollama_running(base_url):
        sys.exit(
            f"✗ Cannot reach Ollama at {base_url}\n"
            "  Make sure `ollama serve` is running, then try again."
        )

    # Optionally show available models
    try:
        models = list_models(base_url)
        if model not in models and len(models) == 1:
            print(f"  (auto-selecting only available model: {models[0]})")
            model = models[0]
        elif len(models) > 1 and model not in models:
            print(f"  ⚠ '{model}' not found locally. Available: {', '.join(models)}")
    except Exception:
        pass  # non-fatal

    if file and os.path.exists(file):
        with open(file, 'r', encoding='utf8') as promptfile:
            prompt = promptfile.read()

        print(f"\n  Ollama chat  ·  model = {model}  ·  stream = {stream}")
        print("  Commands: /exit  /quit  /clear  /models\n")
        # history.append({"role": "user", "content": prompt})
        print("  AI  › ", end="")

        try:
            # print({"role": "user", "content": prompt})
            reply = chat(base_url, model, [{"role": "user", "content": prompt}], stream=stream)
        except requests.exceptions.HTTPError as e:
            print(f"\n  ✗ Ollama HTTP error: {e}")
        except requests.exceptions.ConnectionError:
            print("\n  ✗ Lost connection to Ollama.")
        except Exception as e:
            print(f"\n  ✗ Unexpected error: {e}")
        exit(0)

    history: list[dict] = []

    while True:
        try:
            user_input = input("\n  You › ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Bye 👋")
            break

        if not user_input:
            continue

        # ── slash commands ──
        if user_input in ("/exit", "/quit"):
            print("\n  Bye 👋")
            break

        if user_input == "/clear":
            history.clear()
            print("  (conversation cleared)")
            continue

        if user_input == "/models":
            try:
                for m in list_models(base_url):
                    print(f"    · {m}")
            except Exception as e:
                print(f"  ⚠ Could not list models: {e}")
            continue

        if user_input == "/model":
            new = input("  Set model › ").strip()
            if new:
                model = new
                print(f"  (model → {model})")
            continue

        # ── normal chat turn ──
        history.append({"role": "user", "content": user_input})
        print("  AI  › ", end="")

        try:
            reply = chat(base_url, model, history, stream=stream)
            history.append({"role": "assistant", "content": reply})
        except requests.exceptions.HTTPError as e:
            print(f"\n  ✗ Ollama HTTP error: {e}")
            # remove the failed user turn so we don't pollute context
            history.pop()
        except requests.exceptions.ConnectionError:
            print("\n  ✗ Lost connection to Ollama.")
            history.pop()
        except Exception as e:
            print(f"\n  ✗ Unexpected error: {e}")
            history.pop()


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat with a local Ollama model")
    parser.add_argument("--model",   default=DEFAULT_MODEL, help="Model name (default: %(default)s)")
    parser.add_argument("--url",     default=OLLAMA_BASE_URL, help="Ollama base URL (default: %(default)s)")
    parser.add_argument("--no-stream", action="store_true", help="Disable token streaming")
    parser.add_argument("--prompt", default=None, help="Use the prompt found in a file")
    args = parser.parse_args()

    run(args.url, args.model, args.prompt, stream=not args.no_stream)

"""
    ## How to use
    # 1. Make sure Ollama is installed and serving
    ollama serve &          # or it's already running

    # 2. Pull a model (if you haven't)
    ollama pull qwen3.8

    # 3. Install the one dependency
    pip install requests

    # 4. Chat
    python ollama_chat.py --model qwen3.8
"""