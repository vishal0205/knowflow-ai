from app.rag.llm import generate_answer


context = """
Employee Handbook 2026

Remote Work Policy

Employees may work remotely up to three days per week,
subject to manager approval.

Employees must maintain a secure working environment
when working remotely.
"""

question = "What is the company's health insurance policy?"

answer = generate_answer(
    question,
    context,
)

print("\nQUESTION:")
print(question)

print("\nANSWER:")
print(answer)