# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import date, datetime

from .._models import BaseModel

__all__ = ["PopulationResponse", "Data", "Error"]


class Data(BaseModel):
    id: str
    """Unique identifier for the population"""

    average_accuracy: Optional[float] = None
    """Average accuracy for this population model.

    Calculated as the mean average inverse mean absolute error (1 - MAE) for all
    test predictions
    """

    average_normalised_information_loss: Optional[float] = None
    """Average normalised information loss for this population model.

    Calculated as the normalised Kullback-Leibler (KL) divergence (entropy) between
    predicted and ground truth answer distributions for all test predictions.
    """

    average_squared_error: Optional[float] = None
    """Average squared error for this population model.

    Calculated as the mean average root mean squared error (RMSE) for all test
    predictions
    """

    created_at: datetime
    """Population creation timestamp"""

    name: str
    """Name of the population"""

    public: bool
    """Whether the population is public"""

    question_count: int
    """Total number of questions"""

    simulacrum_count: int
    """Total number of simulacra"""

    status: str
    """Current status of the population"""

    data_source: Optional[str] = None
    """Where the data comes from"""

    description: Optional[str] = None
    """Optional description"""

    effective_date: Optional[date] = None
    """The date when this data was sourced in reality"""

    reality_target: Optional[str] = None
    """Real-world label"""

    simulation_engine: Optional[str] = None
    """Engine used"""

    test_finished_at: Optional[datetime] = None
    """Benchmark finished"""

    test_started_at: Optional[datetime] = None
    """Benchmark started"""

    upload_filename: Optional[str] = None
    """Original CSV filename"""


class Error(BaseModel):
    code: str
    """Machine-readable error code"""

    message: str
    """Human-readable error message"""


class PopulationResponse(BaseModel):
    data: Optional[Data] = None
    """Population"""

    errors: Optional[List[Error]] = None
    """List of structured error messages, if any occurred during the request."""
