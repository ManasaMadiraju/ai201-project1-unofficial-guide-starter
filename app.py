"""
Milestone 5: Gradio web interface for the SCU Unofficial Guide.
Stretch 3: Category filter dropdown (metadata filtering).
Stretch 4: Conversational memory via gr.Chatbot with persistent history.

Run with:
    python app.py
Then open http://localhost:7860 in your browser.
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
    ["What do students say about Professor Ye Cai's exams?", "All topics"],
    ["Which freshman dorm is best for quiet studying?", "Housing"],
    ["How do SCU dining points work and what happens to unused points?", "Dining"],
    ["What are the concerns about the SimplyOasis allergen station?", "Dining"],
    ["What do students say about Professor Stephen Carroll's grading?", "Professor reviews"],
]


def chat(message: str, category_label: str, history: list):
    """
    Handle one turn of the conversation.

    history is Gradio's native list of [user_msg, assistant_msg] pairs.
    We convert it to the {"role", "content"} format for query.py.
    """
    category = CATEGORIES.get(category_label)

    # Convert Gradio history format → OpenAI message format
    groq_history = []
    for user_msg, assistant_msg in history:
        groq_history.append({"role": "user", "content": user_msg})
        if assistant_msg:
            groq_history.append({"role": "assistant", "content": assistant_msg})

    result = ask(message, category=category, history=groq_history)

    sources_text = "Retrieved from:\n" + "\n".join(f"• {s}" for s in result["sources"])
    full_answer = result["answer"] + "\n\n" + sources_text

    history.append((message, full_answer))
    return "", history


with gr.Blocks(title="SCU Unofficial Guide") as demo:
    gr.Markdown(
        """# SCU Unofficial Guide
Ask anything about Santa Clara University — professors, dining, housing, and campus life.
Answers are grounded in real student reviews and community documents. You can ask follow-up questions and the guide will remember the conversation.
"""
    )

    with gr.Row():
        category_dropdown = gr.Dropdown(
            choices=list(CATEGORIES.keys()),
            value="All topics",
            label="Filter by topic (optional)",
            scale=1,
        )

    chatbot = gr.Chatbot(label="Conversation", height=450)

    with gr.Row():
        message_input = gr.Textbox(
            placeholder="e.g. Which CS professor gives the most useful feedback?",
            label="Your question",
            scale=4,
        )
        send_btn = gr.Button("Ask", variant="primary", scale=1)

    gr.Examples(
        examples=EXAMPLES,
        inputs=[message_input, category_dropdown],
        label="Example questions",
    )

    clear_btn = gr.Button("Clear conversation", size="sm")

    send_btn.click(
        fn=chat,
        inputs=[message_input, category_dropdown, chatbot],
        outputs=[message_input, chatbot],
    )
    message_input.submit(
        fn=chat,
        inputs=[message_input, category_dropdown, chatbot],
        outputs=[message_input, chatbot],
    )
    clear_btn.click(lambda: ([], ""), outputs=[chatbot, message_input])


if __name__ == "__main__":
    demo.launch(server_port=7860)
