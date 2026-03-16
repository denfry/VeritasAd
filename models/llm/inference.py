# models/llm/inference.py
import torch
import json
import logging

logger = logging.getLogger(__name__)

class DisclosureLLM:
    """Class for detecting advertising disclosure using Llama-3 with LoRA, equipped with web search capabilities."""
    
    def __init__(self, adapter_path: str = "./llama-winline-lora", model_manager=None):
        """
        Initialize DisclosureLLM.
        
        Args:
            adapter_path: Path to LoRA adapter.
            model_manager: Optional ModelManager instance to avoid redundant loading.
        """
        self.adapter_path = adapter_path
        if model_manager:
            self.model, self.tokenizer = model_manager.get_llm(adapter_path)
        else:
            # Fallback for standalone usage
            from transformers import AutoModelForCausalLM, AutoTokenizer
            from peft import PeftModel
            base_model = "meta-llama/Meta-Llama-3-8B-Instruct"
            self.tokenizer = AutoTokenizer.from_pretrained(base_model)
            self.model = AutoModelForCausalLM.from_pretrained(
                base_model, torch_dtype=torch.float16, device_map="auto"
            )
            self.model = PeftModel.from_pretrained(self.model, adapter_path)
            self.model.eval()

        # Initialize web searcher
        try:
            from app.services.web_searcher import WebSearcher
            self.searcher = WebSearcher()
        except ImportError:
            self.searcher = None
            logger.warning("WebSearcher not found, web search capabilities will be disabled.")

    def predict(self, text: str, max_iterations: int = 2) -> dict:
        """
        Analyze text for advertising disclosure, optionally searching the web.
        
        Args:
            text: Text to analyze.
            max_iterations: Maximum number of agentic steps (search + answer).
            
        Returns:
            Dictionary with 'disclosure' (bool) and 'confidence' (float).
        """
        system_prompt = (
            "Ты — эксперт по анализу скрытой рекламы. Твоя задача — определить, содержит ли текст признаки рекламы.\n"
            "Ты можешь искать информацию в интернете, чтобы проверить, являются ли сущности из текста реальными брендами или компаниями.\n"
            "Если тебе нужно найти информацию, ответь ТОЛЬКО в формате JSON: {\"search\": \"запрос для поиска\"}\n"
            "Если тебе хватает информации для финального ответа, ответь ТОЛЬКО в формате JSON: {\"disclosure\": boolean, \"reason\": \"объяснение\", \"confidence\": float}"
        )
        
        conversation_history = [
            f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|>",
            f"<|start_header_id|>user<|end_header_id|>\n\nПроанализируй текст: {text}<|eot_id|>"
        ]

        iteration = 0
        raw_responses = []

        while iteration < max_iterations:
            iteration += 1
            prompt = "".join(conversation_history) + "<|start_header_id|>assistant<|end_header_id|>\n\n"
            
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs, 
                    max_new_tokens=150, 
                    temperature=0.1, 
                    do_sample=False,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                
            response_text = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
            raw_responses.append(response_text)
            
            try:
                # Clean response text in case of extra tokens
                json_str = response_text.strip()
                if "{" in json_str and "}" in json_str:
                    json_str = json_str[json_str.find("{"):json_str.rfind("}")+1]
                
                result = json.loads(json_str)
                
                # Check if model wants to search
                if "search" in result and self.searcher and iteration < max_iterations:
                    query = result["search"]
                    logger.info(f"LLM requested web search for: '{query}'")
                    
                    search_results = self.searcher.search_sync(query)
                    
                    if search_results:
                        context = "\n".join([f"- {r['title']}: {r['snippet']}" for r in search_results])
                        search_feedback = f"Результаты поиска по запросу '{query}':\n{context}"
                    else:
                        search_feedback = f"Поиск по запросу '{query}' не дал результатов."
                    
                    conversation_history.append(f"<|start_header_id|>assistant<|end_header_id|>\n\n{json_str}<|eot_id|>")
                    conversation_history.append(f"<|start_header_id|>user<|end_header_id|>\n\n{search_feedback}\nС учетом этой информации, сделай финальный вывод.<|eot_id|>")
                    continue
                    
                # Final response
                return {
                    "disclosure": bool(result.get("disclosure", False)),
                    "reason": str(result.get("reason", "")),
                    "confidence": float(result.get("confidence", 0.0)),
                    "raw": response_text,
                    "iterations": iteration
                }
            except Exception as e:
                logger.error(f"Failed to parse LLM response: {e}. Raw: {response_text}")
                break

        # Fallback if loop breaks or parsing fails completely
        final_raw = raw_responses[-1] if raw_responses else ""
        return {
            "disclosure": "true" in final_raw.lower() or "да" in final_raw.lower() or "реклам" in final_raw.lower(),
            "reason": "fallback_parsing_or_max_iterations_reached",
            "confidence": 0.5,
            "raw": final_raw,
            "iterations": iteration
        }
