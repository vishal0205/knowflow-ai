import json
from pathlib import Path
from app.rag.retriever import search_documents
from app.rag.hybrid_search import (
    bm25_search,
    reciprocal_rank_fusion,
)
from app.rag.reranker import rerank_documents
from app.rag.embeddings import get_embedding_model


DATASET_PATH = Path("evals/dataset.json")


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def retrieve(question: str, top_k: int = 5):
    # Vector retrieval
    vector_results = search_documents(
        question,
        k=10,
    )

    # BM25 retrieval over full corpus
    bm25_results = bm25_search(
        question,
        k=10,
    )

    # RRF
    hybrid_results = reciprocal_rank_fusion(
        vector_results,
        bm25_results,
    )

    # Reranking
    reranked_results = rerank_documents(
        question,
        hybrid_results,
        top_k=top_k,
    )

    return reranked_results


def evaluate():
    dataset = load_dataset()

    total_answerable = 0
    retrieval_hits = 0

    reciprocal_ranks = []

    abstention_total = 0
    abstention_correct = 0

    print("\n" + "=" * 80)
    print("KNOWFLOW RETRIEVAL EVALUATION")
    print("=" * 80)

    for item in dataset:

        question = item["question"]
        expected_source = item["expected_source"]
        answerable = item["answerable"]

        results = retrieve(question, top_k=5)

        sources = [
            Path(document.source).name
            for document, _ in results
        ]

        print("\n" + "-" * 80)
        print("Question:", question)
        print("Expected:", expected_source)
        print("Retrieved:", sources)

        # Answerable questions
        if answerable:

            total_answerable += 1

            if expected_source in sources:
                retrieval_hits += 1

                rank = sources.index(expected_source) + 1

                reciprocal_ranks.append(
                    1 / rank
                )

                print(
                    f"✓ HIT — rank {rank}"
                )

            else:
                reciprocal_ranks.append(0)

                print("✗ MISS")

        # Unanswerable questions
        else:

            abstention_total += 1

            if not results:
                abstention_correct += 1
                print("✓ Correct abstention")

            else:
                best_score = float(results[0][1])

                if best_score < 0:
                    abstention_correct += 1
                    print(
                        f"✓ Correct abstention "
                        f"(best score: {best_score:.2f})"
                    )
                else:
                    print(
                        f"✗ False retrieval "
                        f"(best score: {best_score:.2f})"
                    )

    recall_at_5 = (
        retrieval_hits / total_answerable
        if total_answerable
        else 0
    )

    mrr = (
        sum(reciprocal_ranks)
        / len(reciprocal_ranks)
        if reciprocal_ranks
        else 0
    )

    abstention_accuracy = (
        abstention_correct / abstention_total
        if abstention_total
        else 0
    )

    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    print(
        f"Recall@5:           {recall_at_5:.2%}"
    )

    print(
        f"MRR:                {mrr:.3f}"
    )

    print(
        f"Abstention accuracy: {abstention_accuracy:.2%}"
    )

    print("=" * 80)


if __name__ == "__main__":
    evaluate()