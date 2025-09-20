# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["PredictionResponse", "Data", "Error"]


class Data(BaseModel):
    id: str
    """Question ID"""

    created_at: datetime
    """When the question was created"""

    population: str
    """Population ID"""

    population_name: str
    """Name of the population"""

    predicted_answer_percentages: Union[Dict[str, object], object, None] = None
    """Predicted answer percentages keyed by answer option"""

    question: str
    """Full text of the question"""

    simulated_answer_percentages: Union[Dict[str, object], object, None] = None
    """Simulated answer percentages keyed by answer option"""

    status: str
    """Current status"""

    answer_options: Optional[List[object]] = None
    """Answer options presented to the model (single/ multi-choice)"""

    batch: Optional[str] = None
    """ID shared by all tests or predictions in a batch run"""

    prediction_finished_at: Optional[datetime] = None
    """When prediction finished"""

    prediction_started_at: Optional[datetime] = None
    """When prediction began"""

    public: Optional[bool] = None
    """If the question is public"""

    question_options: Union[Dict[str, object], object, None] = None
    """
    Per-question configuration - see SimulationQuestionOptions and
    PopulationQuestionOptions schemas
    """

    simulation_engine: Optional[str] = None
    """Engine used (e.g. answers-1)"""


class Error(BaseModel):
    code: str
    """Machine-readable error code"""

    message: str
    """Human-readable error message"""


class PredictionResponse(BaseModel):
    data: Optional[Data] = None
    """The primary response payload. Contains the result of the request if successful."""

    errors: Optional[List[Error]] = None
    """List of structured error messages, if any occurred during the request."""
