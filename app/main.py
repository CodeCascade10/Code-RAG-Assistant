from fastapi import FastAPI
from pydantic import BaseModel
from app.core.pipeline import handle_query

app = FastAPI()


class QueryRequest(BaseModel):
    query: str


@app.get("/")
def root():
    return {"message": "Code RAG Backend Running"}


@app.post("/ask")
def ask_question(request: QueryRequest):
    answer = handle_query(request.query)
    return {"answer": answer}