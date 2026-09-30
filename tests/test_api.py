from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert "KnowFlow AI" in response.json()["message"]


def test_query_returns_answer_and_sources(monkeypatch):
    captured = {}

    def fake_answer_question(question, department, access_level):
        captured.update(
            question=question, department=department, access_level=access_level
        )
        return {
            "question": question,
            "answer": "Three days per week [1].",
            "sources": [{"citation": "[1]", "source": "remote_work_policy.pdf"}],
        }

    monkeypatch.setattr(main, "answer_question", fake_answer_question)

    response = client.post(
        "/query",
        json={"question": "How many remote days?", "department": "general"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Three days per week [1]."
    assert body["sources"][0]["citation"] == "[1]"
    # access_level defaults to "employee" when the client does not send it
    assert captured["access_level"] == "employee"
    assert captured["department"] == "general"


def test_query_without_question_is_rejected():
    response = client.post("/query", json={})

    assert response.status_code == 422
