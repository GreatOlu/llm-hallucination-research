import json
from pathlib import Path

from src.retrieval.semantic_search import SemanticRetriever
from src.retrieval.bm25_search import BM25Retriever
from src.retrieval.hybrid_search import HybridRetriever


KNOWLEDGE_BASE_PATH = Path("data/processed/knowledge_base.json")
QUESTIONS_PATH = Path("data/processed/answerable_questions.json")

OUTPUT_DIR = Path("results/retrieval")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

K_VALUES = [1, 5, 10]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_reference_mapping(questions, knowledge_base):
    """
    Match each answerable question to its original
    supporting passage in the knowledge base.
    """

    context_to_ids = {}

    for doc in knowledge_base:
        context_to_ids.setdefault(
            doc["context"], []
        ).append(doc["document_id"])

    reference_mapping = {}

    for question in questions:
        question_id = question["id"]
        context = question["context"]

        matching_ids = context_to_ids.get(context, [])

        if len(matching_ids) != 1:
            raise ValueError(
                f"Question {question_id} matched "
                f"{len(matching_ids)} documents."
            )

        reference_mapping[question_id] = matching_ids[0]

    return reference_mapping


def get_rank(results, reference_doc_id):
    """
    Return the 1-based rank of the reference document.
    Return None if it was not retrieved.
    """

    for rank, result in enumerate(results, start=1):
        if result["document_id"] == reference_doc_id:
            return rank

    return None


def calculate_metrics(records):

    total = len(records)

    metrics = {}

    for method in ["semantic", "bm25", "hybrid"]:

        metrics[method] = {}

        for k in K_VALUES:

            hits = sum(
                1
                for record in records
                if record[f"{method}_rank"] is not None
                and record[f"{method}_rank"] <= k
            )

            metrics[method][f"recall@{k}"] = hits / total

    combined_hits = sum(
        1
        for record in records
        if (
            record["semantic_rank"] is not None
            or record["bm25_rank"] is not None
        )
    )

    metrics["combined_top10_coverage"] = combined_hits / total

    return metrics


def main():

    questions = load_json(QUESTIONS_PATH)
    knowledge_base = load_json(KNOWLEDGE_BASE_PATH)

    print(f"Loaded {len(questions)} questions")
    print(f"Loaded {len(knowledge_base)} passages")

    reference_mapping = build_reference_mapping(
        questions,
        knowledge_base
    )

    print(
        f"Verified {len(reference_mapping)} "
        "reference-document mappings"
    )

    semantic_retriever = SemanticRetriever()
    bm25_retriever = BM25Retriever()
    hybrid_retriever = HybridRetriever(
        rrf_k=60,
        candidate_k=10
    )

    records = []

    for index, question in enumerate(questions, start=1):

        question_id = question["id"]
        question_text = question["question"]

        reference_doc_id = reference_mapping[question_id]

        semantic_results = semantic_retriever.retrieve(
            question_text,
            top_k=10
        )

        bm25_results = bm25_retriever.retrieve(
            question_text,
            top_k=10
        )

        hybrid_results = hybrid_retriever.retrieve(
            question_text,
            top_k=10
        )

        semantic_rank = get_rank(
            semantic_results,
            reference_doc_id
        )

        bm25_rank = get_rank(
            bm25_results,
            reference_doc_id
        )

        hybrid_rank = get_rank(
            hybrid_results,
            reference_doc_id
        )

        records.append({
            "question_id": question_id,
            "question": question_text,
            "reference_document_id": reference_doc_id,
            "semantic_rank": semantic_rank,
            "bm25_rank": bm25_rank,
            "hybrid_rank": hybrid_rank
        })

        if index % 25 == 0:
            print(f"Evaluated {index}/{len(questions)} questions")

    metrics = calculate_metrics(records)

    with open(
        OUTPUT_DIR / "retrieval_results.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(records, f, indent=2)

    with open(
        OUTPUT_DIR / "retrieval_metrics.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(metrics, f, indent=2)

    print("\nRETRIEVAL EVALUATION RESULTS")
    print("=" * 40)

    for method in ["semantic", "bm25", "hybrid"]:

        print(f"\n{method.upper()}")

        for metric, value in metrics[method].items():
            print(f"{metric}: {value:.2%}")

    print(
        "\nCombined top-10 coverage:",
        f"{metrics['combined_top10_coverage']:.2%}"
    )


if __name__ == "__main__":
    main()