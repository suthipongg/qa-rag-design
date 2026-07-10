from gradio.tunneling import CHUNK_SIZE
import io
import fitz  # PyMuPDF
import pandas as pd
from typing import TypedDict, List


class ExtractedPage(TypedDict):
    text: str
    page_number: int | None
    row_range: str | None


def extract_pdf(file_content: bytes) -> List[ExtractedPage]:
    pages = []
    doc = fitz.open(stream=file_content, filetype="pdf")
    
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            pages.append({
                "text": text,
                "page_number": i + 1,
                "row_range": None
            })
            
    doc.close()
    return pages


def extract_markdown(file_content: bytes) -> List[ExtractedPage]:
    text = file_content.decode("utf-8", errors="ignore").strip()
    if not text:
        return []
    return [{
        "text": text,
        "page_number": None,
        "row_range": None
    }]


CHUNK_SIZE = 20

def extract_csv(file_content: bytes) -> List[ExtractedPage]:
    df = pd.read_csv(io.BytesIO(file_content))
    if df.empty:
        return []

    pages = []
    for start_idx in range(0, len(df), CHUNK_SIZE):
        end_idx = min(start_idx + CHUNK_SIZE, len(df))
        sub_df = df.iloc[start_idx:end_idx]
        
        text_lines = []
        for idx, row in sub_df.iterrows():
            row_items = [f"{col}: {val}" for col, val in row.items()]
            text_lines.append(f"Row {idx + 1}: " + ", ".join(row_items))
            
        chunk_text = "\n".join(text_lines)
        pages.append({
            "text": chunk_text,
            "page_number": None,
            "row_range": f"{start_idx + 1}-{end_idx}"
        })
        
    return pages


def extract_xlsx(file_content: bytes) -> List[ExtractedPage]:
    pages = []
    excel_file = pd.ExcelFile(io.BytesIO(file_content))
    
    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        if df.empty:
            continue
            
        for start_idx in range(0, len(df), CHUNK_SIZE):
            end_idx = min(start_idx + CHUNK_SIZE, len(df))
            sub_df = df.iloc[start_idx:end_idx]
            
            text_lines = [f"Sheet: {sheet_name}"]
            for idx, row in sub_df.iterrows():
                row_items = [f"{col}: {val}" for col, val in row.items()]
                text_lines.append(f"Row {idx + 1}: " + ", ".join(row_items))
                
            chunk_text = "\n".join(text_lines)
            pages.append({
                "text": chunk_text,
                "page_number": None,
                "row_range": f"Sheet {sheet_name}, Rows {start_idx + 1}-{end_idx}"
            })
            
    return pages


def extract_text_content(file_content: bytes, filename: str) -> List[ExtractedPage]:
    ext = filename.split(".")[-1].lower()
    
    if ext == "pdf":
        return extract_pdf(file_content)
    elif ext in ["md", "txt"]:
        return extract_markdown(file_content)
    elif ext == "csv":
        return extract_csv(file_content)
    elif ext in ["xlsx", "xls"]:
        return extract_xlsx(file_content)
    else:
        raise ValueError(f"Unsupported file format: .{ext}")
