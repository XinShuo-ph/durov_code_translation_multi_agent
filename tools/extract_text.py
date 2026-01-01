import subprocess
import hashlib
import os
import sys

def extract_text(pdf_path, output_path):
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file {pdf_path} not found.")
        return None

    print(f"Extracting text from {pdf_path} to {output_path}...")
    try:
        # Use pdftotext with layout preservation
        subprocess.run(["pdftotext", "-layout", pdf_path, output_path], check=True)
        print("Extraction complete.")
        
        # Calculate hash
        with open(output_path, "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        print(f"SHA256: {digest[:8]}")
        return digest
    except subprocess.CalledProcessError as e:
        print(f"Error extracting text: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

if __name__ == "__main__":
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "durov_code_book.pdf")
    output_path = "durov_code_full.txt"
    digest = extract_text(pdf_path, output_path)
    if digest:
        print(f"SUCCESS: Text extracted. Hash: {digest[:8]}")
    else:
        sys.exit(1)
