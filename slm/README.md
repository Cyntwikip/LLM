# SLM Fine-Tuning: Coding Assistant with Tool Calling

Fine-tuning a Small Language Model (Llama 3.2 1B) using LoRA via [Unsloth](https://github.com/unslothai/unsloth) to behave as a focused coding assistant — answering only programming questions, emitting structured `<tool_call>` blocks when needed, and refusing off-topic requests.

Designed to run on a free Google Colab T4 GPU (~3 minutes training time).

## Notebooks

### `01_train.ipynb` — Fine-Tuning
Loads `unsloth/Llama-3.2-1B-Instruct` in 4-bit, attaches a LoRA adapter (rank 16, ~11M trainable parameters), and trains for 60 steps on a 31-example hand-crafted dataset. The dataset covers three behaviors:

| Category | Description |
|---|---|
| Direct answers | Coding questions the model answers immediately |
| Tool calls | Questions that trigger a `<tool_call>` JSON block |
| Refusals | Off-topic questions the model politely declines |

Training uses `train_on_responses_only` to mask user/system tokens so the model only learns from assistant outputs. The LoRA adapter is saved to Google Drive for use in the inference notebook.

### `02_inference.ipynb` — Inference & Comparison
Loads the base model and the fine-tuned adapter and runs the same 4 test prompts through both. The fine-tuned model includes a tool execution loop: when it outputs a `<tool_call>` block, the corresponding Python function runs and the result is fed back for a final answer.

Available tools: `run_snippet`, `fetch_docs`, `lookup_error`, `suggest_library`, `search_codebase`, `code_and_run`.

## Files

| File | Description |
|---|---|
| `01_train.ipynb` | LoRA fine-tuning on Colab T4 |
| `02_inference.ipynb` | Base vs fine-tuned comparison with live tool execution |
| `dataset.json` | 31 hand-crafted training examples (direct / tool-call / refusal) |

## Setup

Both notebooks are designed for Google Colab. They mount Google Drive at `MyDrive/SLMDev/` to persist the adapter between sessions.

```
MyDrive/SLMDev/
├── dataset.json               ← copy from this repo
└── coding_assistant_lora/     ← saved by 01_train.ipynb, loaded by 02_inference.ipynb
```
