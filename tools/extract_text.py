import subprocess
import hashlib
import os

def extract_text(pdf_path, output_path):
    try:
        # Use pdftotext to extract text
        # -layout maintains layout
        subprocess.run(['pdftotext', '-layout', pdf_path, output_path], check=True)
        print(f"Text extracted to {output_path}")
        
        # Calculate hash
        with open(output_path, 'rb') as f:
            content = f.read()
            file_hash = hashlib.sha256(content).hexdigest()
            
        print(f"Hash: {file_hash}")
        return file_hash
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None

if __name__ == "__main__":
    pdf_path = "/workspace/durov_code_book.pdf"
    output_path = "/workspace/durov_code_book_extracted.txt"
    
    if os.path.exists(pdf_path):
        extract_text(pdf_path, output_path)
    else:
        print(f"PDF not found at {pdf_path}")
