"""Prompt construction and few-shot examples for LLM claim extraction (VeritasAd 2.0, M2).

Builds the chat messages for the zero-shot and few-shot LLM extraction methods
(roadmap §6 "LLM zero-shot / few-shot extraction"). The LLM is asked to return a
strict JSON array of claim objects; :mod:`app.services.claim_extractor` parses and
validates the output, snapping types/risk onto the canonical enums.

The few-shot examples double as research artifacts; the prompt text is documented
under ``docs/research/prompts/master/``.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

# Canonical taxonomy / risk vocab injected into the prompt so the model stays on
# the schema (kept in sync with app.schemas.claims).
_CLAIM_TYPES = (
    "quantitative, comparative, superlative, temporal, financial, health_safety, "
    "legal_certification, partnership, availability, subjective, non_checkable"
)
_RISK_LEVELS = "low, medium, high, critical"
_MODALITIES = "ocr, asr, metadata, link, description"

SYSTEM_PROMPT = (
    "Ты — система извлечения проверяемых рекламных утверждений из мультимодального "
    "контента (VeritasAd 2.0). Тебе дают сигналы анализа рекламного видео/поста: "
    "аудиотранскрипт (ASR), текст с экрана (OCR), описание, бренды, disclosure-маркеры, "
    "CTA-фразы и ссылки.\n\n"
    "Задача: выделить отдельные ПРОВЕРЯЕМЫЕ рекламные утверждения и для каждого вернуть "
    "строго проверяемую (нормализованную) форму, тип и уровень риска.\n\n"
    "Проверяемое утверждение — это фактическое заявление, истинность которого в принципе "
    "можно установить по внешним источникам (числа, сравнения, обещания результата, "
    "сертификаты, сроки). Субъективные оценки («идеальный выбор», «вам понравится») "
    "помечай is_checkable=false и типом subjective или non_checkable.\n\n"
    f"claim_type ∈ {{{_CLAIM_TYPES}}}.\n"
    f"risk_level ∈ {{{_RISK_LEVELS}}}.\n"
    f"source_modality ∈ {{{_MODALITIES}}}.\n\n"
    "Нормализация: убери маркетинговые усилители и срочность, явно укажи субъект и "
    "измеримый параметр, сохрани количественные границы («до 70%» → верхняя граница).\n\n"
    "Верни ТОЛЬКО валидный JSON — массив объектов, без markdown и пояснений. "
    "Каждый объект: {\"raw_text\": str, \"normalized_claim\": str, \"claim_type\": str, "
    "\"risk_level\": str, \"is_checkable\": bool, \"source_modality\": str, "
    "\"brand\": str|null}. Если проверяемых утверждений нет — верни []."
)

# Few-shot demonstrations (input fragment → expected claim objects).
FEW_SHOT_EXAMPLES: List[Dict[str, Any]] = [
    {
        "input": "Скидка до 70% только сегодня по промокоду VERITAS",
        "output": [
            {
                "raw_text": "Скидка до 70% только сегодня",
                "normalized_claim": "Скидка на товар достигает 70%",
                "claim_type": "quantitative",
                "risk_level": "medium",
                "is_checkable": True,
                "source_modality": "ocr",
                "brand": None,
            }
        ],
    },
    {
        "input": "Наш банк начисляет 16% годовых на остаток — выгоднее, чем у конкурентов",
        "output": [
            {
                "raw_text": "начисляет 16% годовых на остаток",
                "normalized_claim": "Годовая ставка на остаток по счёту составляет 16%",
                "claim_type": "financial",
                "risk_level": "high",
                "is_checkable": True,
                "source_modality": "asr",
                "brand": None,
            },
            {
                "raw_text": "выгоднее, чем у конкурентов",
                "normalized_claim": "Условия по счёту выгоднее, чем у конкурирующих банков",
                "claim_type": "comparative",
                "risk_level": "medium",
                "is_checkable": True,
                "source_modality": "asr",
                "brand": None,
            },
        ],
    },
    {
        "input": "Этот крем идеально подойдёт каждому, вам точно понравится!",
        "output": [
            {
                "raw_text": "вам точно понравится",
                "normalized_claim": "",
                "claim_type": "non_checkable",
                "risk_level": "low",
                "is_checkable": False,
                "source_modality": "asr",
                "brand": None,
            }
        ],
    },
    {
        "input": "Официальный партнёр чемпионата, сертифицировано по ГОСТ, доставка за 24 часа",
        "output": [
            {
                "raw_text": "Официальный партнёр чемпионата",
                "normalized_claim": "Компания является официальным партнёром чемпионата",
                "claim_type": "partnership",
                "risk_level": "medium",
                "is_checkable": True,
                "source_modality": "ocr",
                "brand": None,
            },
            {
                "raw_text": "сертифицировано по ГОСТ",
                "normalized_claim": "Товар сертифицирован по стандарту ГОСТ",
                "claim_type": "legal_certification",
                "risk_level": "high",
                "is_checkable": True,
                "source_modality": "ocr",
                "brand": None,
            },
            {
                "raw_text": "доставка за 24 часа",
                "normalized_claim": "Срок доставки товара составляет 24 часа",
                "claim_type": "temporal",
                "risk_level": "medium",
                "is_checkable": True,
                "source_modality": "asr",
                "brand": None,
            },
        ],
    },
]


def _format_signals(signals: Dict[str, Any]) -> str:
    """Render the multimodal signals block for the user message."""
    lines: List[str] = []
    transcript = (signals.get("transcript") or "").strip()
    ocr_text = (signals.get("ocr_text") or "").strip()
    description = (signals.get("description") or "").strip()
    brands = signals.get("detected_brands") or []
    disclosure = signals.get("disclosure_markers") or []
    cta = signals.get("cta_matches") or []
    urls = signals.get("commercial_urls") or []

    if transcript:
        lines.append(f"ASR (речь):\n{transcript}")
    if ocr_text:
        lines.append(f"OCR (текст на экране):\n{ocr_text}")
    if description:
        lines.append(f"Описание/метаданные:\n{description}")
    if brands:
        names = ", ".join(
            str(b.get("name")) for b in brands if isinstance(b, dict) and b.get("name")
        )
        if names:
            lines.append(f"Бренды: {names}")
    if disclosure:
        lines.append(f"Disclosure-маркеры: {', '.join(map(str, disclosure))}")
    if cta:
        lines.append(f"CTA-фразы: {', '.join(map(str, cta))}")
    if urls:
        lines.append(f"Ссылки: {', '.join(map(str, urls))}")

    return "\n\n".join(lines) if lines else "(сигналы отсутствуют)"


def build_messages(signals: Dict[str, Any], *, few_shot: bool) -> List[Dict[str, str]]:
    """Build the chat messages for LLM claim extraction.

    Args:
        signals: multimodal signal dict (transcript, ocr_text, description,
            detected_brands, disclosure_markers, cta_matches, commercial_urls).
        few_shot: when True, prepend the demonstration examples.

    Returns:
        A list of ``{role, content}`` messages for ``LLMService.generate_response``.
    """
    messages: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    if few_shot:
        for example in FEW_SHOT_EXAMPLES:
            messages.append(
                {"role": "user", "content": f"Сигналы:\n\n{example['input']}"}
            )
            messages.append(
                {
                    "role": "assistant",
                    "content": json.dumps(example["output"], ensure_ascii=False),
                }
            )

    messages.append(
        {"role": "user", "content": f"Сигналы:\n\n{_format_signals(signals)}"}
    )
    return messages
