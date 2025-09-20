# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .answer_response import AnswerResponse

__all__ = ["APIResponseListAnswers", "Error"]


class Error(BaseModel):
    code: str
    """Machine-readable error code"""

    message: str
    """Human-readable error message"""


class APIResponseListAnswers(BaseModel):
    data: Optional[List[AnswerResponse]] = None
    """The primary response payload. Contains the result of the request if successful."""

    errors: Optional[List[Error]] = None
    """List of structured error messages, if any occurred during the request."""
