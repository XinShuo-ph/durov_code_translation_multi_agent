#!/usr/bin/env python3
"""
Multilingual PDF generator using reportlab.
Creates PDFs with Russian, English, Chinese, and Japanese text in parallel.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
import sys
from pathlib import Path

# Font configuration for multilingual support
# Using system fonts or downloadable free fonts
FONT_CONFIG = {
    'russian': {
        'regular': 'DejaVuSans',
        'bold': 'DejaVuSans-Bold',
        'color': colors.black
    },
    'english': {
        'regular': 'DejaVuSans',
        'bold': 'DejaVuSans-Bold', 
        'color': colors.blue
    },
    'chinese': {
        'regular': 'DejaVuSans',  # Will try to use CJK font if available
        'bold': 'DejaVuSans-Bold',
        'color': colors.red
    },
    'japanese': {
        'regular': 'DejaVuSans',
        'bold': 'DejaVuSans-Bold',
        'color': colors.darkgreen
    }
}

def register_fonts():
    """Register fonts for multilingual support."""
    try:
        # Try to register DejaVu fonts (widely available)
        pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
        return True
    except:
        # Fall back to reportlab default fonts
        print("Warning: DejaVu fonts not found, using defaults")
        return False

def create_language_style(lang_config, base_size=11):
    """Create paragraph style for a specific language."""
    return ParagraphStyle(
        name=f'Language_{lang_config["color"]}',
        fontName=lang_config['regular'],
        fontSize=base_size,
        textColor=lang_config['color'],
        leading=base_size * 1.3,
        alignment=TA_JUSTIFY,
        spaceBefore=3,
        spaceAfter=3
    )

def generate_multilingual_pdf(translation_json_path, output_pdf_path):
    """
    Generate a PDF with four-language parallel text.
    
    Args:
        translation_json_path: Path to JSON with translations
        output_pdf_path: Path for output PDF
    """
    # Load translation data
    with open(translation_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Setup PDF
    doc = SimpleDocTemplate(
        str(output_pdf_path),
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=0.75*inch
    )
    
    # Register fonts
    register_fonts()
    
    # Create styles
    styles = {
        'ru': create_language_style(FONT_CONFIG['russian'], 11),
        'en': create_language_style(FONT_CONFIG['english'], 10),
        'zh': create_language_style(FONT_CONFIG['chinese'], 10),
        'ja': create_language_style(FONT_CONFIG['japanese'], 10)
    }
    
    # Build document content
    story = []
    
    # Add page header
    title_style = ParagraphStyle(
        'Title',
        fontName='DejaVuSans-Bold',
        fontSize=14,
        textColor=colors.black,
        spaceAfter=20,
        alignment=TA_LEFT
    )
    
    page_num = data.get('page', '?')
    story.append(Paragraph(f"Page {page_num} - Durov Code (Multilingual Edition)", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Add sentences in four languages
    for sentence in data.get('sentences', []):
        # Russian (original)
        if 'ru' in sentence:
            story.append(Paragraph(sentence['ru'], styles['ru']))
        
        # English
        if 'en' in sentence:
            story.append(Paragraph(sentence['en'], styles['en']))
        
        # Chinese
        if 'zh' in sentence:
            story.append(Paragraph(sentence['zh'], styles['zh']))
        
        # Japanese
        if 'ja' in sentence:
            story.append(Paragraph(sentence['ja'], styles['ja']))
        
        # Space between sentence groups
        story.append(Spacer(1, 0.15*inch))
    
    # Add translator notes if present
    if 'translator_notes' in data and data['translator_notes']:
        story.append(Spacer(1, 0.3*inch))
        notes_style = ParagraphStyle(
            'Notes',
            fontName='DejaVuSans',
            fontSize=9,
            textColor=colors.grey,
            leading=11,
            leftIndent=20
        )
        story.append(Paragraph("<b>Translator Notes:</b>", notes_style))
        for note in data['translator_notes']:
            story.append(Paragraph(f"• {note}", notes_style))
    
    # Build PDF
    doc.build(story)
    print(f"PDF generated: {output_pdf_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 compile_pages.py <translation_json> <output_pdf>")
        sys.exit(1)
    
    translation_json = Path(sys.argv[1])
    output_pdf = Path(sys.argv[2])
    
    if not translation_json.exists():
        print(f"Error: Translation file not found: {translation_json}")
        sys.exit(1)
    
    generate_multilingual_pdf(translation_json, output_pdf)
