import os
import re
import time
import math
import sqlite3
from typing import Dict, Any, List, Optional

class KnowledgeVaultEngine:
    """Manages document ingestion, codebase analysis, PDF text extraction, and grounded RAG querying."""

    def __init__(self, db_path: str = "data/tony_vault.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vault_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    doc_type TEXT NOT NULL,
                    total_chunks INTEGER NOT NULL,
                    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vault_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id INTEGER NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    chunk_text TEXT NOT NULL,
                    token_count INTEGER,
                    FOREIGN KEY(doc_id) REFERENCES vault_documents(id)
                )
            """)
            conn.commit()

    def extract_text_from_file(self, file_path: str) -> str:
        """Extracts text content from TXT, MD, Python, JS, JSON, or PDF files."""
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            # Attempt PDF extraction using pypdf, pdfminer, or fallback regex text extraction
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                pages_text = [page.extract_text() or "" for page in reader.pages]
                return "\n".join(pages_text)
            except ImportError:
                try:
                    import pypdf2
                    reader = pypdf2.PdfReader(file_path)
                    pages_text = [page.extract_text() or "" for page in reader.pages]
                    return "\n".join(pages_text)
                except Exception:
                    # Fallback binary text extractor for simple PDFs
                    with open(file_path, "rb") as f:
                        raw = f.read().decode("latin-1", errors="ignore")
                        clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', raw)
                        return clean[:50000]
            except Exception as e:
                return f"Error reading PDF: {str(e)}"
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

    def chunk_text(self, text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
        """Splits document text into overlapping chunks for semantic retrieval."""
        words = text.split()
        if not words:
            return []
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            i += (chunk_size - overlap)
        return chunks

    def ingest_document(self, filename: str, content: str, doc_type: str = "text") -> Dict[str, Any]:
        """Ingests a document or code snippet into the Knowledge Vault."""
        chunks = self.chunk_text(content)
        if not chunks:
            return {"success": False, "error": "Document contains no readable text."}

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO vault_documents (filename, doc_type, total_chunks) VALUES (?, ?, ?)",
                (filename, doc_type, len(chunks))
            )
            doc_id = cursor.lastrowid

            for idx, ch in enumerate(chunks):
                token_count = len(ch.split())
                cursor.execute(
                    "INSERT INTO vault_chunks (doc_id, chunk_index, chunk_text, token_count) VALUES (?, ?, ?, ?)",
                    (doc_id, idx, ch, token_count)
                )
            conn.commit()

        return {
            "success": True,
            "doc_id": doc_id,
            "filename": filename,
            "chunks_count": len(chunks),
            "total_words": len(content.split())
        }

    def search_vault(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Performs lexical and TF-IDF weighted scoring to find top matching chunks."""
        query_terms = set(re.findall(r'\w+', query.lower()))
        if not query_terms:
            return []

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, c.doc_id, d.filename, d.doc_type, c.chunk_index, c.chunk_text
                FROM vault_chunks c
                JOIN vault_documents d ON c.doc_id = d.id
            """)
            rows = cursor.fetchall()

        scored_chunks = []
        for row in rows:
            chunk_id, doc_id, filename, doc_type, chunk_idx, text = row
            text_lower = text.lower()
            words = re.findall(r'\w+', text_lower)
            if not words:
                continue

            score = 0.0
            for term in query_terms:
                count = text_lower.count(term)
                if count > 0:
                    score += count * (1.0 + math.log(1 + 10.0 / (len(words) + 1)))

            if score > 0:
                scored_chunks.append({
                    "chunk_id": chunk_id,
                    "doc_id": doc_id,
                    "filename": filename,
                    "doc_type": doc_type,
                    "chunk_index": chunk_idx,
                    "text": text,
                    "score": round(score, 3)
                })

        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]

    def list_documents(self) -> List[Dict[str, Any]]:
        """Returns all ingested documents in the vault."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, filename, doc_type, total_chunks, ingested_at FROM vault_documents ORDER BY id DESC")
            rows = cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "filename": r[1],
                    "doc_type": r[2],
                    "total_chunks": r[3],
                    "ingested_at": r[4]
                }
                for r in rows
            ]
