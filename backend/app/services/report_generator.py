import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging
from app.utils.ad_classification import classify_advertising

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Font setup — reportlab's built-in Helvetica has no Cyrillic glyphs, so Russian
# text renders as tofu boxes. Register a Unicode TTF (Cyrillic-capable) once at
# import, trying common locations across Windows / Linux / macOS.
# ---------------------------------------------------------------------------
_FONT_REGULAR_CANDIDATES = [
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]
_FONT_BOLD_CANDIDATES = [
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/segoeuib.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]


def _register_fonts() -> tuple[str, str]:
    """Register a Cyrillic-capable font family; fall back to Helvetica."""
    regular = next((p for p in _FONT_REGULAR_CANDIDATES if os.path.exists(p)), None)
    if not regular:
        logger.warning("no_unicode_font_found_cyrillic_may_render_incorrectly")
        return ("Helvetica", "Helvetica-Bold")

    bold = next((p for p in _FONT_BOLD_CANDIDATES if os.path.exists(p)), None)
    try:
        pdfmetrics.registerFont(TTFont("VeritasUI", regular))
        bold_name = "VeritasUI"
        if bold:
            pdfmetrics.registerFont(TTFont("VeritasUI-Bold", bold))
            bold_name = "VeritasUI-Bold"
        # Map <b>…</b> inline markup to the bold face.
        pdfmetrics.registerFontFamily(
            "VeritasUI",
            normal="VeritasUI",
            bold=bold_name,
            italic="VeritasUI",
            boldItalic=bold_name,
        )
        return ("VeritasUI", bold_name)
    except Exception as exc:  # pragma: no cover - font loading edge cases
        logger.warning("font_registration_failed error=%s", exc)
        return ("Helvetica", "Helvetica-Bold")


FONT, FONT_BOLD = _register_fonts()

# Palette
_INDIGO = colors.HexColor("#4F46E5")
_CYAN = colors.HexColor("#0891B2")
_RED = colors.HexColor("#DC2626")
_GREEN = colors.HexColor("#059669")
_SLATE = colors.HexColor("#475569")
_LIGHT = colors.HexColor("#F1F5F9")
_BORDER = colors.HexColor("#E2E8F0")


def _esc(value) -> str:
    """Escape text for reportlab paragraph markup."""
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


class ReportGenerator:
    """Generate clean, Cyrillic-aware PDF reports for video analysis."""

    def __init__(self):
        from app.core.config import settings

        self.output_dir = settings.reports_path
        self.output_dir.mkdir(exist_ok=True, parents=True)

        base = getSampleStyleSheet()
        self.body = ParagraphStyle(
            "Body", parent=base["Normal"], fontName=FONT, fontSize=10,
            leading=15, textColor=colors.HexColor("#1E293B"),
        )
        self.title_style = ParagraphStyle(
            "Title", parent=base["Heading1"], fontName=FONT_BOLD, fontSize=26,
            textColor=_INDIGO, spaceAfter=2, alignment=TA_LEFT,
        )
        self.subtitle_style = ParagraphStyle(
            "Subtitle", parent=base["Normal"], fontName=FONT, fontSize=11,
            textColor=_SLATE, spaceAfter=18,
        )
        self.heading_style = ParagraphStyle(
            "Heading", parent=base["Heading2"], fontName=FONT_BOLD, fontSize=14,
            textColor=_INDIGO, spaceAfter=8, spaceBefore=18,
        )
        self.muted = ParagraphStyle(
            "Muted", parent=self.body, fontSize=9, textColor=_SLATE,
        )

    # -- helpers ----------------------------------------------------------
    def _kv_table(self, rows: List[List[str]], header_color, col_widths):
        data = [[Paragraph(f"<b>{_esc(c)}</b>", ParagraphStyle(
            "th", parent=self.body, fontName=FONT_BOLD, textColor=colors.white))
            for c in rows[0]]]
        for r in rows[1:]:
            data.append([Paragraph(_esc(c), self.body) for c in r])
        t = Table(data, colWidths=col_widths, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), header_color),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _LIGHT]),
            ("GRID", (0, 0), (-1, -1), 0.5, _BORDER),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ]))
        return t

    def _bar(self, label: str, value: float) -> Table:
        """A labelled score bar rendered as a 2-cell table."""
        pct = max(0.0, min(1.0, float(value or 0.0)))
        filled = max(0.01, pct)
        color = _RED if pct < 0.3 else (colors.HexColor("#D97706") if pct < 0.7 else _GREEN)
        bar = Table(
            [[""]], colWidths=[10 * cm * filled], rowHeights=[0.32 * cm]
        )
        bar.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), color),
            ("LINEBEFORE", (0, 0), (0, 0), 0, color),
        ]))
        track = Table([[bar]], colWidths=[10 * cm], rowHeights=[0.32 * cm])
        track.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), _BORDER),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("VALIGN", (0, 0), (0, 0), "MIDDLE"),
        ]))
        row = Table(
            [[Paragraph(_esc(label), self.body), track,
              Paragraph(f"<b>{pct:.0%}</b>", self.body)]],
            colWidths=[5 * cm, 10 * cm, 1.6 * cm],
        )
        row.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
        ]))
        return row

    # -- main -------------------------------------------------------------
    def generate(self, analysis_data: Dict) -> Path:
        try:
            video_id = analysis_data.get("video_id", "unknown")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = self.output_dir / f"report_{video_id}_{timestamp}.pdf"

            doc = SimpleDocTemplate(
                str(pdf_path), pagesize=A4,
                rightMargin=1.8 * cm, leftMargin=1.8 * cm,
                topMargin=1.6 * cm, bottomMargin=1.6 * cm,
                title=f"VeritasAd — отчёт {video_id}",
            )
            story = []

            has_ad = bool(analysis_data.get("has_advertising", False))
            confidence = float(analysis_data.get("confidence_score", 0.0) or 0.0)
            disclosure_markers = analysis_data.get("disclosure_text", []) or \
                analysis_data.get("disclosure_markers", []) or []
            detected_brands = analysis_data.get("detected_brands", []) or []
            detected_keywords = analysis_data.get("detected_keywords", []) or []
            commercial_urls = analysis_data.get("commercial_urls", []) or []
            promo_codes = analysis_data.get("promo_codes", []) or []
            cta_matches = analysis_data.get("cta_matches", []) or []
            erids = analysis_data.get("erids", []) or []

            classification = analysis_data.get("ad_classification")
            reason = analysis_data.get("ad_reason")
            if not classification or not reason:
                cd = classify_advertising(
                    has_advertising=has_ad,
                    disclosure_markers=disclosure_markers,
                    detected_brands=detected_brands,
                    detected_keywords=detected_keywords,
                )
                classification = classification or cd["classification"]
                reason = reason or cd["reason"]

            # --- Header ---
            story.append(Paragraph("VeritasAd", self.title_style))
            story.append(Paragraph("Отчёт об анализе рекламы", self.subtitle_style))

            # --- Verdict banner ---
            verdict_text = "Обнаружена реклама" if has_ad else "Реклама не обнаружена"
            verdict_color = _RED if has_ad else _GREEN
            banner = Table(
                [[Paragraph(
                    f'<font color="white" size="15"><b>{verdict_text}</b></font><br/>'
                    f'<font color="white" size="9">Уверенность: {confidence:.0%} · '
                    f'Классификация: {_esc(self._ru_class(classification))}</font>',
                    self.body)]],
                colWidths=[17.4 * cm],
            )
            banner.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), verdict_color),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
            ]))
            story.append(banner)
            story.append(Spacer(1, 0.5 * cm))

            # --- Summary ---
            story.append(Paragraph("Сводка", self.heading_style))
            dur = float(analysis_data.get("duration", 0) or 0)
            summary_rows = [
                ["Параметр", "Значение"],
                ["Вердикт", verdict_text],
                ["Уверенность", f"{confidence:.0%}"],
                ["Классификация", self._ru_class(classification)],
                ["ID видео", str(video_id)],
                ["Длительность", self._fmt_duration(dur)],
                ["Дата анализа", datetime.now().strftime("%d.%m.%Y %H:%M")],
            ]
            story.append(self._kv_table(summary_rows, _INDIGO, [5.4 * cm, 12 * cm]))

            if reason:
                story.append(Paragraph("Причина классификации", self.heading_style))
                story.append(Paragraph(_esc(reason), self.body))

            # --- Scores as bars ---
            story.append(Paragraph("Оценки по сигналам", self.heading_style))
            story.append(self._bar("Видео (логотипы)", analysis_data.get("visual_score", 0)))
            story.append(self._bar("Аудио (ключевые слова)", analysis_data.get("audio_score", 0)))
            story.append(self._bar("Текст", analysis_data.get("text_score", 0)))
            story.append(self._bar("Маркировка", analysis_data.get("disclosure_score", 0)))
            story.append(self._bar("Коммерческие ссылки", analysis_data.get("link_score", 0)))

            # --- Commercial signals (the hard evidence) ---
            if commercial_urls or promo_codes or cta_matches or erids:
                story.append(Paragraph("Коммерческие сигналы", self.heading_style))
                if commercial_urls:
                    story.append(Paragraph(
                        f"<b>Ссылки ({len(commercial_urls)}):</b> "
                        + ", ".join(_esc(u) for u in commercial_urls[:15]), self.body))
                if promo_codes:
                    story.append(Paragraph(
                        "<b>Промокоды:</b> " + ", ".join(_esc(p) for p in promo_codes[:15]),
                        self.body))
                if cta_matches:
                    story.append(Paragraph(
                        "<b>Призывы к действию (CTA):</b> "
                        + ", ".join(_esc(c) for c in cta_matches[:15]), self.body))
                if erids:
                    story.append(Paragraph(
                        "<b>ЕРИД:</b> " + ", ".join(_esc(e) for e in erids[:15]), self.body))

            # --- Brands ---
            if detected_brands:
                story.append(Paragraph(
                    f"Обнаруженные бренды ({len(detected_brands)})", self.heading_style))
                brand_rows = [["Бренд", "Уверенность", "Появления"]]
                for b in detected_brands[:25]:
                    ts = b.get("timestamps", []) or []
                    appear = ", ".join(f"{float(t):.0f}с" for t in ts[:6]) if ts else "—"
                    brand_rows.append([
                        b.get("name", "—"),
                        f"{float(b.get('confidence', 0) or 0):.0%}",
                        appear,
                    ])
                story.append(self._kv_table(brand_rows, _CYAN, [7 * cm, 3.4 * cm, 7 * cm]))

            # --- Keywords ---
            if detected_keywords:
                story.append(Paragraph("Ключевые слова", self.heading_style))
                story.append(Paragraph(
                    ", ".join(_esc(k) for k in detected_keywords[:25]), self.body))

            # --- Disclosure markers ---
            if disclosure_markers:
                story.append(Paragraph("Маркеры маркировки", self.heading_style))
                story.append(Paragraph(
                    ", ".join(_esc(m) for m in disclosure_markers[:25]), self.body))

            # --- Transcript ---
            transcript = analysis_data.get("transcript", "") or ""
            if transcript.strip():
                story.append(PageBreak())
                story.append(Paragraph("Транскрипт", self.heading_style))
                if len(transcript) > 4000:
                    transcript = transcript[:4000] + "…"
                ts_style = ParagraphStyle(
                    "Transcript", parent=self.body, fontSize=9, leading=14,
                    alignment=TA_JUSTIFY, textColor=_SLATE,
                )
                story.append(Paragraph(_esc(transcript), ts_style))

            # --- Footer ---
            story.append(Spacer(1, 0.8 * cm))
            story.append(Paragraph(
                "<font size='8'>Сформировано VeritasAd · veritasad.ai · "
                f"{datetime.now().strftime('%d.%m.%Y %H:%M')}</font>", self.muted))

            doc.build(story)
            logger.info(f"PDF report generated: {pdf_path}")
            return pdf_path

        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            raise

    # -- formatting helpers ----------------------------------------------
    @staticmethod
    def _ru_class(classification) -> str:
        mapping = {
            "official": "Официальная реклама",
            "unofficial": "Неофициальная реклама",
            "no_ad": "Реклама не обнаружена",
            "none": "Реклама не обнаружена",
            "suspected": "Предполагаемая реклама",
        }
        if not classification:
            return "—"
        return mapping.get(str(classification).lower(), str(classification))

    @staticmethod
    def _fmt_duration(seconds: float) -> str:
        seconds = int(seconds or 0)
        if seconds <= 0:
            return "—"
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        if h:
            return f"{h} ч {m} мин {s} с"
        if m:
            return f"{m} мин {s} с"
        return f"{s} с"
