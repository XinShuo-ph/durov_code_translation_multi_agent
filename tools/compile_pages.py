from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
import sys
import os

# Register Fonts
# Adjust paths based on 'fc-list' output
try:
    font_path = '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'
    pdfmetrics.registerFont(TTFont('DroidSans', font_path))
    print("Fonts registered successfully.")
    
    # Use DroidSans for all
    font_sc = 'DroidSans'
    font_jp = 'DroidSans'
    font_std = 'DroidSans'
    
except Exception as e:
    print(f"Error registering fonts: {e}")
    # Fallback
    font_sc = 'Helvetica'
    font_jp = 'Helvetica'
    font_std = 'Helvetica'

def create_pdf(json_path, output_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []
    
    styles = getSampleStyleSheet()
    # Create custom styles for each language
    style_ru = ParagraphStyle('RU', parent=styles['Normal'], fontName=font_std, fontSize=10, leading=14)
    style_en = ParagraphStyle('EN', parent=styles['Normal'], fontName=font_std, fontSize=10, leading=14, textColor=colors.darkblue)
    style_zh = ParagraphStyle('ZH', parent=styles['Normal'], fontName=font_sc, fontSize=10, leading=14, textColor=colors.darkred)
    style_ja = ParagraphStyle('JA', parent=styles['Normal'], fontName=font_jp, fontSize=10, leading=14, textColor=colors.darkgreen)

    story.append(Paragraph(f"Page {data['page']} - Chapter {data['chapter']}", styles['Heading1']))
    story.append(Spacer(1, 12))

    for sentence in data['sentences']:
        # Create a table for each sentence? Or just paragraphs?
        # Instructions say "visually distinguished by color/font".
        # 4-row block per sentence seems good.
        
        # ID
        story.append(Paragraph(f"<b>Sentence {sentence['id']}</b>", styles['Normal']))
        
        # RU
        story.append(Paragraph(sentence['ru'], style_ru))
        
        # EN
        story.append(Paragraph(sentence['en'], style_en))
        
        # ZH
        story.append(Paragraph(sentence['zh'], style_zh))
        
        # JA
        story.append(Paragraph(sentence['ja'], style_ja))
        
        story.append(Spacer(1, 12))
        story.append(Paragraph("-" * 50, styles['Normal']))
        story.append(Spacer(1, 12))

    # Add Translator Notes if any
    if 'translator_notes' in data and data['translator_notes']:
        story.append(PageBreak())
        story.append(Paragraph("Translator Notes", styles['Heading2']))
        for note in data['translator_notes']:
            story.append(Paragraph(f"- {note}", styles['Normal']))

    doc.build(story)
    print(f"PDF created at {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compile_pages.py <json_file> <output_pdf>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    pdf_file = sys.argv[2]
    create_pdf(json_file, pdf_file)
