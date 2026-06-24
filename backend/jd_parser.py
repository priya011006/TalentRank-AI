import docx
from pathlib import Path

def parse_docx(file_path: Path) -> str:
    """
    Load a Microsoft Word document (.docx) and extract all paragraphs 
    into a single string, separated by newlines.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Job Description file not found at: {file_path}")
        
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)
