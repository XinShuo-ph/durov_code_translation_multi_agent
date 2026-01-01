#!/usr/bin/env python3
"""
Generate multilingual PDF pages using XeLaTeX.
Supports Russian, English, Chinese, and Japanese with proper fonts.
"""

import json
import subprocess
import os
import sys
from pathlib import Path

LATEX_TEMPLATE = r'''
\documentclass[12pt,a4paper]{article}
\usepackage{fontspec}
\usepackage{xeCJK}
\usepackage{xcolor}
\usepackage{geometry}
\usepackage{parskip}

\geometry{margin=2cm}

% Font configuration
\setmainfont{DejaVu Serif}
\setsansfont{DejaVu Sans}
\setCJKmainfont{Noto Sans CJK SC}
\setCJKsansfont{Noto Sans CJK SC}

% CJK fallback for Japanese
\newCJKfontfamily\japanesefont{Noto Sans CJK JP}

% Color definitions
\definecolor{rucolor}{RGB}{0, 0, 0}       % Black for Russian
\definecolor{encolor}{RGB}{0, 0, 200}     % Blue for English  
\definecolor{zhcolor}{RGB}{180, 0, 0}     % Red for Chinese
\definecolor{jacolor}{RGB}{0, 128, 0}     % Green for Japanese

% Language commands
\newcommand{\rutext}[1]{\textcolor{rucolor}{#1}}
\newcommand{\entext}[1]{\textcolor{encolor}{#1}}
\newcommand{\zhtext}[1]{\textcolor{zhcolor}{#1}}
\newcommand{\jatext}[1]{{\japanesefont\textcolor{jacolor}{#1}}}

\begin{document}

\begin{center}
\LARGE\textbf{%%PAGE_TITLE%%}
\end{center}

\vspace{1em}

%%CONTENT%%

\end{document}
'''

def escape_latex(text):
    """Escape special LaTeX characters."""
    replacements = {
        '\\': r'\textbackslash{}',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def generate_content(sentences):
    """Generate LaTeX content from sentences."""
    content_lines = []
    
    for i, sent in enumerate(sentences, 1):
        ru = escape_latex(sent.get('ru', ''))
        en = escape_latex(sent.get('en', ''))
        zh = sent.get('zh', '')  # CJK doesn't need escaping for most chars
        ja = sent.get('ja', '')  # CJK doesn't need escaping for most chars
        
        # Chinese and Japanese still need some escaping
        for char in ['&', '%', '$', '#', '_', '{', '}']:
            zh = zh.replace(char, '\\' + char)
            ja = ja.replace(char, '\\' + char)
        
        block = f'''\\noindent\\rutext{{{ru}}}

\\noindent\\entext{{{en}}}

\\noindent\\zhtext{{{zh}}}

\\noindent\\jatext{{{ja}}}

\\vspace{{0.8em}}
\\hrule
\\vspace{{0.8em}}
'''
        content_lines.append(block)
    
    return '\n'.join(content_lines)

def generate_pdf(json_path, output_path):
    """Generate PDF from translation JSON using XeLaTeX."""
    # Load translation data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    page_num = data.get('page', '?')
    chapter = data.get('chapter', '?')
    sentences = data.get('sentences', [])
    
    # Generate LaTeX content
    title = f"Durov Code - Page {page_num} (Chapter {chapter})"
    content = generate_content(sentences)
    
    # Fill template
    latex_doc = LATEX_TEMPLATE.replace('%%PAGE_TITLE%%', escape_latex(title))
    latex_doc = latex_doc.replace('%%CONTENT%%', content)
    
    # Write temporary LaTeX file
    output_path = Path(output_path)
    tex_path = output_path.with_suffix('.tex')
    
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(latex_doc)
    
    # Compile with XeLaTeX
    work_dir = output_path.parent or Path('.')
    try:
        result = subprocess.run(
            ['xelatex', '-interaction=nonstopmode', '-output-directory', str(work_dir), str(tex_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"XeLaTeX warning/errors (may still succeed):")
            # Print last 20 lines of log for debugging
            log_lines = result.stdout.split('\n')[-20:]
            for line in log_lines:
                if 'error' in line.lower() or 'warning' in line.lower():
                    print(line)
        
        # Check if PDF was created
        pdf_path = tex_path.with_suffix('.pdf')
        if pdf_path.exists():
            # Rename to desired output path
            if pdf_path != output_path:
                pdf_path.rename(output_path)
            print(f"PDF created successfully: {output_path}")
            
            # Clean up auxiliary files
            for ext in ['.aux', '.log', '.tex']:
                aux_file = output_path.with_suffix(ext)
                if aux_file.exists():
                    aux_file.unlink()
            
            return True
        else:
            print(f"Error: PDF not created")
            return False
            
    except subprocess.TimeoutExpired:
        print("Error: XeLaTeX compilation timed out")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_page_latex.py input.json output.pdf")
        sys.exit(1)
    
    json_path = sys.argv[1]
    output_path = sys.argv[2]
    
    success = generate_pdf(json_path, output_path)
    sys.exit(0 if success else 1)
