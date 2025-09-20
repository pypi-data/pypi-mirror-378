# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from semilattice import Semilattice, AsyncSemilattice
from tests.utils import assert_matches_type
from semilattice.types import AnswerGetResponse, APIResponseListAnswers
from semilattice._utils import parse_date

# pyright: reportDeprecated=false

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAnswers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_benchmark(self, client: Semilattice) -> None:
        with pytest.warns(DeprecationWarning):
            answer = client.answers.benchmark(
                answers={
                    "ground_answer_counts": {"foo": 0},
                    "ground_answer_sample_size": 0,
                    "question": "question",
                    "question_options": {"question_type": "single-choice"},
                },
                population_id="population_id",
            )

        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_benchmark_with_all_params(self, client: Semilattice) -> None:
        with pytest.warns(DeprecationWarning):
            answer = client.answers.benchmark(
                answers={
                    "ground_answer_counts": {"foo": 0},
                    "ground_answer_sample_size": 0,
                    "question": "question",
                    "question_options": {
                        "question_type": "single-choice",
                        "limit": 0,
                    },
                    "answer_options": ["string"],
                },
                population_id="population_id",
                batch={
                    "name": "Q4 user trends questions",
                    "description": "A copy testing benchmarking batch",
                    "effective_date": parse_date("2024-01-09"),
                },
            )

        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_benchmark(self, client: Semilattice) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.answers.with_raw_response.benchmark(
                answers={
                    "ground_answer_counts": {"foo": 0},
                    "ground_answer_sample_size": 0,
                    "question": "question",
                    "question_options": {"question_type": "single-choice"},
                },
                population_id="population_id",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        answer = response.parse()
        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_benchmark(self, client: Semilattice) -> None:
        with pytest.warns(DeprecationWarning):
            with client.answers.with_streaming_response.benchmark(
                answers={
                    "ground_answer_counts": {"foo": 0},
                    "ground_answer_sample_size": 0,
                    "question": "question",
                    "question_options": {"question_type": "single-choice"},
                },
                population_id="population_id",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                answer = response.parse()
                assert_matches_type(APIResponseListAnswers, answer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Semilattice) -> None:
        with pytest.warns(DeprecationWarning):
            answer = client.answers.get(
                "answer_id",
            )

        assert_matches_type(AnswerGetResponse, answer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Semilattice) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.answers.with_raw_response.get(
                "answer_id",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        answer = response.parse()
        assert_matches_type(AnswerGetResponse, answer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Semilattice) -> None:
        with pytest.warns(DeprecationWarning):
            with client.answers.with_streaming_response.get(
                "answer_id",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                answer = response.parse()
                assert_matches_type(AnswerGetResponse, answer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Semilattice) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(ValueError, match=r"Expected a non-empty value for `answer_id` but received ''"):
                client.answers.with_raw_response.get(
                    "",
                )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_simulate(self, client: Semilattice) -> None:
        with pytest.warns(DeprecationWarning):
            answer = client.answers.simulate(
                answers={
                    "question": "question",
                    "question_options": {"question_type": "single-choice"},
                },
                population_id="population_id",
            )

        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_simulate_with_all_params(self, client: Semilattice) -> None:
        with pytest.warns(DeprecationWarning):
            answer = client.answers.simulate(
                answers={
                    "question": "question",
                    "question_options": {
                        "question_type": "single-choice",
                        "limit": 0,
                    },
                    "answer_options": ["string"],
                },
                population_id="population_id",
                batch={
                    "name": "Q4 user trends questions",
                    "description": "A copy testing benchmarking batch",
                    "effective_date": parse_date("2024-01-09"),
                },
            )

        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_simulate(self, client: Semilattice) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.answers.with_raw_response.simulate(
                answers={
                    "question": "question",
                    "question_options": {"question_type": "single-choice"},
                },
                population_id="population_id",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        answer = response.parse()
        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_simulate(self, client: Semilattice) -> None:
        with pytest.warns(DeprecationWarning):
            with client.answers.with_streaming_response.simulate(
                answers={
                    "question": "question",
                    "question_options": {"question_type": "single-choice"},
                },
                population_id="population_id",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                answer = response.parse()
                assert_matches_type(APIResponseListAnswers, answer, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAnswers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_benchmark(self, async_client: AsyncSemilattice) -> None:
        with pytest.warns(DeprecationWarning):
            answer = await async_client.answers.benchmark(
                answers={
                    "ground_answer_counts": {"foo": 0},
                    "ground_answer_sample_size": 0,
                    "question": "question",
                    "question_options": {"question_type": "single-choice"},
                },
                population_id="population_id",
            )

        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_benchmark_with_all_params(self, async_client: AsyncSemilattice) -> None:
        with pytest.warns(DeprecationWarning):
            answer = await async_client.answers.benchmark(
                answers={
                    "ground_answer_counts": {"foo": 0},
                    "ground_answer_sample_size": 0,
                    "question": "question",
                    "question_options": {
                        "question_type": "single-choice",
                        "limit": 0,
                    },
                    "answer_options": ["string"],
                },
                population_id="population_id",
                batch={
                    "name": "Q4 user trends questions",
                    "description": "A copy testing benchmarking batch",
                    "effective_date": parse_date("2024-01-09"),
                },
            )

        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_benchmark(self, async_client: AsyncSemilattice) -> None:
        with pytest.warns(DeprecationWarning):
            response = await async_client.answers.with_raw_response.benchmark(
                answers={
                    "ground_answer_counts": {"foo": 0},
                    "ground_answer_sample_size": 0,
                    "question": "question",
                    "question_options": {"question_type": "single-choice"},
                },
                population_id="population_id",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        answer = await response.parse()
        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_benchmark(self, async_client: AsyncSemilattice) -> None:
        with pytest.warns(DeprecationWarning):
            async with async_client.answers.with_streaming_response.benchmark(
                answers={
                    "ground_answer_counts": {"foo": 0},
                    "ground_answer_sample_size": 0,
                    "question": "question",
                    "question_options": {"question_type": "single-choice"},
                },
                population_id="population_id",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                answer = await response.parse()
                assert_matches_type(APIResponseListAnswers, answer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncSemilattice) -> None:
        with pytest.warns(DeprecationWarning):
            answer = await async_client.answers.get(
                "answer_id",
            )

        assert_matches_type(AnswerGetResponse, answer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncSemilattice) -> None:
        with pytest.warns(DeprecationWarning):
            response = await async_client.answers.with_raw_response.get(
                "answer_id",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        answer = await response.parse()
        assert_matches_type(AnswerGetResponse, answer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncSemilattice) -> None:
        with pytest.warns(DeprecationWarning):
            async with async_client.answers.with_streaming_response.get(
                "answer_id",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                answer = await response.parse()
                assert_matches_type(AnswerGetResponse, answer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncSemilattice) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(ValueError, match=r"Expected a non-empty value for `answer_id` but received ''"):
                await async_client.answers.with_raw_response.get(
                    "",
                )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_simulate(self, async_client: AsyncSemilattice) -> None:
        with pytest.warns(DeprecationWarning):
            answer = await async_client.answers.simulate(
                answers={
                    "question": "question",
                    "question_options": {"question_type": "single-choice"},
                },
                population_id="population_id",
            )

        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_simulate_with_all_params(self, async_client: AsyncSemilattice) -> None:
        with pytest.warns(DeprecationWarning):
            answer = await async_client.answers.simulate(
                answers={
                    "question": "question",
                    "question_options": {
                        "question_type": "single-choice",
                        "limit": 0,
                    },
                    "answer_options": ["string"],
                },
                population_id="population_id",
                batch={
                    "name": "Q4 user trends questions",
                    "description": "A copy testing benchmarking batch",
                    "effective_date": parse_date("2024-01-09"),
                },
            )

        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_simulate(self, async_client: AsyncSemilattice) -> None:
        with pytest.warns(DeprecationWarning):
            response = await async_client.answers.with_raw_response.simulate(
                answers={
                    "question": "question",
                    "question_options": {"question_type": "single-choice"},
                },
                population_id="population_id",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        answer = await response.parse()
        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_simulate(self, async_client: AsyncSemilattice) -> None:
        with pytest.warns(DeprecationWarning):
            async with async_client.answers.with_streaming_response.simulate(
                answers={
                    "question": "question",
                    "question_options": {"question_type": "single-choice"},
                },
                population_id="population_id",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                answer = await response.parse()
                assert_matches_type(APIResponseListAnswers, answer, path=["response"])

        assert cast(Any, response.is_closed) is True
