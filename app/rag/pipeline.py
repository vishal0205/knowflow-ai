
import time

from app.rag.hybrid_search import hybrid_search
from app.rag.reranker import rerank_documents
from app.rag.llm import generate_answer
from app.observability.logger import log_query
from app.rag.query_router import route_query


ABSTENTION_ANSWER = (
    "I don't have enough information in the provided documents to answer that."
)
LLM_ERROR_ANSWER = (
    "I'm unable to generate an answer right now. Please try again later."
)


def answer_question(
    question: str,
    department: str | None = None,
    access_level: str | None = None,
    top_k: int = 5,
):
    start_time = time.perf_counter()
    route = route_query(question)

    if route == "greeting":
        answer = (
            "Hello! I can help you find information in the organization's "
            "knowledge base."
        )
        log_query(
            question=question,
            department=department,
            access_level=access_level,
            sources=[],
            latency_ms=(time.perf_counter() - start_time) * 1000,
            abstained=False,
        )
        return {
            "question": question,
            "answer": answer,
            "sources": [],
            "retrieved_contexts": [],
            "abstained": False,
        }

    if route == "out_of_scope":
        answer = (
            "I can only answer questions based on the organization's "
            "knowledge base."
        )
        log_query(
            question=question,
            department=department,
            access_level=access_level,
            sources=[],
            latency_ms=(time.perf_counter() - start_time) * 1000,
            abstained=True,
        )
        return {
            "question": question,
            "answer": answer,
            "sources": [],
            "retrieved_contexts": [],
            "abstained": True,
        }

    # 1. Permission-aware hybrid retrieval
    hybrid_results = hybrid_search(
        question,
        k=10,
        department=department,
        access_level=access_level,
    )

    # 2. Reranking
    reranked_results = rerank_documents(
        question,
        hybrid_results,
        top_k=top_k,
    )
    reranked_results = [
        (document, score)
        for document, score in reranked_results
        if float(score) > 0
    ]

    # 3. Abstain if no positive-scoring candidates remain
    if not reranked_results:
        log_query(
            question=question,
            department=department,
            access_level=access_level,
            sources=[],
            latency_ms=(time.perf_counter() - start_time) * 1000,
            abstained=True,
        )
        return {
            "question": question,
            "answer": ABSTENTION_ANSWER,
            "sources": [],
            "retrieved_contexts": [],
            "abstained": True,
        }

    # 4. Build citation-aware context
    context_parts = []
    sources = []

    for index, (document, score) in enumerate(reranked_results, start=1):
        citation_id = f"[{index}]"

        context_parts.append(
            f"""
{citation_id}
Source: {document.source}
Page: {document.page}
Content:
{document.content}
"""
        )

        sources.append(
            {
                "citation": citation_id,
                "source": document.source,
                "page": document.page,
                "score": float(score),
            }
        )

    context = "\n\n---\n\n".join(context_parts)

    # 5. Generate answer safely
    try:
        answer = generate_answer(question, context)
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("The LLM returned an empty answer.")
    except Exception:
        log_query(
            question=question,
            department=department,
            access_level=access_level,
            sources=[],
            latency_ms=(time.perf_counter() - start_time) * 1000,
            abstained=True,
        )
        return {
            "question": question,
            "answer": LLM_ERROR_ANSWER,
            "sources": [],
            "retrieved_contexts": [],
            "abstained": True,
            "error": "llm_unavailable",
        }

    # 6. Log successful generation
    log_query(
        question=question,
        department=department,
        access_level=access_level,
        sources=sources,
        latency_ms=(time.perf_counter() - start_time) * 1000,
        abstained=False,
    )

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "retrieved_contexts": [
            document.content for document, _ in reranked_results
        ],
        "abstained": False,
    }
