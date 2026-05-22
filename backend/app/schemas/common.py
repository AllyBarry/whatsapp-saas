"""Shared response envelopes."""
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class DataResponse(BaseModel, Generic[T]):
    """Success envelope: {"success": true, "data": ...}."""

    success: bool = True
    data: T


def ok(data: T) -> dict:
    return {"success": True, "data": data}
