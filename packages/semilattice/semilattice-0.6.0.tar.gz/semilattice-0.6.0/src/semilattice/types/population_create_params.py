# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from datetime import date
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._types import FileTypes
from .._utils import PropertyInfo

__all__ = ["PopulationCreateParams", "PopulationOptions", "PopulationOptionsQuestionOption"]


class PopulationCreateParams(TypedDict, total=False):
    name: Required[str]
    """Name of the new population"""

    population_options: Required[PopulationOptions]
    """**Important:** the API expects population_options to be sent as JSON string.

    Use json.dumps() to convert your object to string format for multipart/form-data
    requests.
    """

    seed_data: Required[FileTypes]

    data_source: Optional[str]
    """Where the data comes from"""

    description: Optional[str]
    """Optional description for the population"""

    effective_date: Annotated[Union[str, date, None], PropertyInfo(format="iso8601")]
    """The date when this data was sourced in reality"""

    reality_target: Optional[str]
    """Label for the real-world target the population is modeling"""

    run_test: Optional[bool]
    """Whether to run an accuracy test immediately after creation"""

    simulation_engine: str
    """Identifier for the simulation engine to be used"""


class PopulationOptionsQuestionOption(TypedDict, total=False):
    question_number: Required[int]
    """
    The column index number of the question to which the options apply (1-based),
    ignoring the first `sim_id` column
    """

    question_type: Required[Literal["single-choice", "multiple-choice", "open-ended"]]
    """Type of question: one of 'single-choice', 'multiple-choice', or 'open-ended'"""

    limit: Optional[int]
    """
    Maximum number of choices or responses which were allowed for multiple-choice
    questions
    """


class PopulationOptions(TypedDict, total=False):
    question_options: Required[Iterable[PopulationOptionsQuestionOption]]
    """
    Tells API if the columns in the seed data are single-choice, multiple-choice, or
    open-ended.If multiple choice, specifies if it was limited choice (eg. 'up to
    3').This makes sure that test simulations are run correctly when test population
    is run.
    """
