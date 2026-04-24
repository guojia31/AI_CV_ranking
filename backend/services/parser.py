import pandas as pd
from docx import Document
import PyPDF2


def read_file(file, filename):

    if filename.endswith(".txt"):
        return file.read().decode("utf-8", errors="ignore")

    if filename.endswith(".csv"):
        df = pd.read_csv(file)
        return df.to_string(index=False)

    if filename.endswith(".docx"):
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])

    if filename.endswith(".pdf"):
        text = ""
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    return ""
