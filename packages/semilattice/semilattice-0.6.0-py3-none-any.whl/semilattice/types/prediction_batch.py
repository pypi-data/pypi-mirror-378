# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import date, datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["PredictionBatch", "Data", "DataBatch", "DataPrediction", "Error"]


class DataBatch(BaseModel):
    id: str

    batch_type: Literal["prediction", "test", "test_loocv"]
    """
    Either 'prediction', meaning a set of new predictions; 'test' meaning a set of
    test predictions with known ground truth; or 'test_loocv' for leave one out
    cross-validation testing on the population model
    """

    created_at: datetime
    """Batch creation timestamp"""

    name: str
    """Name of the batch run"""

    public: bool
    """Whether the population is public"""

    status: str
    """Current status of the batch"""

    data_source: Optional[str] = None
    """Where the data comes from"""

    description: Optional[str] = None
    """Optional description"""

    effective_date: Optional[date] = None
    """The date when this data was sourced in reality"""

    population: Optional[str] = None
    """ID of the population model this batch will simulate"""

    prediction_finished_at: Optional[datetime] = None
    """When batch prediction finished"""

    prediction_started_at: Optional[datetime] = None
    """When batch prediction began"""

    simulation_engine: Optional[str] = None
    """Simulation engine this population model will use"""


class DataPrediction(BaseModel):
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


class Data(BaseModel):
    batch: DataBatch
    """Batches model data:"""

    predictions: List[DataPrediction]


class Error(BaseModel):
    code: str
    """Machine-readable error code"""

    message: str
    """Human-readable error message"""


class PredictionBatch(BaseModel):
    data: Optional[Data] = None
    """The primary response payload. Contains the result of the request if successful."""

    errors: Optional[List[Error]] = None
    """List of structured error messages, if any occurred during the request."""
