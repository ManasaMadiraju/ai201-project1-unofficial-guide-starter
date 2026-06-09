"""
SCU Unofficial Guide — Gradio web interface.
Stretch 3: Category filter (metadata filtering).
Stretch 4: Conversational memory via chat history.

Run with:
    python app.py
Then open http://localhost:7860
"""

import gradio as gr
from query import ask

CATEGORIES = {
    "All topics": None,
    "Professor reviews": "professor_reviews",
    "Dining": "dining",
    "Housing": "housing",
    "Campus life": "campus_life",
}

EXAMPLES = [
    "What do students say about Professor Ye Cai's exams?",
    "Which freshman dorm is best for quiet studying?",
    "How do SCU dining points work and what happens to unused points?",
    "What are the concerns about the SimplyOasis allergen station?",
    "What do students say about Professor Stephen Carroll's grading?",
    "Which professors give the most useful feedback?",
]

CSS = """
body, .gradio-container {
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
}
.gradio-container {
    max-width: 900px !important;
    margin: 0 auto !important;
}
#header {
    background: linear-gradient(135deg, #8C1515 0%, #6B0F0F 100%);
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 20px;
    color: white;
}
#header h1 {
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 6px 0;
    color: white !important;
}
#header p {
    font-size: 0.95rem;
    opacity: 0.88;
    margin: 0;
    color: white !important;
}
#chatbox {
    border-radius: 10px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
}
#send-btn {
    background: #8C1515 !important;
    border-color: #8C1515 !important;
    color: white !important;
    font-weight: 600;
    border-radius: 8px !important;
    height: 46px !important;
}
#send-btn:hover {
    background: #6B0F0F !important;
    border-color: #6B0F0F !important;
}
#clear-btn {
    border-radius: 8px !important;
    height: 36px !important;
    font-size: 0.85rem !important;
}
#filter-row {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 8px;
}
.message.bot {
    background: #fdf6f6 !important;
    border-left: 3px solid #8C1515 !important;
}
#examples-section {
    margin-top: 12px;
}
footer { display: none !important; }
"""

def respond(message: str, history: list, category_label: str):
    """
    Handle one conversation turn.
    history: Gradio 6 format — list of dicts {"role": "user"/"assistant", "content": str}
    """
    if not message.strip():
        yield history
        return

    category = CATEGORIES.get(category_label)

    # Build Groq-compatible history (exclude the current message — it's added below)
    groq_history = [
        {"role": m["role"], "content": m["content"]}
        for m in history
    ]

    try:
        result = ask(message, category=category, history=groq_history)
        sources_text = "\n\n**Retrieved from:** " + " · ".join(
            f"`{s}`" for s in result["sources"]
        )
        full_answer = result["answer"] + sources_text
    except Exception as e:
        full_answer = f"Something went wrong: {e}\n\nPlease make sure the vector store is built (`python embed.py`) and your `.env` has a valid GROQ_API_KEY."

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": full_answer})
    yield history


with gr.Blocks(title="SCU Unofficial Guide") as demo:

    # ── Header ──────────────────────────────────────────────────────────
    gr.HTML("""
        <div id="header">
            <h1>🎓 SCU Unofficial Guide</h1>
            <p>Ask anything about Santa Clara University — professors, dining, housing, and campus life.<br>
            Answers are grounded in real student reviews. Ask follow-up questions; the guide remembers your conversation.</p>
        </div>
    """)

    # ── Filter row ───────────────────────────────────────────────────────
    with gr.Group(elem_id="filter-row"):
        with gr.Row():
            category_dropdown = gr.Dropdown(
                choices=list(CATEGORIES.keys()),
                value="All topics",
                label="Filter by topic",
                info="Restrict answers to a specific area",
                scale=1,
                min_width=220,
            )
            gr.Markdown(
                """<div style='font-size:0.85rem; color:#6b7280; padding-top:8px'>
                Filter searches only that category of documents.<br>
                Leave as <b>All topics</b> for cross-category questions.
                </div>""",
                scale=3,
            )

    # ── Chatbot ──────────────────────────────────────────────────────────
    chatbot = gr.Chatbot(
        label="",
        height=460,
        elem_id="chatbox",
        show_label=False,
        placeholder="<div style='text-align:center; color:#9ca3af; padding:40px 0'>Ask a question about SCU to get started</div>",
    )

    # ── Input row ────────────────────────────────────────────────────────
    with gr.Row():
        message_input = gr.Textbox(
            placeholder="e.g. Which professor gives the best feedback in the CS department?",
            label="",
            show_label=False,
            scale=5,
            lines=1,
            max_lines=3,
            container=False,
        )
        send_btn = gr.Button("Ask →", variant="primary", scale=1, elem_id="send-btn", min_width=90)

    with gr.Row():
        clear_btn = gr.Button("🗑 Clear conversation", size="sm", elem_id="clear-btn")

    # ── Examples ─────────────────────────────────────────────────────────
    with gr.Accordion("Example questions", open=True, elem_id="examples-section"):
        gr.Examples(
            examples=EXAMPLES,
            inputs=message_input,
            label="",
        )

    # ── Event wiring ─────────────────────────────────────────────────────
    send_btn.click(
        fn=respond,
        inputs=[message_input, chatbot, category_dropdown],
        outputs=chatbot,
    ).then(fn=lambda: "", outputs=message_input)

    message_input.submit(
        fn=respond,
        inputs=[message_input, chatbot, category_dropdown],
        outputs=chatbot,
    ).then(fn=lambda: "", outputs=message_input)

    clear_btn.click(fn=lambda: [], outputs=chatbot)


if __name__ == "__main__":
    demo.launch(server_port=7860, css=CSS)
