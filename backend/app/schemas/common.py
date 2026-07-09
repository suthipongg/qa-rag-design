from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


class StatusMessage(BaseModel):
    message: str
