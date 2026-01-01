import sys
import json
import os
from reportlab.lib import pagesizes, colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def register_fonts():
    # Try to find a CJK font
    cjk_fonts = [
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
        "/usr/share/fonts/truetype/arphic/uming.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
    ]
    
    font_name = 'Helvetica' # Default
    
    for font_path in cjk_fonts:
        if os.path.exists(font_path):
            try:
                if font_path.endswith('.ttc'):
                    pdfmetrics.registerFont(TTFont('UniversalFont', font_path, subfontIndex=0))
                else:
                    pdfmetrics.registerFont(TTFont('UniversalFont', font_path))
                font_name = 'UniversalFont'
                print(f"Using font: {font_path}")
                break
            except Exception as e:
                print(f"Failed to load {font_path}: {e}")
                continue
                
    return font_name

def compile_page(json_path, output_pdf_path):
    if not os.path.exists(json_path):
        print(f"Error: JSON file {json_path} not found")
        sys.exit(1)

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    doc = SimpleDocTemplate(output_pdf_path, pagesize=pagesizes.A4)
    elements = []
    
    font_name = register_fonts()
    
    styles = getSampleStyleSheet()
    style_normal = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        leading=14
    )
    
    style_header = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=14,
        leading=18,
        spaceAfter=12
    )

    # Title/Header
    chapter_num = data.get('chapter', '?')
    page_num = data.get('page', '?')
    elements.append(Paragraph(f"Chapter {chapter_num} - Page {page_num}", style_header))
    elements.append(Spacer(1, 12))
    
    # Content Table
    # Rows: [Ru, En, Zh, Ja]
    table_data = [
        [
            Paragraph("<b>Russian</b>", style_normal),
            Paragraph("<b>English</b>", style_normal),
            Paragraph("<b>Chinese</b>", style_normal),
            Paragraph("<b>Japanese</b>", style_normal)
        ]
    ]
    
    for sentence in data.get('sentences', []):
        row = [
            Paragraph(sentence.get('ru', ''), style_normal),
            Paragraph(sentence.get('en', ''), style_normal),
            Paragraph(sentence.get('zh', ''), style_normal),
            Paragraph(sentence.get('ja', ''), style_normal)
        ]
        table_data.append(row)
        
    # Calculate column width
    # A4 width = 595.27, margins ~72 total? ReportLab default margin is 72 (1 inch)
    # So 450 printable width.
    col_w = 450 / 4
    
    t = Table(table_data, colWidths=[col_w]*4)
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ('FONTNAME', (0,0), (-1,-1), font_name)
    ]))
    
    elements.append(t)
    
    # Metadata
    elements.append(Spacer(1, 24))
    notes = data.get('translator_notes', [])
    if notes:
        elements.append(Paragraph("<b>Translator Notes:</b>", style_normal))
        for note in notes:
             elements.append(Paragraph(f"- {note}", style_normal))

    doc.build(elements)
    print(f"Generated PDF: {output_pdf_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 tools/compile_pages.py <input_json> <output_pdf>")
        sys.exit(1)
        
    compile_page(sys.argv[1], sys.argv[2])
