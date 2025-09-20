# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .answer_response import AnswerResponse

__all__ = ["AnswerGetResponse", "Error"]


class Error(BaseModel):
    code: str
    """Machine-readable error code"""

    message: str
    """Human-readable error message"""


class AnswerGetResponse(BaseModel):
    data: Optional[AnswerResponse] = None
    """
    We define this to maintain backwards compatibility pre API v1.1.0 / SDK v0.6.0
    This class is inherited by the TestsResponse as that needs all the computed,
    renamed evals PredictionsResponse does not inherit this class because you can't
    exclude the computed evals
    """

    errors: Optional[List[Error]] = None
    """List of structured error messages, if any occurred during the request."""
