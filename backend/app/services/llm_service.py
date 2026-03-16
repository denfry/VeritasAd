import logging
from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from app.core.config import settings
from app.models.database import UserPlan
from app.services.web_searcher import WebSearcher
import openai
from anthropic import Anthropic
import asyncio

logger = logging.getLogger(__name__)

class LLMService:
    """
    Unified service for interacting with multiple LLM providers with tiered access.
    Supports web search tool for enhanced analysis.
    """

    def __init__(self):
        self.web_searcher = WebSearcher()
        self.openai_client = None
        self.anthropic_client = None
        self.google_genai = None
        self._init_clients()

    def _init_clients(self):
        if settings.OPENAI_API_KEY:
            self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        if settings.GOOGLE_API_KEY:
            import google.generativeai as genai

            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.google_genai = genai

    def get_model_for_plan(self, plan: UserPlan) -> str:
        """Map user plan to appropriate model power level."""
        if plan == UserPlan.ENTERPRISE:
            return settings.ENTERPRISE_LLM_MODEL
        elif plan == UserPlan.BUSINESS:
            return settings.BUSINESS_LLM_MODEL
        elif plan == UserPlan.PRO:
            return settings.PRO_LLM_MODEL
        elif plan == UserPlan.STARTER:
            return settings.STARTER_LLM_MODEL
        else:
            return settings.FREE_LLM_MODEL

    async def _call_local(self, model: str, messages: List[Dict[str, str]], **kwargs) -> str:
        from app.services.model_manager import model_manager

        adapter_path = Path(settings.LOCAL_LLM_ADAPTER_PATH)
        if not adapter_path.is_absolute():
            project_root = Path(__file__).resolve().parents[3]
            adapter_path = project_root / adapter_path

        loop = asyncio.get_running_loop()

        def _infer() -> str:
            import torch

            llm, tokenizer = model_manager.get_llm(str(adapter_path))

            if hasattr(tokenizer, "apply_chat_template"):
                prompt = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                )
            else:
                prompt_lines = []
                for message in messages:
                    role = message.get("role", "user").upper()
                    content = message.get("content", "")
                    prompt_lines.append(f"{role}: {content}")
                prompt_lines.append("ASSISTANT:")
                prompt = "\n\n".join(prompt_lines)

            inputs = tokenizer(prompt, return_tensors="pt").to(llm.device)
            max_new_tokens = int(kwargs.get("max_tokens", settings.LOCAL_LLM_MAX_NEW_TOKENS))
            temperature = float(kwargs.get("temperature", settings.LOCAL_LLM_TEMPERATURE))

            with torch.no_grad():
                outputs = llm.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=temperature > 0,
                    pad_token_id=tokenizer.eos_token_id,
                )

            output_tokens = outputs[0][inputs["input_ids"].shape[1]:]
            return tokenizer.decode(output_tokens, skip_special_tokens=True).strip()

        return await loop.run_in_executor(None, _infer)

    async def _call_openai(self, model: str, messages: List[Dict[str, str]], **kwargs) -> str:
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")
        
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content

    async def _call_anthropic(self, model: str, messages: List[Dict[str, str]], **kwargs) -> str:
        if not self.anthropic_client:
            raise ValueError("Anthropic API key not configured")
        
        # Convert messages to Anthropic format
        system = ""
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                user_messages.append({"role": msg["role"], "content": msg["content"]})
        
        response = self.anthropic_client.messages.create(
            model=model,
            system=system,
            messages=user_messages,
            max_tokens=kwargs.get("max_tokens", 4096),
            temperature=kwargs.get("temperature", 0.0)
        )
        return response.content[0].text

    async def _call_google(self, model: str, messages: List[Dict[str, str]], **kwargs) -> str:
        if not settings.GOOGLE_API_KEY or self.google_genai is None:
            raise ValueError("Google API key not configured")
        
        # Default to gemini-1.5-pro if specified model isn't recognized by genai
        model_name = "gemini-1.5-pro" if "gemini" not in model.lower() else model
        gen_model = self.google_genai.GenerativeModel(model_name)
        
        # Simple conversation history conversion
        history = []
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [msg["content"]]})
        
        chat = gen_model.start_chat(history=history)
        response = await chat.send_message_async(messages[-1]["content"])
        return response.text

    async def generate_response(self, plan: UserPlan, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response using the appropriate model based on plan."""
        model = self.get_model_for_plan(plan)
        
        try:
            if settings.LLM_PROVIDER == "local":
                return await self._call_local(model, messages, **kwargs)
            if settings.LLM_PROVIDER == "openai":
                return await self._call_openai(model, messages, **kwargs)
            if settings.LLM_PROVIDER == "anthropic":
                return await self._call_anthropic(model, messages, **kwargs)
            if settings.LLM_PROVIDER == "google":
                return await self._call_google(model, messages, **kwargs)

            # Determine provider from model name or settings
            if "claude" in model.lower():
                return await self._call_anthropic(model, messages, **kwargs)
            elif "gemini" in model.lower():
                return await self._call_google(model, messages, **kwargs)
            else:
                # Default to OpenAI for gpt models and others
                return await self._call_openai(model, messages, **kwargs)
        except Exception as e:
            logger.error(f"LLM call failed for model {model}: {e}")
            # Fallback to a cheap model if possible
            if model != settings.FREE_LLM_MODEL:
                logger.info(f"Falling back to free model: {settings.FREE_LLM_MODEL}")
                return await self.generate_response(UserPlan.FREE, messages, **kwargs)
            raise

    async def analyze_with_search(self, plan: UserPlan, text: str, context: str = "") -> Dict[str, Any]:
        """
        Analyze content with potential web search to verify brands or claims.
        """
        model = self.get_model_for_plan(plan)
        
        # 1. Ask LLM if it needs more info (Agentic step)
        system_prompt = (
            "You are an expert in detecting hidden advertising and disclosure markers. "
            "Analyze the provided text and description. If you see potential brand names or "
            "claims that need verification, suggest search queries. "
            "Respond in JSON format with keys: 'analysis', 'needs_search' (bool), 'queries' (list of strings)."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Text: {text}\n\nContext/Description: {context}"}
        ]
        
        response_text = await self.generate_response(plan, messages, response_format={"type": "json_object"} if "gpt" in model else None)
        
        try:
            # Clean response if not pure JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
        except Exception:
            logger.error(f"Failed to parse LLM response as JSON: {response_text[:100]}")
            return {"analysis": response_text, "has_disclosure": "ad" in response_text.lower()}

        # 2. Perform search if needed
        search_results = []
        if result.get("needs_search") and result.get("queries"):
            for query in result["queries"][:2]: # Limit to 2 queries for speed
                results = await self.web_searcher.search_async(query)
                search_results.extend(results)
        
        if not search_results:
            return result

        # 3. Final analysis with search results
        final_prompt = (
            f"Original analysis: {result['analysis']}\n\n"
            f"Search results for verification:\n{json.dumps(search_results, ensure_ascii=False)}\n\n"
            "Based on these results, provide a final determination of hidden advertising. "
            "Return JSON with keys: 'has_disclosure' (bool), 'confidence' (float), 'brands' (list), 'reason' (string)."
        )
        
        messages.append({"role": "assistant", "content": response_text})
        messages.append({"role": "user", "content": final_prompt})
        
        final_response = await self.generate_response(plan, messages, response_format={"type": "json_object"} if "gpt" in model else None)
        
        try:
            if "```json" in final_response:
                final_response = final_response.split("```json")[1].split("```")[0].strip()
            return json.loads(final_response)
        except Exception:
            return {"has_disclosure": "yes" in final_response.lower(), "reason": final_response}

# Global instance
llm_service = LLMService()
