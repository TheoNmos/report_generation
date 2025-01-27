from pydantic import BaseModel


class QueryPrompt(BaseModel):
    prompt: str
