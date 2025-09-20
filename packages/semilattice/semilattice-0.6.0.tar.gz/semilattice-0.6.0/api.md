# Predictions

Types:

```python
from semilattice.types import (
    APIResponseListPredictions,
    Prediction,
    PredictionBatch,
    PredictionRequest,
    PredictionResponse,
)
```

Methods:

- <code title="post /v1/predictions">client.predictions.<a href="./src/semilattice/resources/predictions.py">create</a>(\*\*<a href="src/semilattice/types/prediction_create_params.py">params</a>) -> <a href="./src/semilattice/types/api_response_list_predictions.py">APIResponseListPredictions</a></code>
- <code title="get /v1/predictions/{prediction_id}">client.predictions.<a href="./src/semilattice/resources/predictions.py">get</a>(prediction_id) -> <a href="./src/semilattice/types/prediction_response.py">PredictionResponse</a></code>
- <code title="get /v1/predictions/batch/{batch_id}">client.predictions.<a href="./src/semilattice/resources/predictions.py">get_batch</a>(batch_id) -> <a href="./src/semilattice/types/prediction_batch.py">PredictionBatch</a></code>

# Tests

Types:

```python
from semilattice.types import APIResponseListTests, Test, TestBatch, TestRequest, TestResponse
```

Methods:

- <code title="post /v1/tests">client.tests.<a href="./src/semilattice/resources/tests.py">create</a>(\*\*<a href="src/semilattice/types/test_create_params.py">params</a>) -> <a href="./src/semilattice/types/api_response_list_tests.py">APIResponseListTests</a></code>
- <code title="get /v1/tests/{test_id}">client.tests.<a href="./src/semilattice/resources/tests.py">get</a>(test_id) -> <a href="./src/semilattice/types/test_response.py">TestResponse</a></code>
- <code title="get /v1/tests/batch/{batch_id}">client.tests.<a href="./src/semilattice/resources/tests.py">get_batch</a>(batch_id) -> <a href="./src/semilattice/types/test_batch.py">TestBatch</a></code>

# Answers

Types:

```python
from semilattice.types import (
    AnswerRequest,
    AnswerResponse,
    APIResponseListAnswers,
    AnswerGetResponse,
)
```

Methods:

- <code title="post /v1/answers/benchmark">client.answers.<a href="./src/semilattice/resources/answers.py">benchmark</a>(\*\*<a href="src/semilattice/types/answer_benchmark_params.py">params</a>) -> <a href="./src/semilattice/types/api_response_list_answers.py">APIResponseListAnswers</a></code>
- <code title="get /v1/answers/{answer_id}">client.answers.<a href="./src/semilattice/resources/answers.py">get</a>(answer_id) -> <a href="./src/semilattice/types/answer_get_response.py">AnswerGetResponse</a></code>
- <code title="post /v1/answers">client.answers.<a href="./src/semilattice/resources/answers.py">simulate</a>(\*\*<a href="src/semilattice/types/answer_simulate_params.py">params</a>) -> <a href="./src/semilattice/types/api_response_list_answers.py">APIResponseListAnswers</a></code>

# Populations

Types:

```python
from semilattice.types import APIResponseListPopulations, PopulationResponse
```

Methods:

- <code title="post /v1/populations">client.populations.<a href="./src/semilattice/resources/populations.py">create</a>(\*\*<a href="src/semilattice/types/population_create_params.py">params</a>) -> <a href="./src/semilattice/types/population_response.py">PopulationResponse</a></code>
- <code title="get /v1/populations">client.populations.<a href="./src/semilattice/resources/populations.py">list</a>(\*\*<a href="src/semilattice/types/population_list_params.py">params</a>) -> <a href="./src/semilattice/types/api_response_list_populations.py">APIResponseListPopulations</a></code>
- <code title="get /v1/populations/{population_id}">client.populations.<a href="./src/semilattice/resources/populations.py">get</a>(population_id) -> <a href="./src/semilattice/types/population_response.py">PopulationResponse</a></code>
- <code title="post /v1/populations/{population_id}/test">client.populations.<a href="./src/semilattice/resources/populations.py">test</a>(population_id) -> <a href="./src/semilattice/types/population_response.py">PopulationResponse</a></code>
