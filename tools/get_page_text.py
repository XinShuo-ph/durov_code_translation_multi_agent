import sys
import os

def get_page(page_num, full_text_path):
    if not os.path.exists(full_text_path):
        return "Error: File not found"
        
    with open(full_text_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by form feed
    pages = content.split('\f')
    
    # Check if page exists
    if 0 < page_num <= len(pages):
        return pages[page_num - 1]
    else:
        return f"Error: Page {page_num} out of range (1-{len(pages)})"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/get_page_text.py <page_num>")
        sys.exit(1)
        
    page = int(sys.argv[1])
    # Adjust for file location
    path = "durov_code_full.txt"
    print(get_page(page, path))
