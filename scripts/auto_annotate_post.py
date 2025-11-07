# scripts/auto_annotate_post.py
import json
import argparse
from pathlib import Path
import re

DISCLOSURE_KEYWORDS = [
    "реклама", "спонсор", "партнёр", "сотрудничество",
    "ad", "sponsored", "partner", "промо", "продаж"
]

def has_disclosure(text: str) -> bool:
    text = text.lower()
    return any(kw in text for kw in DISCLOSURE_KEYWORDS)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-json", required=True)
    parser.add_argument("--platform", required=True)
    args = parser.parse_args()

    with open(args.post_json, "r", encoding="utf-8") as f:
        post = json.load(f)

    # Собираем текст
    text_parts = [
        post.get("title", ""),
        post.get("description", ""),
        " ".join([c.get("text", "") for c in post.get("comments", [])[:50]])  # первые 50 комментов
    ]
    full_text = " ".join(filter(None, text_parts))

    # Аннотация
    label = 1 if has_disclosure(full_text) else 0
    confidence = 0.95 if label else 0.8  # заглушка, потом ML

    # Сохраняем в датасет
    annotated = {
        "post_id": Path(args.post_json).stem,
        "platform": args.platform,
        "url": post.get("webpage_url"),
        "title": post.get("title"),
        "text": full_text[:2000],
        "label": label,
        "confidence": confidence,
        "annotated_at": __import__("datetime").datetime.now().isoformat()
    }

    dataset_path = Path("../data/annotated/disclosure_dataset/posts.jsonl")
    dataset_path.parent.mkdir(exist_ok=True, parents=True)

    with open(dataset_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(annotated, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
