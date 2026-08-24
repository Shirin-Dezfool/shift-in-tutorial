"""Request/response models."""

from pydantic import BaseModel


class CreateLinkRequest(BaseModel):
    url: str


class LinkResponse(BaseModel):
    code: str
    url: str
    clicks: int

    @classmethod
    def from_record(cls, record: "object") -> "LinkResponse":
        return cls(code=record.code, url=record.url, clicks=record.clicks)
