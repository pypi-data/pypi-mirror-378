# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..types import prediction_create_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.prediction_batch import PredictionBatch
from ..types.prediction_response import PredictionResponse
from ..types.api_response_list_predictions import APIResponseListPredictions

__all__ = ["PredictionsResource", "AsyncPredictionsResource"]


class PredictionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PredictionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#accessing-raw-response-data-eg-headers
        """
        return PredictionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PredictionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#with_streaming_response
        """
        return PredictionsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        population_id: str,
        predictions: prediction_create_params.Predictions,
        batch: Optional[prediction_create_params.Batch] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIResponseListPredictions:
        """
        Predicts the answer to a new question for a target population.

        Args:
          population_id: ID of the population model against which to run the simulation

          predictions: One or more predictions to run.

          batch: Optional batch details to apply to these predictions. If provided, a batch
              object will be created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/predictions",
            body=maybe_transform(
                {
                    "population_id": population_id,
                    "predictions": predictions,
                    "batch": batch,
                },
                prediction_create_params.PredictionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIResponseListPredictions,
        )

    def get(
        self,
        prediction_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PredictionResponse:
        """
        Retrieves an answer prediction.

        Args:
          prediction_id: ID of the prediction you want to fetch.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not prediction_id:
            raise ValueError(f"Expected a non-empty value for `prediction_id` but received {prediction_id!r}")
        return self._get(
            f"/v1/predictions/{prediction_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PredictionResponse,
        )

    def get_batch(
        self,
        batch_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PredictionBatch:
        """
        Retrieves a batch of predictions.

        Args:
          batch_id: ID of the prediction batch you want to fetch.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not batch_id:
            raise ValueError(f"Expected a non-empty value for `batch_id` but received {batch_id!r}")
        return self._get(
            f"/v1/predictions/batch/{batch_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PredictionBatch,
        )


class AsyncPredictionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPredictionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPredictionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPredictionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#with_streaming_response
        """
        return AsyncPredictionsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        population_id: str,
        predictions: prediction_create_params.Predictions,
        batch: Optional[prediction_create_params.Batch] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIResponseListPredictions:
        """
        Predicts the answer to a new question for a target population.

        Args:
          population_id: ID of the population model against which to run the simulation

          predictions: One or more predictions to run.

          batch: Optional batch details to apply to these predictions. If provided, a batch
              object will be created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/predictions",
            body=await async_maybe_transform(
                {
                    "population_id": population_id,
                    "predictions": predictions,
                    "batch": batch,
                },
                prediction_create_params.PredictionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIResponseListPredictions,
        )

    async def get(
        self,
        prediction_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PredictionResponse:
        """
        Retrieves an answer prediction.

        Args:
          prediction_id: ID of the prediction you want to fetch.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not prediction_id:
            raise ValueError(f"Expected a non-empty value for `prediction_id` but received {prediction_id!r}")
        return await self._get(
            f"/v1/predictions/{prediction_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PredictionResponse,
        )

    async def get_batch(
        self,
        batch_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PredictionBatch:
        """
        Retrieves a batch of predictions.

        Args:
          batch_id: ID of the prediction batch you want to fetch.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not batch_id:
            raise ValueError(f"Expected a non-empty value for `batch_id` but received {batch_id!r}")
        return await self._get(
            f"/v1/predictions/batch/{batch_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PredictionBatch,
        )


class PredictionsResourceWithRawResponse:
    def __init__(self, predictions: PredictionsResource) -> None:
        self._predictions = predictions

        self.create = to_raw_response_wrapper(
            predictions.create,
        )
        self.get = to_raw_response_wrapper(
            predictions.get,
        )
        self.get_batch = to_raw_response_wrapper(
            predictions.get_batch,
        )


class AsyncPredictionsResourceWithRawResponse:
    def __init__(self, predictions: AsyncPredictionsResource) -> None:
        self._predictions = predictions

        self.create = async_to_raw_response_wrapper(
            predictions.create,
        )
        self.get = async_to_raw_response_wrapper(
            predictions.get,
        )
        self.get_batch = async_to_raw_response_wrapper(
            predictions.get_batch,
        )


class PredictionsResourceWithStreamingResponse:
    def __init__(self, predictions: PredictionsResource) -> None:
        self._predictions = predictions

        self.create = to_streamed_response_wrapper(
            predictions.create,
        )
        self.get = to_streamed_response_wrapper(
            predictions.get,
        )
        self.get_batch = to_streamed_response_wrapper(
            predictions.get_batch,
        )


class AsyncPredictionsResourceWithStreamingResponse:
    def __init__(self, predictions: AsyncPredictionsResource) -> None:
        self._predictions = predictions

        self.create = async_to_streamed_response_wrapper(
            predictions.create,
        )
        self.get = async_to_streamed_response_wrapper(
            predictions.get,
        )
        self.get_batch = async_to_streamed_response_wrapper(
            predictions.get_batch,
        )
