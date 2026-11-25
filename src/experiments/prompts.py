CONDITIONS = [
    "baseline",
    "hallucination_aware",
    "rag",
    "rag_hallucination_aware",
]

HALLUCINATION_AWARE_INSTRUCTION = """
Answer the question only when you have sufficient information.
Do not invent facts or make unsupported claims.
If you are uncertain or cannot determine the answer, respond:
"I don't know."
""".strip()


def build_prompt(question, condition, passages=None):
    if condition not in CONDITIONS:
        raise ValueError(f"Unknown condition: {condition}")

    if condition in ["rag", "rag_hallucination_aware"]:
        if passages is None:
            raise ValueError("RAG conditions require retrieved passages.")

        context = "\n\n".join(
            f"[Document {i + 1}]\n{passage['context']}"
            for i, passage in enumerate(passages)
        )

        prompt = (
            "Use the provided passages to answer the question.\n\n"
            f"Passages:\n{context}\n\n"
            f"Question: {question}\nAnswer:"
        )
    else:
        prompt = f"Question: {question}\nAnswer:"

    if condition in ["hallucination_aware", "rag_hallucination_aware"]:
        prompt = HALLUCINATION_AWARE_INSTRUCTION + "\n\n" + prompt

    return prompt