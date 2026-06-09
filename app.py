"""
Milestone 5: Gradio web interface for the SCU Unofficial Guide.

Run with:
    python app.py
Then open http://localhost:7860 in your browser.
"""

import gradio as gr
from query import ask

EXAMPLES = [
    "What do students say about Professor Ye Cai's exams?",
    "Which freshman dorm is best for quiet studying?",
    "How do SCU dining points work and what happens to unused points?",
    "What are the concerns about the SimplyOasis allergen station?",
    "What do students say about Professor Stephen Carroll's grading?",
]


def handle_query(question: str):
    if not question.strip():
        return "Please enter a question.", ""

    result = ask(question)
    sources_text = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources_text


with gr.Blocks(title="SCU Unofficial Guide") as demo:
    gr.Markdown(
        """# SCU Unofficial Guide
Ask questions about Santa Clara University professors, dining, housing, and campus life.
Answers are grounded in real student reviews and community documents.
"""
    )

    with gr.Row():
        with gr.Column(scale=3):
            question_input = gr.Textbox(
                label="Your question",
                placeholder="e.g. Which CS professor gives the most useful feedback?",
                lines=2,
            )
            ask_btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        answer_output = gr.Textbox(label="Answer", lines=10, interactive=False)

    with gr.Row():
        sources_output = gr.Textbox(
            label="Retrieved from", lines=4, interactive=False
        )

    gr.Examples(
        examples=EXAMPLES,
        inputs=question_input,
        label="Example questions",
    )

    ask_btn.click(
        fn=handle_query,
        inputs=question_input,
        outputs=[answer_output, sources_output],
    )
    question_input.submit(
        fn=handle_query,
        inputs=question_input,
        outputs=[answer_output, sources_output],
    )

if __name__ == "__main__":
    demo.launch(server_port=7860)
