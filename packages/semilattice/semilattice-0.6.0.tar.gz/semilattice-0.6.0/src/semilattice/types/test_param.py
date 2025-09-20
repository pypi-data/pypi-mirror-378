# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Literal, Required, TypedDict

from .._types import SequenceNotStr

__all__ = ["TestParam", "QuestionOptions"]


class QuestionOptions(TypedDict, total=False):
    question_type: Required[Literal["single-choice", "multiple-choice"]]
    """Type of question: one of 'single-choice' or 'multiple-choice'"""

    limit: Optional[int]
    """Maximum number of choices or responses to allow for multiple-choice questions"""


class TestParam(TypedDict, total=False):
    ground_answer_counts: Required[Dict[str, int]]
    """Ground-truth answer counts used for test predictions"""

    ground_answer_sample_size: Required[int]
    """Sample size of population behind ground_answer_counts."""

    question: Required[str]
    """Text of the question"""

    question_options: Required[QuestionOptions]
    """Per-question parameters (question type, limits, etc.)"""

    answer_options: Optional[SequenceNotStr[str]]
    """
    Possible answers presented to the simulation model (required for
    single-/multiple-choice questions).
    """
