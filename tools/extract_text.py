import subprocess
import os
import hashlib

def extract_text(pdf_path, output_path):
    """Extracts text from PDF using pdftotext."""
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found.")
        return False
    
    try:
        subprocess.run(["pdftotext", "-layout", pdf_path, output_path], check=True)
        print(f"Text extracted to {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting text: {e}")
        return False
    except FileNotFoundError:
        print("Error: pdftotext not found.")
        return False

def calculate_hash(file_path):
    """Calculates SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

if __name__ == "__main__":
    pdf_file = "/workspace/durov_code_book.pdf"
    output_file = "/workspace/durov_code_book.txt"
    
    if extract_text(pdf_file, output_file):
        file_hash = calculate_hash(output_file)
        print(f"Hash: {file_hash}")
