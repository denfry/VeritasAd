# backend/scripts/auto_annotate.py
import json
import subprocess
from pathlib import Path
import cv2
import pytesseract
import random
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === ПУТЬ К TESSERACT (ИЗМЕНИТЕ ПОД СВОЮ СИСТЕМУ) ===
pytesseract.pytesseract.tesseract_cmd = (
    r'C:\Users\denfry\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'  # Windows
    # '/usr/bin/tesseract'  # Linux
    # '/opt/homebrew/bin/tesseract'  # macOS (Apple Silicon)
)

ANNOTATED_DIR = Path("../../data/annotated/disclosure_dataset")
ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)

def transcribe(video_path: Path) -> str:
    """Whisper транскрипция (fallback при ошибке)"""
    try:
        txt_path = video_path.with_suffix(".txt")
        result = subprocess.run([
            "whisper", str(video_path),
            "--model", "tiny",
            "--language", "ru",
            "--output_format", "txt",
            "--output_dir", str(video_path.parent)
        ], capture_output=True, text=True, timeout=180)

        if result.returncode != 0:
            logger.warning(f"Whisper error: {result.stderr}")
            return "Транскрипция недоступна."

        return txt_path.read_text(encoding="utf-8").strip()
    except Exception as e:
        logger.error(f"Transcribe exception: {e}")
        return ""

def ocr_video(video_path: Path) -> str:
    """OCR с pytesseract: кадры каждые 3 сек, preprocessing"""
    try:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return ""

        texts = []
        frame_count = 0
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        frame_interval = max(1, int(fps * 3))  # Каждые 3 сек

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % frame_interval == 0:
                # Preprocessing
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Увеличение контраста
                gray = cv2.equalizeHist(gray)
                # Бинаризация
                _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                # OCR
                custom_config = r'--oem 3 --psm 6 -l rus+eng'
                text = pytesseract.image_to_string(binary, config=custom_config)
                if text.strip():
                    texts.append(text.strip())
            frame_count += 1
            if frame_count > 10 * fps:  # Макс 30 сек
                break
        cap.release()
        return " ".join(texts)
    except Exception as e:
        logger.error(f"OCR exception: {e}")
        return ""

def label_disclosure(text: str) -> tuple:
    keywords = [
        "реклама", "спонсор", "партнёр", "подарок", "#pr", "#реклама",
        "при поддержке", "сотрудничество", "благодарю за", "промо"
    ]
    has = any(kw.lower() in text.lower() for kw in keywords)
    reason = "Обнаружены ключевые слова рекламы" if has else "Нет признаков disclosure"
    return ("Да" if has else "Нет"), reason

def save_to_dataset(entry: dict, split: str = "train"):
    path = ANNOTATED_DIR / f"{split}.jsonl"
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    logger.info(f"Добавлено в {split}.jsonl")

def main(video_path: str):
    video_path_obj = Path(video_path)
    if not video_path_obj.exists():
        raise FileNotFoundError(f"Видео не найдено: {video_path}")

    logger.info(f"Обработка видео: {video_path_obj.name}")

    # 1. Транскрипция
    transcription = transcribe(video_path_obj)

    # 2. OCR
    ocr_text = ocr_video(video_path_obj)

    # 3. Объединение
    full_text = f"{transcription} {ocr_text}".strip()
    if not full_text:
        full_text = "Текст не распознан."

    # 4. Разметка
    label, reason = label_disclosure(full_text)

    # 5. Формат Alpaca
    alpaca_entry = {
        "instruction": "Определи, содержит ли текст disclosure рекламного характера (да/нет). Обоснуй.",
        "input": full_text[:1500],
        "output": f"{label}. Причина: {reason}."
    }

    # 6. Сохранение
    r = random.random()
    split = "train" if r < 0.8 else ("val" if r < 0.9 else "test")
    save_to_dataset(alpaca_entry, split)

    print(f"Добавлено в {split}.jsonl | Disclosure: {label}")
    print(f"Текст: {full_text[:200]}...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video-path", required=True, help="Путь к видео")
    args = parser.parse_args()
    main(args.video_path)
