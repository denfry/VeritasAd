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

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate PDF reports for video analysis"""

    def __init__(self):
        """Initialize PDF report generator"""
        self.output_dir = Path("../data/reports")
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
            story.append(Paragraph("BGQB 0=0;870 @5:;0<=>9 8=B53@0F88", self.styles['Heading2']))
            story.append(Spacer(1, 0.5*cm))

            # Summary section
            story.append(Paragraph(" 57C;LB0BK 0=0;870", self.heading_style))

            has_ad = analysis_data.get("has_advertising", False)
            confidence = analysis_data.get("confidence_score", 0.0)

            result_text = " #  " if has_ad else " 5:;0<0 =5 >1=0@C65=0"
            result_color = colors.red if has_ad else colors.green

            result_para = Paragraph(
                f'<font color="{result_color.hexval()}" size="14"><b>{result_text}</b></font>',
                self.styles['Normal']
            )
            story.append(result_para)
            story.append(Spacer(1, 0.3*cm))

            summary_data = [
                ["0@0<5B@", "=0G5=85"],
                ["#25@5==>ABL", f"{confidence:.1%}"],
                ["845> ID", video_id],
                ["0B0 0=0;870", datetime.now().strftime("%d.%m.%Y %H:%M")],
                [";8B5;L=>ABL 2845>", f"{analysis_data.get('duration', 0):.1f} A5:"],
                ["@5<O >1@01>B:8", f"{analysis_data.get('processing_time', 0):.1f} A5:"],
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

            # Detailed scores
            story.append(Paragraph("5B0;L=K5 >F5=:8", self.heading_style))

            scores_data = [
                ["0B53>@8O", "F5=:0"],
                ["87C0;L=K9 0=0;87 (;>3>B8?K)", f"{analysis_data.get('visual_score', 0):.1%}"],
                ["C48> 0=0;87 (:;NG52K5 A;>20)", f"{analysis_data.get('audio_score', 0):.1%}"],
                [""5:AB>2K9 0=0;87", f"{analysis_data.get('text_score', 0):.1%}"],
                ["0@:5@K disclosure", f"{analysis_data.get('disclosure_score', 0):.1%}"],
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
                story.append(Paragraph("1=0@C65==K5 1@5=4K", self.heading_style))

                for brand in detected_brands:
                    brand_name = brand.get("name", "Unknown")
                    conf = brand.get("confidence", 0)
                    timestamps = brand.get("timestamps", [])

                    brand_text = f"<b>{brand_name}</b> (C25@5==>ABL: {conf:.1%})"
                    if timestamps:
                        times_str = ", ".join([f"{t:.1f}A" for t in timestamps[:5]])
                        brand_text += f"<br/>@5<5==K5 <5B:8: {times_str}"

                    story.append(Paragraph(brand_text, self.styles['Normal']))
                    story.append(Spacer(1, 0.2*cm))

            # Detected keywords
            keywords = analysis_data.get("detected_keywords", [])
            if keywords:
                story.append(Paragraph("1=0@C65==K5 :;NG52K5 A;>20", self.heading_style))
                keywords_text = ", ".join(keywords[:20])  # Limit to 20
                story.append(Paragraph(keywords_text, self.styles['Normal']))
                story.append(Spacer(1, 0.3*cm))

            # Disclosure markers
            disclosure_text = analysis_data.get("disclosure_text", [])
            if disclosure_text:
                story.append(Paragraph("0@:5@K @0A:@KB8O @5:;0<K", self.heading_style))
                disclosure_str = ", ".join(disclosure_text)
                story.append(Paragraph(disclosure_str, self.styles['Normal']))
                story.append(Spacer(1, 0.3*cm))

            # Transcript
            transcript = analysis_data.get("transcript", "")
            if transcript:
                story.append(PageBreak())
                story.append(Paragraph(""@0=A:@8?F8O 0C48>", self.heading_style))

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
            footer_text = "<i>!35=5@8@>20=> A8AB5<>9 VeritasAd | veritasad.ai</i>"
            story.append(Paragraph(footer_text, self.styles['Normal']))

            # Build PDF
            doc.build(story)

            logger.info(f"PDF report generated: {pdf_path}")
            return pdf_path

        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            raise
