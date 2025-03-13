from pydantic import BaseModel


class QueryPrompt(BaseModel):
    prompt: str


class GeneratedQuery(BaseModel):
    query: str
    confidence: float
