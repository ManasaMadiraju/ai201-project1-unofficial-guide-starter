"""
Milestone 5: Grounded response generation using Groq + retrieved context.

Usage:
    from query import ask
    result = ask("Which freshman dorm is best for quiet studying?")
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
4. Keep answers concise and directly useful to a current or incoming SCU student."""


def build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a context block for the prompt."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"[Document {i} — {chunk['source']}]\n{chunk['text']}")
    return "\n\n".join(parts)


def ask(question: str, k: int = 5) -> dict:
    """
    Retrieve relevant chunks and generate a grounded answer.

    Returns:
        {"answer": str, "sources": list[str], "chunks": list[dict]}
    """
    chunks = retrieve(question, k=k)
    context = build_context(chunks)

    user_message = f"""Document excerpts:
{context}

Question: {question}"""

    response = _client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
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

    return {"answer": answer, "sources": sources, "chunks": chunks}


if __name__ == "__main__":
    test_questions = [
        "What do students say about Professor Ye Cai's exams in FNCE121?",
        "Is there anything my documents don't cover, like parking on campus?",
    ]
    for q in test_questions:
        print(f"\nQ: {q}")
        print("-" * 50)
        result = ask(q)
        print(result["answer"])
        print(f"\nSources: {', '.join(result['sources'])}")
        print()
