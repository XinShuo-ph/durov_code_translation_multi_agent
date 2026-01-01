import hashlib
import os

files = [
    "/workspace/durov_code_book.txt",
    "/workspace/chapter_structure.md",
    "/workspace/research/durov_bio.md",
    "/workspace/research/vk_history.md",
    "/workspace/research/russia_context.md",
    "/workspace/research/chapter_summaries.md"
]

for f in files:
    if os.path.exists(f):
        sha256_hash = hashlib.sha256()
        with open(f, "rb") as file:
            for byte_block in iter(lambda: file.read(4096), b""):
                sha256_hash.update(byte_block)
        print(f"{os.path.basename(f)}: {sha256_hash.hexdigest()[:8]}")
    else:
        print(f"{os.path.basename(f)}: NOT FOUND")
