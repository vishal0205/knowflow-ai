from fastapi import FastAPI

from app.models import QueryRequest, QueryResponse
from app.rag.pipeline import answer_question
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="KnowFlow AI",
    description="Enterprise RAG Knowledge Assistant",
    version="0.2.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "KnowFlow AI is running",
        "version": "0.2.0",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    result = answer_question(
        question=request.question,
        department=request.department,
        access_level=request.access_level,
    )

    return {
        "question": result["question"],
        "answer": result["answer"],
        "sources": result["sources"],
    }