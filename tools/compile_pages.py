#!/usr/bin/env python3
"""
PDF Compilation Script for Durov Code Book Translation
Generates multilingual pages with Russian, English, Chinese, and Japanese.
Uses PyMuPDF (fitz) for better CJK support.
"""

import json
import os
from pathlib import Path
import fitz  # PyMuPDF

# Color scheme for languages (RGB values normalized 0-1)
COLORS = {
    'ru': (0, 0, 0),           # Black for Russian (original)
    'en': (0, 0.4, 0.8),       # Blue for English
    'zh': (0, 0.6, 0.2),       # Green for Chinese
    'ja': (0.6, 0, 0.6),       # Purple for Japanese
}

# Language labels
LABELS = {'ru': '[RU]', 'en': '[EN]', 'zh': '[中文]', 'ja': '[日本語]'}

# Font settings
FONTS = {
    'default': 'helv',  # Helvetica for Latin
    'cjk': 'china-s',   # Simplified Chinese (also works for Japanese)
}

def create_page_pdf(page_data, output_path):
    """Create a single page PDF with all translations."""
    doc = fitz.open()
    
    page_num = page_data.get('page', 0)
    chapter = page_data.get('chapter', '')
    sentences = page_data.get('sentences', [])
    notes = page_data.get('translator_notes', [])
    
    # Calculate content - may need multiple pages
    current_page = None
    y_pos = 0
    margin = 50
    line_height = 14
    page_width = 612  # Letter size
    page_height = 792
    usable_width = page_width - 2 * margin
    
    def new_page():
        nonlocal current_page, y_pos
        current_page = doc.new_page(width=page_width, height=page_height)
        y_pos = margin
        
        # Header
        current_page.insert_text(
            (margin, y_pos),
            f"Код Дурова / The Durov Code - Page {page_num}",
            fontname="helv",
            fontsize=10,
            color=(0.5, 0.5, 0.5)
        )
        y_pos += 25
        
        # Page title
        if chapter:
            current_page.insert_text(
                (margin, y_pos),
                chapter,
                fontname="helv",
                fontsize=14,
                color=(0, 0, 0)
            )
            y_pos += 30
    
    def check_space(needed=50):
        nonlocal y_pos
        if y_pos + needed > page_height - margin:
            new_page()
    
    new_page()
    
    for sentence in sentences:
        check_space(100)
        
        for lang in ['ru', 'en', 'zh', 'ja']:
            text = sentence.get(lang, '')
            if not text:
                continue
            
            color = COLORS.get(lang, (0, 0, 0))
            label = LABELS.get(lang, '')
            
            # Choose font based on language
            fontname = "helv"
            if lang in ['zh', 'ja']:
                fontname = "china-s"
            elif lang == 'ru':
                fontname = "helv"
            
            full_text = f"{label} {text}"
            
            # Split text into lines that fit
            try:
                # Use text box for auto-wrapping
                rect = fitz.Rect(margin, y_pos, page_width - margin, y_pos + 200)
                text_writer = fitz.TextWriter(current_page.rect)
                
                # Try to insert with wrapping
                font = fitz.Font(fontname)
                text_lines = []
                words = full_text.split()
                current_line = ""
                
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    width = font.text_length(test_line, fontsize=10)
                    if width < usable_width:
                        current_line = test_line
                    else:
                        if current_line:
                            text_lines.append(current_line)
                        current_line = word
                if current_line:
                    text_lines.append(current_line)
                
                for line in text_lines:
                    check_space(line_height + 5)
                    current_page.insert_text(
                        (margin, y_pos),
                        line,
                        fontname=fontname,
                        fontsize=10,
                        color=color
                    )
                    y_pos += line_height
                    
            except Exception as e:
                # Fallback: simple text insert
                current_page.insert_text(
                    (margin, y_pos),
                    full_text[:80] + "..." if len(full_text) > 80 else full_text,
                    fontname="helv",
                    fontsize=10,
                    color=color
                )
                y_pos += line_height
        
        # Separator line
        y_pos += 5
        current_page.draw_line(
            (margin, y_pos),
            (page_width - margin, y_pos),
            color=(0.8, 0.8, 0.8),
            width=0.5
        )
        y_pos += 10
    
    # Footer with notes
    if notes:
        check_space(50)
        y_pos += 10
        current_page.insert_text(
            (margin, y_pos),
            "Notes: " + "; ".join(notes),
            fontname="helv",
            fontsize=8,
            color=(0.4, 0.4, 0.4)
        )
    
    # Legend on last page
    y_pos = page_height - 30
    legend = "RU (black) | EN (blue) | 中文 (green) | 日本語 (purple)"
    current_page.insert_text(
        (margin, y_pos),
        legend,
        fontname="china-s",
        fontsize=8,
        color=(0.5, 0.5, 0.5)
    )
    
    doc.save(str(output_path))
    doc.close()
    
    return output_path


def compile_demo_page(page_num, sentences, output_dir="examples"):
    """Compile a demo page with provided sentences."""
    page_data = {
        "page": page_num,
        "chapter": "Глава 1 - Ботанический сад (Botanical Garden)" if page_num == 13 else f"Page {page_num}",
        "sentences": sentences,
        "translator_notes": ["Demo translation for format verification"]
    }
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = Path(output_dir) / f"page_{page_num:03d}_demo.pdf"
    
    create_page_pdf(page_data, output_path)
    
    print(f"Compiled demo: {output_path}")
    return output_path


def test_compilation():
    """Test the compilation with sample sentences from page 13."""
    sample_sentences = [
        {
            "id": 1,
            "ru": "Мальчик с томом Сервантеса выходит из подъезда.",
            "en": "A boy with a volume of Cervantes exits the building entrance.",
            "zh": "一个手捧塞万提斯著作的男孩走出公寓楼。",
            "ja": "セルバンテスの本を持った少年が建物の入り口を出る。"
        },
        {
            "id": 2,
            "ru": "Перед ним пустынные кварталы, поля и высоковольтные вышки.",
            "en": "Before him are desolate city blocks, fields, and high-voltage towers.",
            "zh": "他面前是荒凉的街区、田野和高压电塔。",
            "ja": "彼の前には荒涼としたブロック、野原、高圧送電塔が広がっている。"
        },
        {
            "id": 3,
            "ru": "Сканируя пространство на предмет гопников, мальчик с книгой идет к трассе.",
            "en": "Scanning the space for gopniks, the boy with the book walks toward the highway.",
            "zh": "边扫视周围是否有小混混,手拿书本的男孩朝公路走去。",
            "ja": "ゴプニクがいないか周囲を見回しながら、本を持った少年は道路に向かって歩く。"
        },
    ]
    
    return compile_demo_page(13, sample_sentences)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            result = test_compilation()
            print(f"Test completed: {result}")
        else:
            page_num = int(sys.argv[1])
            # Would need to load from JSON
            print(f"Would compile page {page_num}")
    else:
        print("Usage: python compile_pages.py [page_num | --test]")
        print("  page_num: Compile single page")
        print("  --test: Test with sample sentences")
