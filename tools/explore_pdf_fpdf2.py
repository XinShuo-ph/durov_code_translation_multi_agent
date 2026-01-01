from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os

class MultilingualPDF(FPDF):
    def header(self):
        self.set_font('NotoSans', '', 10)
        self.cell(0, 10, 'Durov Code - Multilingual Translation Demo', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

def create_demo_pdf(output_path):
    pdf = MultilingualPDF()
    
    # Register fonts
    # Using installed NotoSans for Latin/Cyrillic
    pdf.add_font('NotoSans', '', '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf')
    # Using downloaded CJK fonts
    pdf.add_font('NotoSansSC', '', '/workspace/tools/fonts/NotoSansCJKsc-Regular.otf')
    pdf.add_font('NotoSansJP', '', '/workspace/tools/fonts/NotoSansCJKjp-Regular.otf')

    pdf.add_page()
    
    # Set text size
    pdf.set_font_size(12)
    
    # Sample text
    sentences = [
        {
            'ru': 'Мальчик с томом Сервантеса выходит из подъезда...',
            'en': 'A boy with a volume of Cervantes exits the building entrance...',
            'zh': '一个手捧塞万提斯著作的男孩走出公寓楼...',
            'ja': 'セルバンテスの本を持った少年が建物の入り口を出る...'
        },
        {
            'ru': 'Рядом море.',
            'en': 'The sea is nearby.',
            'zh': '大海就在附近。',
            'ja': '海が近くにある。'
        }
    ]
    
    for sent in sentences:
        # Russian - Black
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('NotoSans', '', 12)
        pdf.multi_cell(0, 8, sent['ru'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # English - Blue
        pdf.set_text_color(0, 0, 255)
        pdf.set_font('NotoSans', '', 12)
        pdf.multi_cell(0, 8, sent['en'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Chinese - Red
        pdf.set_text_color(255, 0, 0)
        pdf.set_font('NotoSansSC', '', 12)
        pdf.multi_cell(0, 8, sent['zh'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Japanese - Green
        pdf.set_text_color(0, 128, 0)
        pdf.set_font('NotoSansJP', '', 12)
        pdf.multi_cell(0, 8, sent['ja'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Spacing
        pdf.ln(5)
        
    pdf.output(output_path)
    print(f"PDF created at {output_path}")

if __name__ == "__main__":
    output_dir = '/workspace/output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    create_demo_pdf(os.path.join(output_dir, 'demo_fpdf2.pdf'))
