import subprocess
import os
import hashlib

def extract_text(pdf_path, output_path):
    print(f"Extracting text from {pdf_path} to {output_path}...")
    try:
        # Use pdftotext with layout preservation
        subprocess.run(['pdftotext', '-layout', pdf_path, output_path], check=True)
        print("Extraction complete.")
        
        # Calculate hash of the extracted text
        with open(output_path, 'rb') as f:
            content = f.read()
            sha256_hash = hashlib.sha256(content).hexdigest()
            print(f"SHA256 Hash: {sha256_hash}")
            return sha256_hash
    except subprocess.CalledProcessError as e:
        print(f"Error running pdftotext: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    pdf_path = "/workspace/durov_code_book.pdf"
    output_path = "/workspace/research/durov_code_text.txt"
    
    # Ensure research directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    extract_text(pdf_path, output_path)
