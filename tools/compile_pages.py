#!/usr/bin/env python3
"""
Compile translated page to multilingual PDF using LaTeX.
Takes JSON translation file and generates PDF with color-coded languages.
"""

import json
import subprocess
import sys
from pathlib import Path
import tempfile
import os

# LaTeX template header
LATEX_HEADER = r"""\documentclass[12pt,a4paper]{article}
\usepackage{xeCJK}
\usepackage{fontspec}
\usepackage{color}
\usepackage{geometry}
\usepackage{setspace}
\usepackage{fancyhdr}

% Set up fonts
\setmainfont{Noto Serif}
\setCJKmainfont{Noto Sans CJK SC}
\setCJKmonofont{Noto Sans Mono CJK SC}

% Define colors for each language
\definecolor{russiancolor}{RGB}{0,0,0}
\definecolor{englishcolor}{RGB}{0,68,153}
\definecolor{chinesecolor}{RGB}{204,0,0}
\definecolor{japanesecolor}{RGB}{0,128,0}

% Page geometry
\geometry{a4paper, left=2.5cm, right=2.5cm, top=3cm, bottom=3cm}

% Line spacing
\setstretch{1.3}

% Commands for each language
\newcommand{\ru}[1]{\textcolor{russiancolor}{#1}}
\newcommand{\en}[1]{\textcolor{englishcolor}{#1}}
\newcommand{\zh}[1]{\textcolor{chinesecolor}{#1}}
\newcommand{\ja}[1]{\textcolor{japanesecolor}{#1}}

% Header/footer
\pagestyle{fancy}
\fancyhf{}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0pt}

\begin{document}
"""

LATEX_FOOTER = r"""
\end{document}
"""

def escape_latex(text):
    """Escape special LaTeX characters"""
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text

def generate_latex(translation_data):
    """Generate LaTeX content from translation JSON"""
    
    latex_content = LATEX_HEADER
    
    # Add page header
    page_num = translation_data.get('page', '?')
    chapter = translation_data.get('chapter', '?')
    latex_content += f"\n\\section*{{Page {page_num} - Chapter {chapter}}}\n"
    latex_content += "\\thispagestyle{empty}\n\n"
    
    # Add sentences
    latex_content += "\\begin{spacing}{1.5}\n"
    latex_content += "\\setlength{\\parindent}{0pt}\n"
    latex_content += "\\setlength{\\parskip}{0.8em}\n\n"
    
    for sent in translation_data.get('sentences', []):
        ru_text = escape_latex(sent.get('ru', ''))
        en_text = escape_latex(sent.get('en', ''))
        zh_text = escape_latex(sent.get('zh', ''))
        ja_text = escape_latex(sent.get('ja', ''))
        
        latex_content += f"\\ru{{{ru_text}}}\n\n"
        latex_content += f"\\en{{{en_text}}}\n\n"
        latex_content += f"\\zh{{{zh_text}}}\n\n"
        latex_content += f"\\ja{{{ja_text}}}\n\n"
        latex_content += "\\bigskip\n\n"
    
    latex_content += "\\end{spacing}\n"
    
    # Add notes if present
    if translation_data.get('translator_notes'):
        latex_content += "\n\\vfill\n"
        latex_content += "\\begin{small}\n"
        latex_content += "\\textit{Translator notes:}\n"
        latex_content += "\\begin{itemize}\n"
        for note in translation_data['translator_notes']:
            latex_content += f"  \\item {escape_latex(note)}\n"
        latex_content += "\\end{itemize}\n"
        latex_content += "\\end{small}\n"
    
    latex_content += LATEX_FOOTER
    
    return latex_content

def compile_to_pdf(json_file, output_pdf=None):
    """Compile translation JSON to PDF"""
    
    json_path = Path(json_file)
    if not json_path.exists():
        print(f"Error: {json_file} not found")
        return False
    
    # Load translation data
    with open(json_path, 'r', encoding='utf-8') as f:
        translation_data = json.load(f)
    
    # Generate LaTeX
    latex_content = generate_latex(translation_data)
    
    # Create temporary directory for compilation
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_file = Path(tmpdir) / "output.tex"
        
        # Write LaTeX file
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        # Compile with XeLaTeX
        try:
            result = subprocess.run(
                ['xelatex', '-interaction=nonstopmode', 'output.tex'],
                cwd=tmpdir,
                capture_output=True,
                timeout=60
            )
            
            if result.returncode != 0:
                print(f"XeLaTeX compilation failed:")
                print(result.stdout.decode('utf-8', errors='ignore'))
                return False
            
            # Copy PDF to output location
            compiled_pdf = Path(tmpdir) / "output.pdf"
            if not compiled_pdf.exists():
                print("PDF was not generated")
                return False
            
            if output_pdf is None:
                page_num = translation_data.get('page', 'unknown')
                output_pdf = f"page_{page_num:03d}_translated.pdf"
            
            output_path = Path(output_pdf)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            import shutil
            shutil.copy(compiled_pdf, output_path)
            
            print(f"✓ Generated: {output_path}")
            print(f"  Size: {output_path.stat().st_size // 1024}KB")
            return True
            
        except subprocess.TimeoutExpired:
            print("XeLaTeX compilation timed out")
            return False
        except Exception as e:
            print(f"Error during compilation: {e}")
            return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python compile_pages.py <translation.json> [output.pdf]")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_pdf = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = compile_to_pdf(json_file, output_pdf)
    sys.exit(0 if success else 1)
