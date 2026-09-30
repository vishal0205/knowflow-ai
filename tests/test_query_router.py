import pytest

from app.rag.query_router import route_query


@pytest.mark.parametrize(
    "text",
    ["hi", "Hello", "  hey there  ", "Good Morning", "thanks", "bye"],
)
def test_greetings_are_routed_as_greeting(text):
    assert route_query(text) == "greeting"


@pytest.mark.parametrize(
    "text",
    [
        "What is the weather today?",
        "Write code for a login page",
        "what is the stock price of Apple",
    ],
)
def test_unrelated_requests_are_out_of_scope(text):
    assert route_query(text) == "out_of_scope"


@pytest.mark.parametrize("text", ["", "   "])
def test_empty_question_is_out_of_scope(text):
    assert route_query(text) == "out_of_scope"


@pytest.mark.parametrize(
    "text",
    [
        "How many days can employees work remotely?",
        "What is the leave policy?",
    ],
)
def test_company_questions_go_to_knowledge_pipeline(text):
    assert route_query(text) == "knowledge"


@pytest.mark.xfail(
    reason="Known limitation: keyword router misroutes this company question",
    strict=False,
)
def test_company_question_containing_python_code_is_not_blocked():
    assert route_query("What is our Python code review policy?") == "knowledge"
