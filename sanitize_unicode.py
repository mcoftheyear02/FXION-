import os
import re

# Mapping of problematic Unicode characters to ASCII equivalents
REPLACEMENTS = {
    "\u2014": "--",  # em dash
    "\u2013": "-",   # en dash
    "\u2500": "-",   # box horizontal
    "\u2550": "=",   # double box horizontal
    "\u2502": "|",   # box vertical
    "\u2551": "|",   # double box vertical
    "\u2713": "[OK]", # check mark
    "\u2717": "[ERR]", # cross mark
    "\u2605": "[*]", # star
    "\u03a8": "PSI", # Psi
    "\u03a3": "SUM", # Sigma
    "\u03a9": "OMEGA", # Omega
    "\u221e": "INF",  # infinity
    "\u2194": "<->", # left right arrow
    "\u2192": "->",  # right arrow
    "\u2554": "+",   # box double top left
    "\u2557": "+",   # box double top right
    "\u255a": "+",   # box double bottom left
    "\u255d": "+",   # box double bottom right
    "\u2551": "|",   # box double vertical
    "\u2550": "=",   # box double horizontal
}

def sanitize_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, "r", encoding="cp1252") as f:
                content = f.read()
        except Exception as e:
            print(f"Skipping {file_path}: {e}")
            return

    original_content = content
    for char, replacement in REPLACEMENTS.items():
        content = content.replace(char, replacement)
    
    # Also replace any other non-ASCII characters that might be left
    # (except for standard control characters)
    content = "".join([c if ord(c) < 128 else " " for c in content])

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Sanitized: {file_path}")

def main():
    for root, dirs, files in os.walk("."):
        if ".git" in dirs:
            dirs.remove(".git")
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")
        
        for file in files:
            if file.endswith(".py"):
                sanitize_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
