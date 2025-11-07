# models/llm/inference.py
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class DisclosureLLM:
    def __init__(self, base_model="meta-llama/Meta-Llama-3-8B-Instruct", adapter_path="./llama-winline-lora"):
        self.tokenizer = AutoTokenizer.from_pretrained(base_model)
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model, torch_dtype=torch.float16, device_map="auto"
        )
        self.model = PeftModel.from_pretrained(self.model, adapter_path)
        self.model.eval()

    def predict(self, text: str) -> dict:
        prompt = f"""### Инструкция: Определи наличие disclosure (да/нет).
### Текст: {text}
### Ответ:"""
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        outputs = self.model.generate(**inputs, max_new_tokens=50, temperature=0.1)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return {"disclosure": "да" in response.lower(), "raw": response}