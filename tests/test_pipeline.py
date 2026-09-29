from app.rag.pipeline import answer_question


question = "What is the company's stock option policy?"

result = answer_question(question)


print("\n" + "=" * 70)
print("QUESTION")
print("=" * 70)

print(result["question"])


print("\n" + "=" * 70)
print("ANSWER")
print("=" * 70)

print(result["answer"])


print("\n" + "=" * 70)
print("SOURCES")
print("=" * 70)

for source in result["sources"]:
    print(source)