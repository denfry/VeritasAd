import torch
from transformers import CLIPProcessor, CLIPModel, AutoModelForCausalLM, AutoTokenizer
from faster_whisper import WhisperModel
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class ModelManager:
    _instance = None
    _models = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance

    def get_clip(self):
        if "clip" not in self._models:
            logger.info(f"Loading CLIP model: {settings.CLIP_MODEL}")
            model = CLIPModel.from_pretrained(settings.CLIP_MODEL)
            processor = CLIPProcessor.from_pretrained(settings.CLIP_MODEL)
            self._models["clip"] = (model, processor)
        return self._models["clip"]

    def get_whisper(self):
        if "whisper" not in self._models:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            logger.info(f"Loading Whisper model: {settings.WHISPER_MODEL} ({device}, {compute_type})")
            self._models["whisper"] = WhisperModel(
                settings.WHISPER_MODEL, device=device, compute_type=compute_type
            )
        return self._models["whisper"]

    def get_llm(self, adapter_path: str):
        try:
            from peft import PeftModel
        except ModuleNotFoundError:
            raise RuntimeError(
                "LLM adapter loading requires 'peft'. Install with: pip install peft"
            ) from None
        model_key = f"llm_{adapter_path}"
        if model_key not in self._models:
            base_model = settings.LOCAL_LLM_BASE_MODEL
            logger.info(f"Loading LLM with adapter: {adapter_path}")
            tokenizer = AutoTokenizer.from_pretrained(base_model)
            use_cuda = torch.cuda.is_available()
            model = AutoModelForCausalLM.from_pretrained(
                base_model,
                torch_dtype=torch.float16 if use_cuda else torch.float32,
                device_map="auto" if use_cuda else None,
            )
            if not use_cuda:
                model = model.to("cpu")
            model = PeftModel.from_pretrained(model, adapter_path)
            model.eval()
            self._models[model_key] = (model, tokenizer)
        return self._models[model_key]

# Global instance
model_manager = ModelManager()
