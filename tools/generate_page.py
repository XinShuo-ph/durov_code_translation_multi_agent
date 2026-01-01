from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os
import json
import sys

class MultilingualPDF(FPDF):
    def header(self):
        self.set_font('NotoSans', '', 10)
        # Using cell instead of direct text to avoid issues, though header usually fixed
        self.cell(0, 10, 'Durov Code - Translation', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

def generate_page(json_path, output_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    pdf = MultilingualPDF()
    
    # Register fonts
    pdf.add_font('NotoSans', '', '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf')
    pdf.add_font('NotoSansSC', '', '/workspace/tools/fonts/NotoSansCJKsc-Regular.otf')
    pdf.add_font('NotoSansJP', '', '/workspace/tools/fonts/NotoSansCJKjp-Regular.otf')

    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title/Page info
    pdf.set_font('NotoSans', '', 14)
    pdf.cell(0, 10, f"Page {data.get('page')} - Chapter {data.get('chapter')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.ln(5)
    
    for sent in data['sentences']:
        # Russian - Black
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('NotoSans', '', 12)
        pdf.multi_cell(0, 6, sent['ru'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # English - Blue
        pdf.set_text_color(0, 0, 255)
        pdf.set_font('NotoSans', '', 12)
        pdf.multi_cell(0, 6, sent['en'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Chinese - Red
        pdf.set_text_color(255, 0, 0)
        pdf.set_font('NotoSansSC', '', 12)
        pdf.multi_cell(0, 6, sent['zh'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Japanese - Green
        pdf.set_text_color(0, 128, 0)
        pdf.set_font('NotoSansJP', '', 12)
        pdf.multi_cell(0, 6, sent['ja'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Spacing
        pdf.ln(5)
        
    pdf.output(output_path)
    print(f"PDF created at {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_page.py input.json output.pdf")
        sys.exit(1)
        
    json_path = sys.argv[1]
    output_path = sys.argv[2]
    generate_page(json_path, output_path)
