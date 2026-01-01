#!/usr/bin/env python3
"""
Page Compilation Script for Durov Code Translation
Converts JSON translations to LaTeX and compiles to PDF
"""

import json
import subprocess
import sys
import os
from pathlib import Path

LATEX_TEMPLATE = r"""% Durov Code Translation - Page {page_num}
\documentclass[12pt,a4paper]{{article}}

\usepackage{{fontspec}}
\usepackage{{xeCJK}}
\usepackage[russian,english]{{babel}}
\usepackage{{xcolor}}
\usepackage[margin=2.5cm]{{geometry}}
\usepackage{{parskip}}

\setmainfont{{DejaVu Serif}}
\setCJKmainfont{{Noto Sans CJK SC}}
\newCJKfontfamily\cjkjapanese{{Noto Sans CJK JP}}

\definecolor{{russiancolor}}{{RGB}}{{0,0,0}}
\definecolor{{englishcolor}}{{RGB}}{{0,51,153}}
\definecolor{{chinesecolor}}{{RGB}}{{204,0,0}}
\definecolor{{japanesecolor}}{{RGB}}{{0,102,51}}

\newcommand{{\ru}}[1]{{\textcolor{{russiancolor}}{{#1}}}}
\newcommand{{\en}}[1]{{\textcolor{{englishcolor}}{{#1}}}}
\newcommand{{\zh}}[1]{{\textcolor{{chinesecolor}}{{#1}}}}
\newcommand{{\ja}}[1]{{\textcolor{{japanesecolor}}{{\cjkjapanese #1}}}}

\newenvironment{{mlsentence}}
  {{\begin{{quote}}\small}}
  {{\end{{quote}}}}

\begin{{document}}

\section*{{{title}}}

\hrule
\vspace{{0.3cm}}

\textit{{Page {page_num}}}

\vspace{{0.5cm}}

{sentences}

\vspace{{0.5cm}}
\hrule

\end{{document}}
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
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def json_to_latex(json_path):
    """Convert translation JSON to LaTeX source"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    page_num = data['page']
    title = data.get('title', f'Page {page_num}')
    
    sentences_latex = []
    for sentence in data['sentences']:
        ru = sentence['ru']
        en = sentence['en']
        zh = sentence['zh']
        ja = sentence['ja']
        
        sent_block = r"""\begin{mlsentence}
\ru{%s}

\en{%s}

\zh{%s}

\ja{%s}
\end{mlsentence}
""" % (ru, en, zh, ja)
        sentences_latex.append(sent_block)
    
    latex_content = LATEX_TEMPLATE.format(
        page_num=page_num,
        title=title,
        sentences='\n'.join(sentences_latex)
    )
    
    return latex_content

def compile_latex(tex_content, output_dir, page_num):
    """Compile LaTeX to PDF using xelatex"""
    tex_file = output_dir / f'page_{page_num:03d}.tex'
    pdf_file = output_dir / f'page_{page_num:03d}.pdf'
    
    # Write LaTeX file
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(tex_content)
    
    # Compile with xelatex
    try:
        result = subprocess.run(
            ['xelatex', '-interaction=nonstopmode', tex_file.name],
            cwd=output_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"LaTeX compilation failed for page {page_num}")
            print(result.stdout[-500:])
            return False
        
        if pdf_file.exists():
            print(f"✓ Page {page_num} compiled successfully: {pdf_file}")
            return True
        else:
            print(f"✗ PDF not generated for page {page_num}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ Compilation timeout for page {page_num}")
        return False
    except Exception as e:
        print(f"✗ Error compiling page {page_num}: {e}")
        return False

def process_page(json_path, output_dir):
    """Complete workflow for one page"""
    json_path = Path(json_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    page_num = data['page']
    
    # Generate LaTeX
    latex_content = json_to_latex(json_path)
    
    # Compile PDF
    success = compile_latex(latex_content, output_dir, page_num)
    
    return success

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 compile_pages.py <json_file> [output_dir]")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'output'
    
    success = process_page(json_file, output_dir)
    sys.exit(0 if success else 1)
