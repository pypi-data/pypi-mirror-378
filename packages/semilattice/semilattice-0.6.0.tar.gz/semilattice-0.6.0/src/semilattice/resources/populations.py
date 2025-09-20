# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Mapping, Optional, cast
from datetime import date

import httpx

from ..types import population_list_params, population_create_params
from .._types import Body, Omit, Query, Headers, NotGiven, FileTypes, omit, not_given
from .._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.population_response import PopulationResponse
from ..types.api_response_list_populations import APIResponseListPopulations

__all__ = ["PopulationsResource", "AsyncPopulationsResource"]


class PopulationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PopulationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#accessing-raw-response-data-eg-headers
        """
        return PopulationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PopulationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#with_streaming_response
        """
        return PopulationsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        name: str,
        population_options: population_create_params.PopulationOptions,
        seed_data: FileTypes,
        data_source: Optional[str] | Omit = omit,
        description: Optional[str] | Omit = omit,
        effective_date: Union[str, date, None] | Omit = omit,
        reality_target: Optional[str] | Omit = omit,
        run_test: Optional[bool] | Omit = omit,
        simulation_engine: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PopulationResponse:
        """
        Creates a new population model.

        Args:
          name: Name of the new population

          population_options: **Important:** the API expects population_options to be sent as JSON string. Use
              json.dumps() to convert your object to string format for multipart/form-data
              requests.

          data_source: Where the data comes from

          description: Optional description for the population

          effective_date: The date when this data was sourced in reality

          reality_target: Label for the real-world target the population is modeling

          run_test: Whether to run an accuracy test immediately after creation

          simulation_engine: Identifier for the simulation engine to be used

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "name": name,
                "population_options": population_options,
                "seed_data": seed_data,
                "data_source": data_source,
                "description": description,
                "effective_date": effective_date,
                "reality_target": reality_target,
                "run_test": run_test,
                "simulation_engine": simulation_engine,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["seed_data"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/v1/populations",
            body=maybe_transform(body, population_create_params.PopulationCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PopulationResponse,
        )

    def list(
        self,
        *,
        limit: int | Omit = omit,
        skip: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIResponseListPopulations:
        """
        Fetches all population models available for predictions.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/populations",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "skip": skip,
                    },
                    population_list_params.PopulationListParams,
                ),
            ),
            cast_to=APIResponseListPopulations,
        )

    def get(
        self,
        population_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PopulationResponse:
        """
        Fetches a population, along with its status, accuracy metrics, and other
        metadata.

        Args:
          population_id: ID of the population to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not population_id:
            raise ValueError(f"Expected a non-empty value for `population_id` but received {population_id!r}")
        return self._get(
            f"/v1/populations/{population_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PopulationResponse,
        )

    def test(
        self,
        population_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PopulationResponse:
        """
        Triggers an accuracy test for a population model, if not yet tested.

        Args:
          population_id: ID of the population to test.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not population_id:
            raise ValueError(f"Expected a non-empty value for `population_id` but received {population_id!r}")
        return self._post(
            f"/v1/populations/{population_id}/test",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PopulationResponse,
        )


class AsyncPopulationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPopulationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPopulationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPopulationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#with_streaming_response
        """
        return AsyncPopulationsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        name: str,
        population_options: population_create_params.PopulationOptions,
        seed_data: FileTypes,
        data_source: Optional[str] | Omit = omit,
        description: Optional[str] | Omit = omit,
        effective_date: Union[str, date, None] | Omit = omit,
        reality_target: Optional[str] | Omit = omit,
        run_test: Optional[bool] | Omit = omit,
        simulation_engine: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PopulationResponse:
        """
        Creates a new population model.

        Args:
          name: Name of the new population

          population_options: **Important:** the API expects population_options to be sent as JSON string. Use
              json.dumps() to convert your object to string format for multipart/form-data
              requests.

          data_source: Where the data comes from

          description: Optional description for the population

          effective_date: The date when this data was sourced in reality

          reality_target: Label for the real-world target the population is modeling

          run_test: Whether to run an accuracy test immediately after creation

          simulation_engine: Identifier for the simulation engine to be used

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "name": name,
                "population_options": population_options,
                "seed_data": seed_data,
                "data_source": data_source,
                "description": description,
                "effective_date": effective_date,
                "reality_target": reality_target,
                "run_test": run_test,
                "simulation_engine": simulation_engine,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["seed_data"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/v1/populations",
            body=await async_maybe_transform(body, population_create_params.PopulationCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PopulationResponse,
        )

    async def list(
        self,
        *,
        limit: int | Omit = omit,
        skip: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIResponseListPopulations:
        """
        Fetches all population models available for predictions.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/populations",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "skip": skip,
                    },
                    population_list_params.PopulationListParams,
                ),
            ),
            cast_to=APIResponseListPopulations,
        )

    async def get(
        self,
        population_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PopulationResponse:
        """
        Fetches a population, along with its status, accuracy metrics, and other
        metadata.

        Args:
          population_id: ID of the population to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not population_id:
            raise ValueError(f"Expected a non-empty value for `population_id` but received {population_id!r}")
        return await self._get(
            f"/v1/populations/{population_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PopulationResponse,
        )

    async def test(
        self,
        population_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PopulationResponse:
        """
        Triggers an accuracy test for a population model, if not yet tested.

        Args:
          population_id: ID of the population to test.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not population_id:
            raise ValueError(f"Expected a non-empty value for `population_id` but received {population_id!r}")
        return await self._post(
            f"/v1/populations/{population_id}/test",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PopulationResponse,
        )


class PopulationsResourceWithRawResponse:
    def __init__(self, populations: PopulationsResource) -> None:
        self._populations = populations

        self.create = to_raw_response_wrapper(
            populations.create,
        )
        self.list = to_raw_response_wrapper(
            populations.list,
        )
        self.get = to_raw_response_wrapper(
            populations.get,
        )
        self.test = to_raw_response_wrapper(
            populations.test,
        )


class AsyncPopulationsResourceWithRawResponse:
    def __init__(self, populations: AsyncPopulationsResource) -> None:
        self._populations = populations

        self.create = async_to_raw_response_wrapper(
            populations.create,
        )
        self.list = async_to_raw_response_wrapper(
            populations.list,
        )
        self.get = async_to_raw_response_wrapper(
            populations.get,
        )
        self.test = async_to_raw_response_wrapper(
            populations.test,
        )


class PopulationsResourceWithStreamingResponse:
    def __init__(self, populations: PopulationsResource) -> None:
        self._populations = populations

        self.create = to_streamed_response_wrapper(
            populations.create,
        )
        self.list = to_streamed_response_wrapper(
            populations.list,
        )
        self.get = to_streamed_response_wrapper(
            populations.get,
        )
        self.test = to_streamed_response_wrapper(
            populations.test,
        )


class AsyncPopulationsResourceWithStreamingResponse:
    def __init__(self, populations: AsyncPopulationsResource) -> None:
        self._populations = populations

        self.create = async_to_streamed_response_wrapper(
            populations.create,
        )
        self.list = async_to_streamed_response_wrapper(
            populations.list,
        )
        self.get = async_to_streamed_response_wrapper(
            populations.get,
        )
        self.test = async_to_streamed_response_wrapper(
            populations.test,
        )
