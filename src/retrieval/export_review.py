import csv
import json
from pathlib import Path

from semantic_search import SemanticRetriever
from bm25_search import BM25Retriever


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CANDIDATES_PATH = (
    PROJECT_ROOT / "data/processed/unanswerable_candidates.json"
)

OUTPUT_PATH = (
    PROJECT_ROOT / "data/processed/unanswerable_review.csv"
)

TOP_K = 10


def main():
    if OUTPUT_PATH.exists():
        print(
            "Review CSV already exists. "
            "Delete or rename it before regenerating."
        )
        return

    print("Loading unanswerable candidates...")

    with open(CANDIDATES_PATH, "r", encoding="utf-8") as file:
        candidates = json.load(file)

    semantic_retriever = SemanticRetriever()
    bm25_retriever = BM25Retriever()

    rows = []

    for index, candidate in enumerate(candidates, start=1):
        question_id = candidate["id"]
        question = candidate["question"]

        semantic_results = semantic_retriever.retrieve(
            question,
            top_k=TOP_K
        )

        bm25_results = bm25_retriever.retrieve(
            question,
            top_k=TOP_K
        )

        # Combine results without duplicate passages.
        combined = {}

        for rank, result in enumerate(semantic_results, start=1):
            document_id = result["document_id"]

            combined[document_id] = {
                "document_id": document_id,
                "title": result["title"],
                "passage": result["context"],
                "semantic_rank": rank,
                "bm25_rank": "",
                "similarity_score": result["similarity_score"],
                "bm25_score": ""
            }

        for rank, result in enumerate(bm25_results, start=1):
            document_id = result["document_id"]

            if document_id in combined:
                combined[document_id]["bm25_rank"] = rank
                combined[document_id]["bm25_score"] = (
                    result["bm25_score"]
                )
            else:
                combined[document_id] = {
                    "document_id": document_id,
                    "title": result["title"],
                    "passage": result["context"],
                    "semantic_rank": "",
                    "bm25_rank": rank,
                    "similarity_score": "",
                    "bm25_score": result["bm25_score"]
                }

        # Preserve semantic ranking first, followed by
        # additional BM25-only passages.
        combined_results = list(combined.values())

        for rank, result in enumerate(combined_results, start=1):
            rows.append({
                "candidate_number": index,
                "question_id": question_id,
                "question": question,
                "rank": rank,
                **result,
                "decision": "",
                "notes": ""
            })

        print(
            f"Processed {index}/{len(candidates)} candidates "
            f"({len(combined_results)} unique passages)"
        )

    fieldnames = [
        "candidate_number",
        "question_id",
        "question",
        "rank",
        "document_id",
        "title",
        "passage",
        "semantic_rank",
        "bm25_rank",
        "similarity_score",
        "bm25_score",
        "decision",
        "notes"
    ]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(
        OUTPUT_PATH,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(rows)

    print(f"\nExported {len(rows)} rows to:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()