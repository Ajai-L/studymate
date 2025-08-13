from typing import Optional


def extract_text_from_pdf(file_path: str) -> Optional[str]:
    try:
        import pdfplumber
    except Exception:
        return None

    try:
        full_text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                if text:
                    full_text_parts.append(text)
        full_text = "\n\n".join(full_text_parts).strip()
        return full_text if full_text else None
    except Exception:
        return None