# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from datetime import date
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo
from .test_param import TestParam

__all__ = ["TestCreateParams", "Tests", "Batch"]


class TestCreateParams(TypedDict, total=False):
    population_id: Required[str]
    """ID of the population model against which to run the simulation"""

    tests: Required[Tests]
    """One or more test predictions to run."""

    batch: Optional[Batch]
    """Optional batch details to apply to these predictions.

    If provided, a batch object will be created.
    """


Tests: TypeAlias = Union[TestParam, Iterable[TestParam]]


class Batch(TypedDict, total=False):
    name: Required[str]
    """Name of the batch run"""

    description: Optional[str]
    """Optional description"""

    effective_date: Annotated[Union[str, date, None], PropertyInfo(format="iso8601")]
    """The date when this data was sourced in reality"""
