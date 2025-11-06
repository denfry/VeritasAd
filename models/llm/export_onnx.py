# models/llm/export_onnx.py
from transformers import AutoModelForCausalLM
from peft import PeftModel
import torch

base_model = AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
model = PeftModel.from_pretrained(base_model, "./llama-winline-lora")
merged = model.merge_and_unload()

dummy_input = torch.randint(0, 1000, (1, 512))
torch.onnx.export(
    merged,
    dummy_input,
    "../../export/llama-disclosure.onnx",
    opset_version=17,
    input_names=["input_ids"],
    output_names=["logits"]
)
