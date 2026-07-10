from typing import List, Dict, Any
from app.utils.extractors import ExtractedPage

class ChunkingService:
    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", " ", ""]

    def _split_text_recursively(self, text: str, separators: List[str]) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text]

        # ถ้าไม่มี separator ให้แบ่งแล้ว ใช้ตัด character แทน
        if not separators:
            chunks = []
            for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
                chunks.append(text[i:i + self.chunk_size])
            return chunks

        separator = separators[0]
        splits = text.split(separator)
        
        chunks = []
        current_chunk = ""
        
        for split in splits:
            # ถ้า chunk ที่ตัดมายังใหญ่ไป ให้ใช้ separator ตัวต่อไปตัดเพิ่ม
            if len(split) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                chunks.extend(self._split_text_recursively(split, separators[1:]))
            else:
                sep_len = len(separator) if current_chunk else 0
                # ถ้า chunk ไม่เต็มให้เติมเพิ่ม
                if len(current_chunk) + sep_len + len(split) <= self.chunk_size:
                    current_chunk += (separator if current_chunk else "") + split
                else:
                    # ถ้า chunk เต็มให้ append แล้วเริ่มต้นใหม่
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    # Initialize next chunk with overlap from the end of current_chunk
                    overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                    current_chunk = current_chunk[overlap_start:]
                    current_chunk += (separator if current_chunk else "") + split

        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return [c for c in chunks if c]

    def chunk_document(self, filename: str, pages: List[ExtractedPage]) -> List[Dict[str, Any]]:
        all_chunks = []
        global_chunk_idx = 0

        for page in pages:
            text = page["text"]
            page_num = page["page_number"]
            row_range = page["row_range"]
            
            # ถ้าเป็น csv xlsx หรืออะไรที่แบ่งเป็นแถวมาแล้วให้ใช้ได้เลยเพราะทำ pre chunk มาแล้ว
            if row_range:
                splits = [text]
            else:
                splits = self._split_text_recursively(text, self.separators)

            for split in splits:
                all_chunks.append({
                    "text": split,
                    "chunk_index": global_chunk_idx,
                    "document_name": filename,
                    "page_number": page_num,
                    "row_range": row_range
                })
                global_chunk_idx += 1

        return all_chunks
