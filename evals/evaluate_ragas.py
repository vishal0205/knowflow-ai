import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from ragas import SingleTurnSample
from ragas.metrics import Faithfulness, ResponseRelevancy
from ragas.embeddings import LangchainEmbeddingsWrapper

from app.rag.embeddings import get_embedding_model
from app.rag.pipeline import answer_question

load_dotenv()

DATASET_PATH = Path("evals/dataset.json")


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


async def evaluate_sample(
    item,
    evaluator_llm,
    embedding_model,
):
    question = item["question"]
    ground_truth = item["ground_truth"]

    print(f"\nEvaluating: {question}")

    result = answer_question(question)
    answer = result["answer"]

    # Skip unanswerable questions for these two RAGAS metrics.
    if not item["answerable"]:
        return None

    sample = SingleTurnSample(
        user_input=question,
        response=answer,
        reference=ground_truth,
        retrieved_contexts=result["retrieved_contexts"],
    )

    faithfulness = Faithfulness(
        llm=evaluator_llm,
    )

    relevancy = ResponseRelevancy(
    llm=evaluator_llm,
    embeddings=embedding_model,
    strictness=1,
    )

    print("  → Starting Faithfulness evaluation...")

    faithfulness_score = await faithfulness.single_turn_ascore(sample)

    print(f"  → Faithfulness complete: {faithfulness_score:.4f}")

    print("  → Starting Answer Relevancy evaluation...")

    relevancy_score = await relevancy.single_turn_ascore(sample)

    print(f"  → Answer Relevancy complete: {relevancy_score:.4f}")
    return {
        "question": question,
        "faithfulness": float(faithfulness_score),
        "answer_relevancy": float(relevancy_score),
    }


async def main():
    dataset = load_dataset()

    # ---------------------------------------------------------
    # Groq is used ONLY as the RAGAS evaluator.
    # Gemini remains the actual KnowFlow generation model.
    # ---------------------------------------------------------
    evaluator_llm = ChatGroq(
        model="openai/gpt-oss-20b",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
    )

    # Reuse KnowFlow's existing embedding model.
    embedding_model = LangchainEmbeddingsWrapper(
        get_embedding_model()
    )

    results = []

    for item in dataset:
        result = await evaluate_sample(
            item,
            evaluator_llm,
            embedding_model,
        )

        if result is not None:
            results.append(result)

    if not results:
        print("\nNo answerable questions found.")
        return

    # ---------------------------------------------------------
    # Calculate averages
    # ---------------------------------------------------------
    avg_faithfulness = sum(
        result["faithfulness"] for result in results
    ) / len(results)

    avg_relevancy = sum(
        result["answer_relevancy"] for result in results
    ) / len(results)

    # ---------------------------------------------------------
    # Print results
    # ---------------------------------------------------------
    print("\n" + "=" * 60)
    print("RAGAS EVALUATION RESULTS")
    print("=" * 60)

    for result in results:
        print(f"\nQuestion: {result['question']}")
        print(f"Faithfulness: {result['faithfulness']:.4f}")
        print(f"Answer Relevancy: {result['answer_relevancy']:.4f}")

    print("\n" + "-" * 60)
    print(f"Average Faithfulness: {avg_faithfulness:.4f}")
    print(f"Average Answer Relevancy: {avg_relevancy:.4f}")
    print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())