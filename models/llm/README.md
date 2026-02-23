LLM fine-tuning notes

Target: Llama 3.1 8B LoRA for disclosure detection in Russian.

Steps:
1) Prepare dataset JSONL with fields: prompt, completion.
2) Run fine_tune.ipynb or convert to a script.
3) Validate with F1 > 0.89, Precision > 0.91, Recall > 0.87.

Recommended commands:
- python fine_tune.py --config configs/lora.yaml
- python inference.py --model models/llm/llama-winline-lora
