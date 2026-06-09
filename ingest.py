"""
Milestone 3: Document ingestion and chunking pipeline.

Loads all .txt files from documents/, cleans them, splits into
overlapping character-level chunks, and returns a list of dicts:
    {"text": str, "source": str, "chunk_index": int}

Usage:
    python ingest.py          # prints 5 sample chunks and total count
    from ingest import load_chunks   # import for use in embed.py
"""

import os
import re
from pathlib import Path

DOCUMENTS_DIR = Path(__file__).parent / "documents"
CHUNK_SIZE = 400      # characters per chunk
CHUNK_OVERLAP = 80    # characters of overlap between consecutive chunks


def clean(text: str) -> str:
    """Remove header lines (SOURCE/URL) and normalize whitespace."""
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        # Skip the SOURCE: and URL: header lines at the top of each file
        if line.strip().startswith("SOURCE:") or line.strip().startswith("URL:"):
            continue
        cleaned.append(line)
    text = "\n".join(cleaned)
    # Collapse runs of 3+ blank lines into two
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, source: str) -> list[dict]:
    """Split text into overlapping chunks of CHUNK_SIZE characters."""
    chunks = []
    start = 0
    idx = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()
        if chunk:
            chunks.append({
                "text": chunk,
                "source": source,
                "chunk_index": idx,
            })
            idx += 1
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def load_chunks() -> list[dict]:
    """Load and chunk all .txt files in the documents directory."""
    all_chunks = []
    for path in sorted(DOCUMENTS_DIR.glob("*.txt")):
        raw = path.read_text(encoding="utf-8")
        text = clean(raw)
        chunks = chunk_text(text, source=path.name)
        all_chunks.extend(chunks)
    return all_chunks


if __name__ == "__main__":
    chunks = load_chunks()
    print(f"Total chunks: {len(chunks)}\n")
    print("=" * 60)
    print("5 SAMPLE CHUNKS")
    print("=" * 60)
    # Pick samples spread across the corpus
    step = max(1, len(chunks) // 5)
    samples = [chunks[i * step] for i in range(5)]
    for i, chunk in enumerate(samples, 1):
        print(f"\n[Sample {i}] source={chunk['source']}  chunk_index={chunk['chunk_index']}")
        print("-" * 40)
        print(chunk["text"])
