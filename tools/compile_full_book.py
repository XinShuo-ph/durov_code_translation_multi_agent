#!/usr/bin/env python3
"""
Compile all translation JSON files into a single multilingual PDF book.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def escape_latex(text):
    """Escape special LaTeX characters."""
    if not text:
        return ""
    replacements = [
        ('\\', '\\textbackslash{}'),
        ('&', '\\&'),
        ('%', '\\%'),
        ('$', '\\$'),
        ('#', '\\#'),
        ('_', '\\_'),
        ('{', '\\{'),
        ('}', '\\}'),
        ('~', '\\textasciitilde{}'),
        ('^', '\\textasciicircum{}'),
    ]
    result = text
    for old, new in replacements:
        if old == '\\':
            # Already handled backslash first
            continue
        result = result.replace(old, new)
    # Handle backslash specially to avoid double-escaping
    result = text.replace('\\', '\\textbackslash{}')
    for old, new in replacements[1:]:
        result = result.replace(old, new)
    return result


def generate_full_book_tex(translations_dir, output_path):
    """Generate a complete LaTeX document from all translation files."""
    
    translations_dir = Path(translations_dir)
    
    # Collect all page files
    page_files = sorted(translations_dir.glob("page_*.json"))
    
    if not page_files:
        print("No translation files found!")
        return None
    
    print(f"Found {len(page_files)} translation files")
    
    # LaTeX preamble
    tex_content = r"""\documentclass[a4paper,11pt]{book}
\usepackage{xltxtra}
\usepackage{xeCJK}
\usepackage{geometry}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{parskip}
\usepackage{fancyhdr}
\usepackage{hyperref}

\geometry{left=2cm,right=2cm,top=2.5cm,bottom=2.5cm}

% Fonts - use available Noto fonts
\setmainfont{Noto Serif}
\setCJKmainfont{Noto Serif CJK SC}
\newCJKfontfamily\zhfont{Noto Serif CJK SC}
\newCJKfontfamily\jafont{Noto Serif CJK JP}

% Colors
\definecolor{rucolor}{RGB}{0,0,0}      % Black
\definecolor{encolor}{RGB}{0,0,139}    % DarkBlue
\definecolor{zhcolor}{RGB}{139,0,0}    % DarkRed
\definecolor{jacolor}{RGB}{0,100,0}    % DarkGreen

% Translation Macro
\newcommand{\parallelsentence}[4]{
    \noindent
    \textcolor{rucolor}{\textbf{RU:}} #1 \\
    \textcolor{encolor}{\textbf{EN:}} #2 \\
    \textcolor{zhcolor}{\textbf{ZH:}} {\zhfont #3} \\
    \textcolor{jacolor}{\textbf{JA:}} {\jafont #4}
    \vspace{0.4cm}
}

% Page style
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE,RO]{\thepage}
\fancyhead[RE]{\leftmark}
\fancyhead[LO]{\rightmark}
\renewcommand{\headrulewidth}{0.4pt}

% Chapter title format
\titleformat{\chapter}[display]
  {\normalfont\huge\bfseries}{\chaptertitlename\ \thechapter}{20pt}{\Huge}

\begin{document}

% Title page
\begin{titlepage}
\centering
\vspace*{3cm}
{\Huge\bfseries Код Дурова\par}
\vspace{0.5cm}
{\LARGE\textit{Durov Code}\par}
\vspace{1cm}
{\Large Реальная история «ВКонтакте» и её создателя\par}
{\large\textit{The Real Story of VKontakte and Its Creator}\par}
\vspace{2cm}
{\Large Николай В. Кононов\par}
{\large\textit{Nikolai V. Kononov}\par}
\vspace{3cm}
{\large Multilingual Edition\par}
{\normalsize Russian • English • 中文 • 日本語\par}
\vspace{2cm}
{\small Translated by AI Collaborative Translation System\par}
\end{titlepage}

\tableofcontents

"""

    current_chapter = None
    chapter_titles = {
        0: ("Front Matter", "Вступление"),
        1: ("Botanical Garden", "Ботанический сад"),
        2: ("University Years", "Университетские годы"),
        3: ("VKontakte Founding", "Создание ВКонтакте"),
        4: ("Growth & Scaling", "Рост и масштабирование"),
        5: ("Business Conflicts", "Бизнес-конфликты"),
        6: ("Philosophy", "Философия"),
        7: ("Future Outlook", "Взгляд в будущее"),
    }

    for page_file in page_files:
        try:
            with open(page_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading {page_file}: {e}")
            continue
        
        page_num = data.get('page', 0)
        chapter_num = data.get('chapter', 0)
        sentences = data.get('sentences', [])
        
        # Start new chapter if needed
        if chapter_num != current_chapter:
            current_chapter = chapter_num
            en_title, ru_title = chapter_titles.get(chapter_num, (f"Chapter {chapter_num}", f"Глава {chapter_num}"))
            if chapter_num == 0:
                tex_content += f"\n\\chapter*{{{ru_title} / {en_title}}}\n\\addcontentsline{{toc}}{{chapter}}{{{en_title}}}\n\n"
            else:
                tex_content += f"\n\\chapter{{{ru_title} / {en_title}}}\n\n"
        
        # Add page marker
        tex_content += f"\n\\subsection*{{Page {page_num}}}\n\n"
        
        # Skip empty pages
        if not sentences:
            tex_content += "\\textit{[Page contains no translatable text]}\n\n"
            continue
        
        # Add each sentence
        for s in sentences:
            ru = escape_latex(s.get('ru', ''))
            en = escape_latex(s.get('en', ''))
            zh = escape_latex(s.get('zh', ''))
            ja = escape_latex(s.get('ja', ''))
            
            if ru or en or zh or ja:
                tex_content += f"\\parallelsentence\n{{{ru}}}\n{{{en}}}\n{{{zh}}}\n{{{ja}}}\n\n"
    
    tex_content += r"""
\chapter*{About This Edition}
\addcontentsline{toc}{chapter}{About This Edition}

This multilingual edition of "Код Дурова" (Durov Code) by Nikolai V. Kononov presents the original Russian text alongside translations in English, Chinese (Simplified), and Japanese.

\textbf{Color Key:}
\begin{itemize}
    \item \textcolor{rucolor}{\textbf{RU:}} Original Russian text
    \item \textcolor{encolor}{\textbf{EN:}} English translation
    \item \textcolor{zhcolor}{\textbf{ZH:}} Chinese translation (简体中文)
    \item \textcolor{jacolor}{\textbf{JA:}} Japanese translation (日本語)
\end{itemize}

\vspace{1cm}
\textit{Translated using AI collaborative multi-agent translation system.}

\end{document}
"""

    # Write the tex file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(tex_content)
    
    print(f"Generated LaTeX file: {output_path}")
    return output_path


def compile_pdf(tex_path, output_dir):
    """Compile LaTeX to PDF using XeLaTeX."""
    print(f"Compiling {tex_path}...")
    
    # Run XeLaTeX twice for TOC
    for i in range(2):
        result = subprocess.run(
            ['xelatex', '-interaction=nonstopmode', '-output-directory=' + str(output_dir), str(tex_path)],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode != 0:
            print(f"XeLaTeX run {i+1} warnings/errors (may be non-fatal):")
            # Print last 50 lines of output
            lines = result.stdout.split('\n')
            for line in lines[-50:]:
                if line.strip():
                    print(f"  {line}")
    
    pdf_path = tex_path.replace('.tex', '.pdf')
    if os.path.exists(pdf_path):
        print(f"Successfully compiled: {pdf_path}")
        return pdf_path
    else:
        print("PDF compilation may have failed - check the log file")
        return None


if __name__ == "__main__":
    translations_dir = sys.argv[1] if len(sys.argv) > 1 else "translations"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    
    os.makedirs(output_dir, exist_ok=True)
    
    tex_path = os.path.join(output_dir, "durov_code_multilingual.tex")
    
    tex_file = generate_full_book_tex(translations_dir, tex_path)
    
    if tex_file:
        compile_pdf(tex_file, output_dir)
