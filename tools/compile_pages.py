import json
import os
import subprocess
import sys

def compile_page(json_path, output_dir):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    page_num = data.get('page')
    sentences = data.get('sentences', [])
    
    tex_content = r"""\documentclass[a4paper,12pt]{article}
\usepackage{xltxtra}
\usepackage{xeCJK}
\usepackage{geometry}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{parskip}

\geometry{left=2cm,right=2cm,top=2cm,bottom=2cm}

% Fonts
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
    \textbf{\textcolor{rucolor}{RU:}} #1 \\
    \textbf{\textcolor{encolor}{EN:}} #2 \\
    \textbf{\textcolor{zhcolor}{ZH:}} {\zhfont #3} \\
    \textbf{\textcolor{jacolor}{JA:}} {\jafont #4}
    \vspace{0.5cm}
}

\begin{document}

\section*{Page """ + str(page_num) + r""" Translation}
"""

    for s in sentences:
        ru = s.get('ru', '').replace('&', '\\&').replace('%', '\\%').replace('$', '\\$').replace('#', '\\#').replace('_', '\\_')
        en = s.get('en', '').replace('&', '\\&').replace('%', '\\%').replace('$', '\\$').replace('#', '\\#').replace('_', '\\_')
        zh = s.get('zh', '').replace('&', '\\&').replace('%', '\\%').replace('$', '\\$').replace('#', '\\#').replace('_', '\\_')
        ja = s.get('ja', '').replace('&', '\\&').replace('%', '\\%').replace('$', '\\$').replace('#', '\\#').replace('_', '\\_')
        
        tex_content += f"\\parallelsentence\n{{{ru}}}\n{{{en}}}\n{{{zh}}}\n{{{ja}}}\n\n"

    tex_content += r"\end{document}"
    
    base_name = os.path.basename(json_path).replace('.json', '')
    tex_file = os.path.join(output_dir, f"{base_name}.tex")
    
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(tex_content)
        
    print(f"Compiling {tex_file}...")
    subprocess.run(['xelatex', '-output-directory=' + output_dir, tex_file], check=True)
    print(f"Compiled {base_name}.pdf")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compile_pages.py <json_file> <output_dir>")
        sys.exit(1)
        
    json_path = sys.argv[1]
    output_dir = sys.argv[2]
    compile_page(json_path, output_dir)
