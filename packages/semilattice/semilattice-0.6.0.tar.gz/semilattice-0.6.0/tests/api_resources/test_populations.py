# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from semilattice import Semilattice, AsyncSemilattice
from tests.utils import assert_matches_type
from semilattice.types import (
    PopulationResponse,
    APIResponseListPopulations,
)
from semilattice._utils import parse_date

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPopulations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Semilattice) -> None:
        population = client.populations.create(
            name="name",
            population_options={
                "question_options": [
                    {
                        "question_number": 0,
                        "question_type": "single-choice",
                    }
                ]
            },
            seed_data=b"raw file contents",
        )
        assert_matches_type(PopulationResponse, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Semilattice) -> None:
        population = client.populations.create(
            name="name",
            population_options={
                "question_options": [
                    {
                        "question_number": 0,
                        "question_type": "single-choice",
                        "limit": 0,
                    }
                ]
            },
            seed_data=b"raw file contents",
            data_source="data_source",
            description="description",
            effective_date=parse_date("2019-12-27"),
            reality_target="reality_target",
            run_test=True,
            simulation_engine="simulation_engine",
        )
        assert_matches_type(PopulationResponse, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Semilattice) -> None:
        response = client.populations.with_raw_response.create(
            name="name",
            population_options={
                "question_options": [
                    {
                        "question_number": 0,
                        "question_type": "single-choice",
                    }
                ]
            },
            seed_data=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        population = response.parse()
        assert_matches_type(PopulationResponse, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Semilattice) -> None:
        with client.populations.with_streaming_response.create(
            name="name",
            population_options={
                "question_options": [
                    {
                        "question_number": 0,
                        "question_type": "single-choice",
                    }
                ]
            },
            seed_data=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            population = response.parse()
            assert_matches_type(PopulationResponse, population, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Semilattice) -> None:
        population = client.populations.list()
        assert_matches_type(APIResponseListPopulations, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Semilattice) -> None:
        population = client.populations.list(
            limit=1,
            skip=0,
        )
        assert_matches_type(APIResponseListPopulations, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Semilattice) -> None:
        response = client.populations.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        population = response.parse()
        assert_matches_type(APIResponseListPopulations, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Semilattice) -> None:
        with client.populations.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            population = response.parse()
            assert_matches_type(APIResponseListPopulations, population, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Semilattice) -> None:
        population = client.populations.get(
            "population_id",
        )
        assert_matches_type(PopulationResponse, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Semilattice) -> None:
        response = client.populations.with_raw_response.get(
            "population_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        population = response.parse()
        assert_matches_type(PopulationResponse, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Semilattice) -> None:
        with client.populations.with_streaming_response.get(
            "population_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            population = response.parse()
            assert_matches_type(PopulationResponse, population, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Semilattice) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `population_id` but received ''"):
            client.populations.with_raw_response.get(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_test(self, client: Semilattice) -> None:
        population = client.populations.test(
            "population_id",
        )
        assert_matches_type(PopulationResponse, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_test(self, client: Semilattice) -> None:
        response = client.populations.with_raw_response.test(
            "population_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        population = response.parse()
        assert_matches_type(PopulationResponse, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_test(self, client: Semilattice) -> None:
        with client.populations.with_streaming_response.test(
            "population_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            population = response.parse()
            assert_matches_type(PopulationResponse, population, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_test(self, client: Semilattice) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `population_id` but received ''"):
            client.populations.with_raw_response.test(
                "",
            )


class TestAsyncPopulations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncSemilattice) -> None:
        population = await async_client.populations.create(
            name="name",
            population_options={
                "question_options": [
                    {
                        "question_number": 0,
                        "question_type": "single-choice",
                    }
                ]
            },
            seed_data=b"raw file contents",
        )
        assert_matches_type(PopulationResponse, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncSemilattice) -> None:
        population = await async_client.populations.create(
            name="name",
            population_options={
                "question_options": [
                    {
                        "question_number": 0,
                        "question_type": "single-choice",
                        "limit": 0,
                    }
                ]
            },
            seed_data=b"raw file contents",
            data_source="data_source",
            description="description",
            effective_date=parse_date("2019-12-27"),
            reality_target="reality_target",
            run_test=True,
            simulation_engine="simulation_engine",
        )
        assert_matches_type(PopulationResponse, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncSemilattice) -> None:
        response = await async_client.populations.with_raw_response.create(
            name="name",
            population_options={
                "question_options": [
                    {
                        "question_number": 0,
                        "question_type": "single-choice",
                    }
                ]
            },
            seed_data=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        population = await response.parse()
        assert_matches_type(PopulationResponse, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncSemilattice) -> None:
        async with async_client.populations.with_streaming_response.create(
            name="name",
            population_options={
                "question_options": [
                    {
                        "question_number": 0,
                        "question_type": "single-choice",
                    }
                ]
            },
            seed_data=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            population = await response.parse()
            assert_matches_type(PopulationResponse, population, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncSemilattice) -> None:
        population = await async_client.populations.list()
        assert_matches_type(APIResponseListPopulations, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncSemilattice) -> None:
        population = await async_client.populations.list(
            limit=1,
            skip=0,
        )
        assert_matches_type(APIResponseListPopulations, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncSemilattice) -> None:
        response = await async_client.populations.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        population = await response.parse()
        assert_matches_type(APIResponseListPopulations, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncSemilattice) -> None:
        async with async_client.populations.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            population = await response.parse()
            assert_matches_type(APIResponseListPopulations, population, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncSemilattice) -> None:
        population = await async_client.populations.get(
            "population_id",
        )
        assert_matches_type(PopulationResponse, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncSemilattice) -> None:
        response = await async_client.populations.with_raw_response.get(
            "population_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        population = await response.parse()
        assert_matches_type(PopulationResponse, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncSemilattice) -> None:
        async with async_client.populations.with_streaming_response.get(
            "population_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            population = await response.parse()
            assert_matches_type(PopulationResponse, population, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncSemilattice) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `population_id` but received ''"):
            await async_client.populations.with_raw_response.get(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_test(self, async_client: AsyncSemilattice) -> None:
        population = await async_client.populations.test(
            "population_id",
        )
        assert_matches_type(PopulationResponse, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_test(self, async_client: AsyncSemilattice) -> None:
        response = await async_client.populations.with_raw_response.test(
            "population_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        population = await response.parse()
        assert_matches_type(PopulationResponse, population, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_test(self, async_client: AsyncSemilattice) -> None:
        async with async_client.populations.with_streaming_response.test(
            "population_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            population = await response.parse()
            assert_matches_type(PopulationResponse, population, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_test(self, async_client: AsyncSemilattice) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `population_id` but received ''"):
            await async_client.populations.with_raw_response.test(
                "",
            )
