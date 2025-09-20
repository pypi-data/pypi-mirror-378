# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from semilattice import Semilattice, AsyncSemilattice
from tests.utils import assert_matches_type
from semilattice.types import TestBatch, TestResponse, APIResponseListTests
from semilattice._utils import parse_date

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTests:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Semilattice) -> None:
        test = client.tests.create(
            population_id="population_id",
            tests={
                "ground_answer_counts": {"foo": 0},
                "ground_answer_sample_size": 0,
                "question": "question",
                "question_options": {"question_type": "single-choice"},
            },
        )
        assert_matches_type(APIResponseListTests, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Semilattice) -> None:
        test = client.tests.create(
            population_id="population_id",
            tests={
                "ground_answer_counts": {"foo": 0},
                "ground_answer_sample_size": 0,
                "question": "question",
                "question_options": {
                    "question_type": "single-choice",
                    "limit": 0,
                },
                "answer_options": ["string"],
            },
            batch={
                "name": "Q4 user trends questions",
                "description": "A copy testing benchmarking batch",
                "effective_date": parse_date("2024-01-09"),
            },
        )
        assert_matches_type(APIResponseListTests, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Semilattice) -> None:
        response = client.tests.with_raw_response.create(
            population_id="population_id",
            tests={
                "ground_answer_counts": {"foo": 0},
                "ground_answer_sample_size": 0,
                "question": "question",
                "question_options": {"question_type": "single-choice"},
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert_matches_type(APIResponseListTests, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Semilattice) -> None:
        with client.tests.with_streaming_response.create(
            population_id="population_id",
            tests={
                "ground_answer_counts": {"foo": 0},
                "ground_answer_sample_size": 0,
                "question": "question",
                "question_options": {"question_type": "single-choice"},
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert_matches_type(APIResponseListTests, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Semilattice) -> None:
        test = client.tests.get(
            "test_id",
        )
        assert_matches_type(TestResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Semilattice) -> None:
        response = client.tests.with_raw_response.get(
            "test_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert_matches_type(TestResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Semilattice) -> None:
        with client.tests.with_streaming_response.get(
            "test_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert_matches_type(TestResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Semilattice) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `test_id` but received ''"):
            client.tests.with_raw_response.get(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_batch(self, client: Semilattice) -> None:
        test = client.tests.get_batch(
            "batch_id",
        )
        assert_matches_type(TestBatch, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_batch(self, client: Semilattice) -> None:
        response = client.tests.with_raw_response.get_batch(
            "batch_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert_matches_type(TestBatch, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_batch(self, client: Semilattice) -> None:
        with client.tests.with_streaming_response.get_batch(
            "batch_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert_matches_type(TestBatch, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_batch(self, client: Semilattice) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_id` but received ''"):
            client.tests.with_raw_response.get_batch(
                "",
            )


class TestAsyncTests:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncSemilattice) -> None:
        test = await async_client.tests.create(
            population_id="population_id",
            tests={
                "ground_answer_counts": {"foo": 0},
                "ground_answer_sample_size": 0,
                "question": "question",
                "question_options": {"question_type": "single-choice"},
            },
        )
        assert_matches_type(APIResponseListTests, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncSemilattice) -> None:
        test = await async_client.tests.create(
            population_id="population_id",
            tests={
                "ground_answer_counts": {"foo": 0},
                "ground_answer_sample_size": 0,
                "question": "question",
                "question_options": {
                    "question_type": "single-choice",
                    "limit": 0,
                },
                "answer_options": ["string"],
            },
            batch={
                "name": "Q4 user trends questions",
                "description": "A copy testing benchmarking batch",
                "effective_date": parse_date("2024-01-09"),
            },
        )
        assert_matches_type(APIResponseListTests, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncSemilattice) -> None:
        response = await async_client.tests.with_raw_response.create(
            population_id="population_id",
            tests={
                "ground_answer_counts": {"foo": 0},
                "ground_answer_sample_size": 0,
                "question": "question",
                "question_options": {"question_type": "single-choice"},
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert_matches_type(APIResponseListTests, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncSemilattice) -> None:
        async with async_client.tests.with_streaming_response.create(
            population_id="population_id",
            tests={
                "ground_answer_counts": {"foo": 0},
                "ground_answer_sample_size": 0,
                "question": "question",
                "question_options": {"question_type": "single-choice"},
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert_matches_type(APIResponseListTests, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncSemilattice) -> None:
        test = await async_client.tests.get(
            "test_id",
        )
        assert_matches_type(TestResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncSemilattice) -> None:
        response = await async_client.tests.with_raw_response.get(
            "test_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert_matches_type(TestResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncSemilattice) -> None:
        async with async_client.tests.with_streaming_response.get(
            "test_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert_matches_type(TestResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncSemilattice) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `test_id` but received ''"):
            await async_client.tests.with_raw_response.get(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_batch(self, async_client: AsyncSemilattice) -> None:
        test = await async_client.tests.get_batch(
            "batch_id",
        )
        assert_matches_type(TestBatch, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_batch(self, async_client: AsyncSemilattice) -> None:
        response = await async_client.tests.with_raw_response.get_batch(
            "batch_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert_matches_type(TestBatch, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_batch(self, async_client: AsyncSemilattice) -> None:
        async with async_client.tests.with_streaming_response.get_batch(
            "batch_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert_matches_type(TestBatch, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_batch(self, async_client: AsyncSemilattice) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_id` but received ''"):
            await async_client.tests.with_raw_response.get_batch(
                "",
            )
