# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["AnswerResponse"]


class AnswerResponse(BaseModel):
    id: str
    """Question ID"""

    accuracy: Optional[float] = None
    """Accuracy for this prediction.

    Calculated as inverse mean absolute error (1 - MAE)
    """

    created_at: datetime
    """When the question was created"""

    information_loss: Optional[float] = None
    """Information loss between predicted and ground-truth distributions.

    Calculated as Kullback-Leibler (KL) divergence (entropy). Cannot be used to
    compare different predictions.
    """

    normalised_information_loss: Optional[float] = None
    """
    Information loss between predicted and ground-truth distributions normalised to
    the number of answer options. Calculated as the normalised Kullback-Leibler (KL)
    divergence (entropy).
    """

    population: str
    """Population ID"""

    population_name: str
    """Name of the population"""

    predicted_answer_percentages: Union[Dict[str, object], object, None] = None
    """Predicted answer percentages keyed by answer option"""

    question: str
    """Full text of the question"""

    root_mean_squared_error: Optional[float] = None
    """Squared error for this prediction. Calculated as root mean squared error (RMSE)"""

    simulated_answer_percentages: Union[Dict[str, object], object, None] = None
    """Simulated answer percentages keyed by answer option"""

    squared_error: Optional[float] = None
    """Squared error for this prediction. Calculated as root mean squared error (RMSE)"""

    status: str
    """Current status"""

    answer_options: Optional[List[object]] = None
    """Answer options presented to the model (single/ multi-choice)"""

    batch: Optional[str] = None
    """ID shared by all tests or predictions in a batch run"""

    ground_answer_counts: Union[Dict[str, object], object, None] = None
    """Ground-truth answer counts (benchmark mode only)"""

    ground_answer_percentages: Union[Dict[str, object], object, None] = None
    """Ground-truth answer percentages (benchmark mode only)"""

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

    test_finished_at: Optional[datetime] = None
    """When test finished"""

    test_started_at: Optional[datetime] = None
    """When test began"""
