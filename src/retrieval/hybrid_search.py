from src.retrieval.semantic_search import SemanticRetriever
from src.retrieval.bm25_search import BM25Retriever


class HybridRetriever:
    def __init__(self, rrf_k=60, candidate_k=10):
        self.semantic_retriever = SemanticRetriever()
        self.bm25_retriever = BM25Retriever()

        self.rrf_k = rrf_k
        self.candidate_k = candidate_k

    def retrieve(self, question, top_k=10):

        semantic_results = self.semantic_retriever.retrieve(
            question,
            top_k=self.candidate_k
        )

        bm25_results = self.bm25_retriever.retrieve(
            question,
            top_k=self.candidate_k
        )

        scores = {}
        documents = {}

        for results in [semantic_results, bm25_results]:

            for rank, doc in enumerate(results, start=1):

                doc_id = doc["document_id"]

                if doc_id not in scores:
                    scores[doc_id] = 0

                scores[doc_id] += 1 / (self.rrf_k + rank)

                if doc_id not in documents:
                    documents[doc_id] = {
                        "document_id": doc_id,
                        "title": doc["title"],
                        "context": doc["context"]
                    }

        ranked_ids = sorted(
            scores,
            key=lambda doc_id: (-scores[doc_id], doc_id)
        )

        results = []

        for doc_id in ranked_ids[:top_k]:

            result = documents[doc_id].copy()
            result["rrf_score"] = scores[doc_id]

            results.append(result)

        return results