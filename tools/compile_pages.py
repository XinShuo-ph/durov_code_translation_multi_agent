#!/usr/bin/env python3
"""
PDF Compilation Script for Durov Code Translation Project

This script compiles translated pages into PDF format using either:
1. LaTeX/XeLaTeX approach (primary)
2. Python reportlab/fpdf2 approach (fallback)

Usage:
    python compile_pages.py --page 13        # Compile single page
    python compile_pages.py --all            # Compile all available pages
    python compile_pages.py --method latex   # Force LaTeX method
    python compile_pages.py --method python  # Force Python method
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Configuration
WORKSPACE = Path(__file__).parent.parent
TRANSLATIONS_DIR = WORKSPACE / "translations"
OUTPUT_DIR = WORKSPACE / "output"
EXAMPLES_DIR = WORKSPACE / "examples"

# Color scheme (RGB)
COLORS = {
    'ru': (0, 0, 0),        # Black
    'en': (0, 82, 147),     # Blue
    'zh': (139, 69, 19),    # Brown
    'ja': (0, 100, 0),      # Green
}

LANG_LABELS = {
    'ru': '[RU]',
    'en': '[EN]',
    'zh': '[中]',
    'ja': '[日]',
}

def load_translation(page_num: int, stage: str = 'raw') -> dict:
    """Load translation JSON for a page."""
    json_path = TRANSLATIONS_DIR / stage / f'page_{page_num:03d}.json'
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_translation(page_num: int, data: dict, stage: str = 'raw'):
    """Save translation JSON for a page."""
    json_path = TRANSLATIONS_DIR / stage / f'page_{page_num:03d}.json'
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_latex_page(page_num: int, data: dict) -> str:
    """Generate LaTeX content for a single page."""
    latex_content = []
    
    # Page header
    latex_content.append(f"\\section*{{Page {page_num}}}")
    if data.get('chapter'):
        latex_content.append(f"\\subsection*{{Chapter {data['chapter']}}}")
    
    # Sentences
    for sentence in data.get('sentences', []):
        latex_content.append("\\paralleltext")
        latex_content.append(f"{{{sentence.get('ru', '')}}}")
        latex_content.append(f"{{{sentence.get('en', '')}}}")
        latex_content.append(f"{{{sentence.get('zh', '')}}}")
        latex_content.append(f"{{{sentence.get('ja', '')}}}")
        latex_content.append("")
    
    # Translator notes
    if data.get('translator_notes'):
        latex_content.append("\\subsection*{Translator Notes}")
        latex_content.append("\\begin{itemize}")
        for note in data['translator_notes']:
            latex_content.append(f"\\item {note}")
        latex_content.append("\\end{itemize}")
    
    return '\n'.join(latex_content)

def compile_with_latex(page_num: int, data: dict) -> bool:
    """Compile page using LaTeX/XeLaTeX."""
    # Read template
    template_path = EXAMPLES_DIR / 'format_demo.tex'
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Generate page content
    page_content = generate_latex_page(page_num, data)
    
    # Create standalone document
    # Find the document begin and replace content
    doc_start = template.find('\\begin{document}')
    doc_end = template.find('\\end{document}')
    
    preamble = template[:doc_start + len('\\begin{document}')]
    
    full_content = preamble + '\n' + page_content + '\n\\end{document}'
    
    # Write temporary file
    temp_dir = OUTPUT_DIR / 'temp'
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    tex_file = temp_dir / f'page_{page_num:03d}.tex'
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    # Compile
    try:
        result = subprocess.run(
            ['xelatex', '-interaction=nonstopmode', f'page_{page_num:03d}.tex'],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        pdf_file = temp_dir / f'page_{page_num:03d}.pdf'
        if pdf_file.exists():
            # Move to output directory
            final_pdf = OUTPUT_DIR / f'page_{page_num:03d}_translated.pdf'
            pdf_file.rename(final_pdf)
            print(f"PDF generated: {final_pdf}")
            return True
        else:
            print(f"LaTeX compilation failed for page {page_num}")
            print(result.stdout[-500:] if result.stdout else "No output")
            return False
    except subprocess.TimeoutExpired:
        print(f"LaTeX compilation timed out for page {page_num}")
        return False
    except Exception as e:
        print(f"LaTeX compilation error: {e}")
        return False

def compile_with_python(page_num: int, data: dict) -> bool:
    """Compile page using Python (fpdf2/reportlab)."""
    try:
        from fpdf import FPDF
        
        class MultilingualPDF(FPDF):
            def __init__(self):
                super().__init__()
                self.add_page()
                # Note: fpdf2 has limited CJK support
                # This is a fallback method
                
            def add_sentence_block(self, ru, en, zh, ja):
                self.set_font('Helvetica', size=10)
                self.set_text_color(*COLORS['ru'])
                self.multi_cell(0, 5, f"[RU] {ru}")
                self.set_text_color(*COLORS['en'])
                self.multi_cell(0, 5, f"[EN] {en}")
                self.set_text_color(*COLORS['zh'])
                self.multi_cell(0, 5, f"[ZH] {zh}")
                self.set_text_color(*COLORS['ja'])
                self.multi_cell(0, 5, f"[JA] {ja}")
                self.ln(5)
        
        pdf = MultilingualPDF()
        
        for sentence in data.get('sentences', []):
            pdf.add_sentence_block(
                sentence.get('ru', ''),
                sentence.get('en', ''),
                sentence.get('zh', ''),
                sentence.get('ja', '')
            )
        
        output_path = OUTPUT_DIR / f'page_{page_num:03d}_translated.pdf'
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        pdf.output(str(output_path))
        print(f"PDF generated (Python): {output_path}")
        return True
    except Exception as e:
        print(f"Python PDF generation error: {e}")
        return False

def compile_page(page_num: int, method: str = 'auto') -> bool:
    """Compile a single page."""
    # Load translation
    data = load_translation(page_num, 'final')
    if data is None:
        data = load_translation(page_num, 'reviewed')
    if data is None:
        data = load_translation(page_num, 'raw')
    if data is None:
        print(f"No translation found for page {page_num}")
        return False
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    if method == 'latex' or method == 'auto':
        if compile_with_latex(page_num, data):
            return True
        elif method == 'auto':
            print("LaTeX failed, trying Python fallback...")
            return compile_with_python(page_num, data)
        return False
    elif method == 'python':
        return compile_with_python(page_num, data)
    else:
        print(f"Unknown method: {method}")
        return False

def compile_all(method: str = 'auto'):
    """Compile all available pages."""
    success = 0
    failed = 0
    
    for stage in ['final', 'reviewed', 'raw']:
        stage_dir = TRANSLATIONS_DIR / stage
        if stage_dir.exists():
            for json_file in sorted(stage_dir.glob('page_*.json')):
                page_num = int(json_file.stem.split('_')[1])
                if compile_page(page_num, method):
                    success += 1
                else:
                    failed += 1
    
    print(f"\nCompilation complete: {success} succeeded, {failed} failed")

def main():
    parser = argparse.ArgumentParser(description='Compile translated pages to PDF')
    parser.add_argument('--page', type=int, help='Page number to compile')
    parser.add_argument('--all', action='store_true', help='Compile all available pages')
    parser.add_argument('--method', choices=['auto', 'latex', 'python'], 
                        default='auto', help='Compilation method')
    
    args = parser.parse_args()
    
    if args.page:
        compile_page(args.page, args.method)
    elif args.all:
        compile_all(args.method)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
