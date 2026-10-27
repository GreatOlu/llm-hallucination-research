import hashlib
import json
from pathlib import Path

import torch
from sentence_transformers import SentenceTransformer, util



MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_BASE_PATH = (
    PROJECT_ROOT / "data/processed/knowledge_base.json"
)

EMBEDDINGS_DIR = PROJECT_ROOT / "data/processed/embeddings"

EMBEDDINGS_PATH = EMBEDDINGS_DIR / "passage_embeddings.pt"


class SemanticRetriever:
    def __init__(self):
        print("Loading embedding model...")
        self.model = SentenceTransformer(MODEL_NAME)

        print("Loading knowledge base...")
        with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as file:
            self.documents = json.load(file)

        passages = [
            document["context"]
            for document in self.documents
        ]

        # Identify the exact corpus and model used to build the cache.
        corpus_signature = hashlib.sha256(
            json.dumps(
                {
                    "model": MODEL_NAME,
                    "documents": [
                        {
                            "document_id": document["document_id"],
                            "context": document["context"]
                        }
                        for document in self.documents
                    ]
                },
                sort_keys=True
            ).encode("utf-8")
        ).hexdigest()

        EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

        if EMBEDDINGS_PATH.exists():
            cache = torch.load(
                EMBEDDINGS_PATH,
                map_location="cpu",
                weights_only=True
            )

            if cache["signature"] == corpus_signature:
                print("Loading cached passage embeddings...")
                self.passage_embeddings = cache["embeddings"]
            else:
                print("Corpus or model changed. Regenerating embeddings...")
                self.passage_embeddings = self.model.encode(
                    passages,
                    convert_to_tensor=True,
                    show_progress_bar=True
                )

                torch.save(
                    {
                        "signature": corpus_signature,
                        "embeddings": self.passage_embeddings.cpu()
                    },
                    EMBEDDINGS_PATH
                )

        else:
            print("Generating passage embeddings...")
            self.passage_embeddings = self.model.encode(
                passages,
                convert_to_tensor=True,
                show_progress_bar=True
            )

            torch.save(
                {
                    "signature": corpus_signature,
                    "embeddings": self.passage_embeddings.cpu()
                },
                EMBEDDINGS_PATH
            )

        print(f"Retriever ready with {len(self.documents)} passages.")

    def retrieve(self, question, top_k=10):
        question_embedding = self.model.encode(
            question,
            convert_to_tensor=True
        ).cpu()

        similarities = util.cos_sim(
            question_embedding,
            self.passage_embeddings.cpu()
        )[0]

        top_results = similarities.topk(
            k=min(top_k, len(self.documents))
        )

        results = []

        for score, index in zip(
            top_results.values.tolist(),
            top_results.indices.tolist()
        ):
            document = self.documents[index]

            results.append({
                "document_id": document["document_id"],
                "title": document["title"],
                "context": document["context"],
                "similarity_score": round(score, 4)
            })

        return results


def main():
    retriever = SemanticRetriever()

    question = "When did geologists stop using isotopes?"

    results = retriever.retrieve(question, top_k=10)

    print(f"\nQuestion: {question}")
    print("\nTop 10 retrieved passages:")

    for rank, result in enumerate(results, start=1):
        print(
            f"\nRank {rank} | "
            f"{result['document_id']} | "
            f"{result['title']} | "
            f"Score: {result['similarity_score']}"
        )

        print(result["context"])


if __name__ == "__main__":
    main()