import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi


PROJECT_ROOT = Path(__file__).resolve().parents[2]

KNOWLEDGE_BASE_PATH = (
    PROJECT_ROOT / "data/processed/knowledge_base.json"
)


def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())


class BM25Retriever:
    def __init__(self):
        print("Loading knowledge base for BM25...")

        with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as file:
            self.documents = json.load(file)

        tokenized_passages = [
            tokenize(document["context"])
            for document in self.documents
        ]

        self.bm25 = BM25Okapi(tokenized_passages)

        print(f"BM25 ready with {len(self.documents)} passages.")

    def retrieve(self, question, top_k=10):
        query_tokens = tokenize(question)

        scores = self.bm25.get_scores(query_tokens)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: (-scores[index], index)
        )

        results = []

        for index in ranked_indices[:top_k]:
            document = self.documents[index]

            results.append({
                "document_id": document["document_id"],
                "title": document["title"],
                "context": document["context"],
                "bm25_score": round(float(scores[index]), 4)
            })

        return results


def main():
    retriever = BM25Retriever()

    question = "When did geologists stop using isotopes?"

    results = retriever.retrieve(question)

    print(f"\nQuestion: {question}")

    for rank, result in enumerate(results, start=1):
        print(
            f"\nRank {rank} | "
            f"{result['document_id']} | "
            f"{result['title']} | "
            f"BM25 Score: {result['bm25_score']}"
        )

        print(result["context"])


if __name__ == "__main__":
    main()