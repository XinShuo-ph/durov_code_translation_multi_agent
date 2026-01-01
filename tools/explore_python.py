from reportlab.lib import pagesizes, colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def create_demo(output_path):
    doc = SimpleDocTemplate(output_path, pagesize=pagesizes.A4)
    elements = []
    
    # Register Font
    font_path = "/usr/share/fonts/truetype/arphic/uming.ttc"
    font_name = 'Helvetica' # Default
    
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('UMing', font_path, subfontIndex=0))
            font_name = 'UMing'
        except Exception as e:
            print(f"Font registration error: {e}")
            pass
    else:
        print("Font not found!")

    styles = getSampleStyleSheet()
    style_normal = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        leading=14
    )
    
    # Data for Page 13 (Brief)
    data = [
        [
            Paragraph("<b>Russian</b>", style_normal),
            Paragraph("<b>English</b>", style_normal),
            Paragraph("<b>Chinese</b>", style_normal),
            Paragraph("<b>Japanese</b>", style_normal)
        ],
        [
            Paragraph("Мальчик с томом Сервантеса выходит из подъезда...", style_normal),
            Paragraph("A boy with a volume of Cervantes exits the building entrance...", style_normal),
            Paragraph("一个手捧塞万提斯著作的男孩走出公寓楼...", style_normal),
            Paragraph("セルバンテスの本を持った少年が建物の入り口を出る...", style_normal)
        ]
    ]
    
    # Page width is A4[0] = 595.27
    # Margins are default ~72
    # Available width ~450
    col_w = 450 / 4
    
    t = Table(data, colWidths=[col_w]*4)
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ('FONTNAME', (0,0), (-1,-1), font_name)
    ]))
    
    elements.append(Paragraph("Page 13 Demo (Python)", styles['Title']))
    elements.append(t)
    
    doc.build(elements)
    print(f"Created {output_path}")

if __name__ == "__main__":
    create_demo("examples/demo_python.pdf")
