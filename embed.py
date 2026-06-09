"""
Milestone 4: Embed chunks and store in ChromaDB. Expose a retrieve() function.
Stretch 3: Metadata filtering by category (professor_reviews, dining, housing, campus_life).

Usage:
    python embed.py           # builds/rebuilds the vector store, then tests retrieval
    from embed import retrieve  # import for use in query.py
"""

import chromadb
from sentence_transformers import SentenceTransformer
from ingest import load_chunks

COLLECTION_NAME = "scu_guide"
DB_PATH = "./chroma_db"
TOP_K = 5

# Map source filename prefixes to categories for metadata filtering
_CATEGORY_MAP = {
    "rmp_": "professor_reviews",
    "top10_professors": "professor_reviews",
    "scu_dining": "dining",
    "food_insecurity": "dining",
    "scu_food_allergy": "dining",
    "scu_dorms": "housing",
    "scu_campus_life": "campus_life",
    "scu_student_reviews": "campus_life",
}

def _get_category(source: str) -> str:
    for prefix, category in _CATEGORY_MAP.items():
        if source.startswith(prefix):
            return category
    return "campus_life"  # fallback

# Load model once at module level so it isn't reloaded on every call
_model = SentenceTransformer("all-MiniLM-L6-v2")
_client = chromadb.PersistentClient(path=DB_PATH)


def build_index():
    """Embed all chunks and store them in ChromaDB. Drops and recreates the collection."""
    # Drop existing collection so we start fresh on rebuild
    try:
        _client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = _client.create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    chunks = load_chunks()

    texts = [c["text"] for c in chunks]
    embeddings = _model.encode(texts, show_progress_bar=True).tolist()

    collection.add(
        ids=[f"{c['source']}__chunk{c['chunk_index']}" for c in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[
            {
                "source": c["source"],
                "chunk_index": c["chunk_index"],
                "category": _get_category(c["source"]),
            }
            for c in chunks
        ],
    )
    print(f"Indexed {len(chunks)} chunks into '{COLLECTION_NAME}'.")
    return collection


def _get_collection():
    """Return the existing collection, or raise a clear error if not built yet."""
    try:
        return _client.get_collection(COLLECTION_NAME)
    except Exception:
        raise RuntimeError(
            "Vector store not found. Run `python embed.py` to build the index first."
        )


def retrieve(query: str, k: int = TOP_K, category: str | None = None) -> list[dict]:
    """
    Embed the query and return the top-k most relevant chunks.

    Args:
        query:    The user's question.
        k:        Number of chunks to return.
        category: Optional filter — one of "professor_reviews", "dining",
                  "housing", "campus_life". If None, searches all documents.

    Returns a list of dicts:
        {"text": str, "source": str, "chunk_index": int, "category": str, "distance": float}
    """
    collection = _get_collection()
    query_embedding = _model.encode([query]).tolist()

    where = {"category": category} if category else None
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text": text,
            "source": meta["source"],
            "chunk_index": meta["chunk_index"],
            "category": meta.get("category", ""),
            "distance": round(dist, 4),
        })
    return chunks


if __name__ == "__main__":
    # Build the index
    build_index()

    # Test with 3 evaluation plan queries
    test_queries = [
        "What do students say about Professor Ye Cai's exams?",
        "Which freshman dorm is best for quiet studying?",
        "What happens to unused dining points at the end of the quarter?",
    ]

    print("\n" + "=" * 60)
    print("RETRIEVAL TEST — 3 EVALUATION QUERIES")
    print("=" * 60)

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 40)
        results = retrieve(query)
        for r in results:
            print(f"  [{r['distance']:.4f}] ({r['source']})  chunk {r['chunk_index']}")
            print(f"  {r['text'][:120]}...")
            print()
