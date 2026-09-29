def route_query(question: str) -> str:
    """
    Route a user query before running the expensive RAG pipeline.

    Returns:
        greeting       -> casual conversation
        knowledge      -> enterprise knowledge-base question
        out_of_scope   -> clearly unrelated request
    """

    query = question.strip().lower()

    if not query:
        return "out_of_scope"

    greeting_patterns = [
    "hi",
    "hello",
    "hey",
    "hey there",
    "hi there",
    "hello there",
    "good morning",
    "good afternoon",
    "good evening",
    "thanks",
    "thank you",
    "bye",
    "goodbye",
    ]

    if query in greeting_patterns:
        return "greeting"

    out_of_scope_patterns = [
        "programming language",
        "write code",
        "python code",
        "javascript code",
        "solve this coding",
        "stock price",
        "weather",
        "sports score",
        "movie recommendation",
    ]

    if any(pattern in query for pattern in out_of_scope_patterns):
        return "out_of_scope"

    return "knowledge"