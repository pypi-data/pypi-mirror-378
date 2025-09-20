# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import date, datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["TestBatch", "Data", "DataBatch", "DataTest", "Error"]


class DataBatch(BaseModel):
    id: str

    average_accuracy: Optional[float] = None
    """Average accuracy for this population model.

    Calculated as the mean average inverse mean absolute error (1 - MAE) for all
    test predictions
    """

    average_normalised_information_loss: Optional[float] = None
    """Average normalised information loss for this population model.

    Calculated as the normalised Kullback-Leibler (KL) divergence (entropy) between
    predicted and ground truth answer distributions for all test predictions in
    batch.
    """

    average_squared_error: Optional[float] = None
    """Average squared error for this population model.

    Calculated as the mean average root mean squared error (RMSE) for all test
    predictions
    """

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

    simulation_engine: Optional[str] = None
    """Simulation engine this population model will use"""

    test_finished_at: Optional[datetime] = None
    """All test predictions finished time"""

    test_started_at: Optional[datetime] = None
    """Test predictions start time"""


class DataTest(BaseModel):
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


class Data(BaseModel):
    batch: DataBatch
    """Batches model data:"""

    tests: List[DataTest]


class Error(BaseModel):
    code: str
    """Machine-readable error code"""

    message: str
    """Human-readable error message"""


class TestBatch(BaseModel):
    __test__ = False
    data: Optional[Data] = None
    """The primary response payload. Contains the result of the request if successful."""

    errors: Optional[List[Error]] = None
    """List of structured error messages, if any occurred during the request."""
