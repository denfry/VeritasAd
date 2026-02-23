from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from pathlib import Path
from datetime import datetime
from typing import Dict
import logging
from app.utils.ad_classification import classify_advertising

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate PDF reports for video analysis"""

    def __init__(self):
        """Initialize PDF report generator"""
        from app.core.config import settings
        self.output_dir = settings.reports_path
        self.output_dir.mkdir(exist_ok=True, parents=True)

        # Setup styles
        self.styles = getSampleStyleSheet()

        # Create custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#4F46E5'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#4F46E5'),
            spaceAfter=12,
            spaceBefore=12
        )

    def generate(self, analysis_data: Dict) -> Path:
        """
        Generate PDF report from analysis data

        Args:
            analysis_data: Analysis results dictionary

        Returns:
            Path to generated PDF file
        """
        try:
            # Create PDF filename
            video_id = analysis_data.get("video_id", "unknown")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"report_{video_id}_{timestamp}.pdf"
            pdf_path = self.output_dir / pdf_filename

            # Create PDF
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )

            # Build content
            story = []

            # Title
            story.append(Paragraph("VeritasAd", self.title_style))
            story.append(Paragraph("Advertising analysis report", self.styles["Heading2"]))
            story.append(Spacer(1, 0.5*cm))

            # Summary section
            story.append(Paragraph("Summary", self.heading_style))

            has_ad = analysis_data.get("has_advertising", False)
            confidence = analysis_data.get("confidence_score", 0.0)
            disclosure_markers = analysis_data.get("disclosure_text", []) or []
            detected_brands = analysis_data.get("detected_brands", []) or []
            detected_keywords = analysis_data.get("detected_keywords", []) or []

            classification = analysis_data.get("ad_classification")
            reason = analysis_data.get("ad_reason")
            if not classification or not reason:
                classification_data = classify_advertising(
                    has_advertising=has_ad,
                    disclosure_markers=disclosure_markers,
                    detected_brands=detected_brands,
                    detected_keywords=detected_keywords,
                )
                classification = classification or classification_data["classification"]
                reason = reason or classification_data["reason"]

            result_text = "Advertising detected" if has_ad else "No advertising detected"
            result_color = colors.red if has_ad else colors.green

            result_para = Paragraph(
                f'<font color="{result_color.hexval()}" size="14"><b>{result_text}</b></font>',
                self.styles['Normal']
            )
            story.append(result_para)
            story.append(Spacer(1, 0.3*cm))

            summary_data = [
                ["Parameter", "Value"],
                ["Confidence", f"{confidence:.1%}"],
                ["Ad classification", classification],
                ["Video ID", video_id],
                ["Analysis date", datetime.now().strftime("%Y-%m-%d %H:%M")],
                ["Video duration", f"{analysis_data.get('duration', 0):.1f} s"],
                ["Processing time", f"{analysis_data.get('processing_time', 0):.1f} s"],
            ]

            summary_table = Table(summary_data, colWidths=[8*cm, 8*cm])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            story.append(summary_table)
            story.append(Spacer(1, 0.5*cm))

            if reason:
                story.append(Paragraph("Classification reason", self.heading_style))
                story.append(Paragraph(reason, self.styles['Normal']))
                story.append(Spacer(1, 0.3*cm))

            # Detailed scores
            story.append(Paragraph("Detailed scores", self.heading_style))

            scores_data = [
                ["Metric", "Score"],
                ["Visual score (logos)", f"{analysis_data.get('visual_score', 0):.1%}"],
                ["Audio score (keywords)", f"{analysis_data.get('audio_score', 0):.1%}"],
                ["Text score", f"{analysis_data.get('text_score', 0):.1%}"],
                ["Disclosure score", f"{analysis_data.get('disclosure_score', 0):.1%}"],
            ]

            scores_table = Table(scores_data, colWidths=[10*cm, 6*cm])
            scores_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#06B6D4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            story.append(scores_table)
            story.append(Spacer(1, 0.5*cm))

            # Detected brands
            detected_brands = analysis_data.get("detected_brands", [])
            if detected_brands:
                story.append(Paragraph("Detected brands", self.heading_style))

                for brand in detected_brands:
                    brand_name = brand.get("name", "Unknown")
                    conf = brand.get("confidence", 0)
                    timestamps = brand.get("timestamps", [])

                    brand_text = f"<b>{brand_name}</b> (confidence: {conf:.1%})"
                    if timestamps:
                        times_str = ", ".join([f"{t:.1f}s" for t in timestamps[:5]])
                        brand_text += f"<br/>Timestamps: {times_str}"

                    story.append(Paragraph(brand_text, self.styles['Normal']))
                    story.append(Spacer(1, 0.2*cm))

            # Detected keywords
            keywords = detected_keywords
            if keywords:
                story.append(Paragraph("Detected keywords", self.heading_style))
                keywords_text = ", ".join(keywords[:20])  # Limit to 20
                story.append(Paragraph(keywords_text, self.styles['Normal']))
                story.append(Spacer(1, 0.3*cm))

            # Disclosure markers
            disclosure_text = disclosure_markers
            if disclosure_text:
                story.append(Paragraph("Disclosure markers", self.heading_style))
                disclosure_str = ", ".join(disclosure_text)
                story.append(Paragraph(disclosure_str, self.styles['Normal']))
                story.append(Spacer(1, 0.3*cm))

            # Transcript
            transcript = analysis_data.get("transcript", "")
            if transcript:
                story.append(PageBreak())
                story.append(Paragraph("Transcript", self.heading_style))

                # Truncate if too long
                if len(transcript) > 3000:
                    transcript = transcript[:3000] + "..."

                transcript_style = ParagraphStyle(
                    'Transcript',
                    parent=self.styles['Normal'],
                    fontSize=10,
                    alignment=TA_JUSTIFY
                )
                story.append(Paragraph(transcript, transcript_style))

            # Footer
            story.append(Spacer(1, 1*cm))
            footer_text = "<i>Generated by VeritasAd | veritasad.ai</i>"
            story.append(Paragraph(footer_text, self.styles['Normal']))

            # Build PDF
            doc.build(story)

            logger.info(f"PDF report generated: {pdf_path}")
            return pdf_path

        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            raise
