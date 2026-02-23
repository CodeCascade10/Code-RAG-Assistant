from app.core.pipeline import handle_query

query = "Explain inheritance in C++ with example"

answer = handle_query(query)

print("\nFinal Answer:\n")
print(answer)