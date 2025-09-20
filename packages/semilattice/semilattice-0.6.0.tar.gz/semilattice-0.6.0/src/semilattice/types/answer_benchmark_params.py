# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from datetime import date
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo
from .test_param import TestParam

__all__ = ["AnswerBenchmarkParams", "Answers", "Batch"]


class AnswerBenchmarkParams(TypedDict, total=False):
    answers: Required[Answers]
    """One or more population answers to simulate.

    A single object is accepted for convenience.
    """

    population_id: Required[str]
    """ID of the population model against which to run the simulation"""

    batch: Optional[Batch]
    """Optional batch details to apply to these predictions.

    If provided, a batch object will be created.
    """


Answers: TypeAlias = Union[TestParam, Iterable[TestParam]]


class Batch(TypedDict, total=False):
    name: Required[str]
    """Name of the batch run"""

    description: Optional[str]
    """Optional description"""

    effective_date: Annotated[Union[str, date, None], PropertyInfo(format="iso8601")]
    """The date when this data was sourced in reality"""
