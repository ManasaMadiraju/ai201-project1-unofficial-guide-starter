"""
Milestone 5: Grounded response generation using Groq + retrieved context.
Stretch 3: Metadata filtering by category passed through to retrieve().
Stretch 4: Conversational memory via history parameter.

Usage:
    from query import ask
    result = ask("Which freshman dorm is best for quiet studying?")
    result = ask("What about laundry?", history=result["history"])
    print(result["answer"])
    print(result["sources"])
"""

import os
from groq import Groq
from dotenv import load_dotenv
from embed import retrieve

load_dotenv()

_client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are the SCU Unofficial Guide — a helpful assistant that answers questions about Santa Clara University using ONLY the information provided in the documents below.

Rules you must follow:
1. Answer using ONLY the information in the provided document excerpts. Do not use your general knowledge about universities, professors, or dining.
2. If the provided excerpts do not contain enough information to answer the question, respond with: "I don't have enough information in my documents to answer that."
3. Be specific and cite which document your answer comes from (e.g., "According to student reviews on Rate My Professors...").
4. You may use previous conversation turns to resolve references (e.g., "her", "that professor", "the same dorm") — but still answer only from the retrieved documents.
5. Keep answers concise and directly useful to a current or incoming SCU student."""


def build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a context block for the prompt."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"[Document {i} — {chunk['source']}]\n{chunk['text']}")
    return "\n\n".join(parts)


def ask(
    question: str,
    k: int = 5,
    category: str | None = None,
    history: list[dict] | None = None,
) -> dict:
    """
    Retrieve relevant chunks and generate a grounded answer.

    Args:
        question: The user's question.
        k:        Number of chunks to retrieve.
        category: Optional metadata filter — "professor_reviews", "dining",
                  "housing", or "campus_life". None = search all.
        history:  Prior conversation turns as a list of
                  {"role": "user"/"assistant", "content": str} dicts.

    Returns:
        {
            "answer": str,
            "sources": list[str],
            "chunks": list[dict],
            "history": list[dict],   # updated history including this turn
        }
    """
    chunks = retrieve(question, k=k, category=category)
    context = build_context(chunks)

    user_message = f"""Document excerpts:
{context}

Question: {question}"""

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    response = _client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2,
    )

    answer = response.choices[0].message.content.strip()

    # Deduplicate sources while preserving order
    seen = set()
    sources = []
    for chunk in chunks:
        if chunk["source"] not in seen:
            seen.add(chunk["source"])
            sources.append(chunk["source"])

    # Build updated history for the next turn
    updated_history = list(history or [])
    updated_history.append({"role": "user", "content": user_message})
    updated_history.append({"role": "assistant", "content": answer})

    return {"answer": answer, "sources": sources, "chunks": chunks, "history": updated_history}


if __name__ == "__main__":
    print("=== Stretch 3: Metadata filtering ===")
    r = ask("Which professors are best at giving feedback?", category="professor_reviews")
    print(f"Q: Which professors are best at giving feedback? [category=professor_reviews]")
    print(r["answer"])
    print(f"Sources: {r['sources']}\n")

    print("=== Stretch 4: Conversational memory ===")
    r1 = ask("Tell me about Professor Ye Cai.")
    print(f"Q1: Tell me about Professor Ye Cai.")
    print(r1["answer"])
    print()

    r2 = ask("What about her exams specifically?", history=r1["history"])
    print(f"Q2: What about her exams specifically?")
    print(r2["answer"])
    print(f"Sources: {r2['sources']}\n")
