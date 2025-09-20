# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import typing_extensions
from typing import Optional

import httpx

from ..types import answer_simulate_params, answer_benchmark_params
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
from ..types.answer_get_response import AnswerGetResponse
from ..types.api_response_list_answers import APIResponseListAnswers

__all__ = ["AnswersResource", "AsyncAnswersResource"]


class AnswersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AnswersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AnswersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AnswersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#with_streaming_response
        """
        return AnswersResourceWithStreamingResponse(self)

    @typing_extensions.deprecated("Replaced by tests.create")
    def benchmark(
        self,
        *,
        answers: answer_benchmark_params.Answers,
        population_id: str,
        batch: Optional[answer_benchmark_params.Batch] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIResponseListAnswers:
        """
        Simulates the answer to a known question to evaluate population model accuracy.

        Args:
          answers: One or more population answers to simulate. A single object is accepted for
              convenience.

          population_id: ID of the population model against which to run the simulation

          batch: Optional batch details to apply to these predictions. If provided, a batch
              object will be created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/answers/benchmark",
            body=maybe_transform(
                {
                    "answers": answers,
                    "population_id": population_id,
                    "batch": batch,
                },
                answer_benchmark_params.AnswerBenchmarkParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIResponseListAnswers,
        )

    @typing_extensions.deprecated("Replaced by predictions.get or tests.get")
    def get(
        self,
        answer_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AnswerGetResponse:
        """
        Retrieves an answer simulation, along with its status and accuracy metrics if
        it's a benchmark simulation.

        Args:
          answer_id: ID of the prediction you want to fetch.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not answer_id:
            raise ValueError(f"Expected a non-empty value for `answer_id` but received {answer_id!r}")
        return self._get(
            f"/v1/answers/{answer_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AnswerGetResponse,
        )

    @typing_extensions.deprecated("Replaced by predictions.create")
    def simulate(
        self,
        *,
        answers: answer_simulate_params.Answers,
        population_id: str,
        batch: Optional[answer_simulate_params.Batch] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIResponseListAnswers:
        """
        Simulates the answer to a new question.

        Args:
          answers: One or more population answers to simulate. A single object is accepted for
              convenience.

          population_id: ID of the population model against which to run the simulation

          batch: Optional batch details to apply to these predictions. If provided, a batch
              object will be created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/answers",
            body=maybe_transform(
                {
                    "answers": answers,
                    "population_id": population_id,
                    "batch": batch,
                },
                answer_simulate_params.AnswerSimulateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIResponseListAnswers,
        )


class AsyncAnswersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAnswersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAnswersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAnswersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#with_streaming_response
        """
        return AsyncAnswersResourceWithStreamingResponse(self)

    @typing_extensions.deprecated("Replaced by tests.create")
    async def benchmark(
        self,
        *,
        answers: answer_benchmark_params.Answers,
        population_id: str,
        batch: Optional[answer_benchmark_params.Batch] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIResponseListAnswers:
        """
        Simulates the answer to a known question to evaluate population model accuracy.

        Args:
          answers: One or more population answers to simulate. A single object is accepted for
              convenience.

          population_id: ID of the population model against which to run the simulation

          batch: Optional batch details to apply to these predictions. If provided, a batch
              object will be created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/answers/benchmark",
            body=await async_maybe_transform(
                {
                    "answers": answers,
                    "population_id": population_id,
                    "batch": batch,
                },
                answer_benchmark_params.AnswerBenchmarkParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIResponseListAnswers,
        )

    @typing_extensions.deprecated("Replaced by predictions.get or tests.get")
    async def get(
        self,
        answer_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AnswerGetResponse:
        """
        Retrieves an answer simulation, along with its status and accuracy metrics if
        it's a benchmark simulation.

        Args:
          answer_id: ID of the prediction you want to fetch.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not answer_id:
            raise ValueError(f"Expected a non-empty value for `answer_id` but received {answer_id!r}")
        return await self._get(
            f"/v1/answers/{answer_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AnswerGetResponse,
        )

    @typing_extensions.deprecated("Replaced by predictions.create")
    async def simulate(
        self,
        *,
        answers: answer_simulate_params.Answers,
        population_id: str,
        batch: Optional[answer_simulate_params.Batch] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIResponseListAnswers:
        """
        Simulates the answer to a new question.

        Args:
          answers: One or more population answers to simulate. A single object is accepted for
              convenience.

          population_id: ID of the population model against which to run the simulation

          batch: Optional batch details to apply to these predictions. If provided, a batch
              object will be created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/answers",
            body=await async_maybe_transform(
                {
                    "answers": answers,
                    "population_id": population_id,
                    "batch": batch,
                },
                answer_simulate_params.AnswerSimulateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIResponseListAnswers,
        )


class AnswersResourceWithRawResponse:
    def __init__(self, answers: AnswersResource) -> None:
        self._answers = answers

        self.benchmark = (  # pyright: ignore[reportDeprecated]
            to_raw_response_wrapper(
                answers.benchmark,  # pyright: ignore[reportDeprecated],
            )
        )
        self.get = (  # pyright: ignore[reportDeprecated]
            to_raw_response_wrapper(
                answers.get,  # pyright: ignore[reportDeprecated],
            )
        )
        self.simulate = (  # pyright: ignore[reportDeprecated]
            to_raw_response_wrapper(
                answers.simulate,  # pyright: ignore[reportDeprecated],
            )
        )


class AsyncAnswersResourceWithRawResponse:
    def __init__(self, answers: AsyncAnswersResource) -> None:
        self._answers = answers

        self.benchmark = (  # pyright: ignore[reportDeprecated]
            async_to_raw_response_wrapper(
                answers.benchmark,  # pyright: ignore[reportDeprecated],
            )
        )
        self.get = (  # pyright: ignore[reportDeprecated]
            async_to_raw_response_wrapper(
                answers.get,  # pyright: ignore[reportDeprecated],
            )
        )
        self.simulate = (  # pyright: ignore[reportDeprecated]
            async_to_raw_response_wrapper(
                answers.simulate,  # pyright: ignore[reportDeprecated],
            )
        )


class AnswersResourceWithStreamingResponse:
    def __init__(self, answers: AnswersResource) -> None:
        self._answers = answers

        self.benchmark = (  # pyright: ignore[reportDeprecated]
            to_streamed_response_wrapper(
                answers.benchmark,  # pyright: ignore[reportDeprecated],
            )
        )
        self.get = (  # pyright: ignore[reportDeprecated]
            to_streamed_response_wrapper(
                answers.get,  # pyright: ignore[reportDeprecated],
            )
        )
        self.simulate = (  # pyright: ignore[reportDeprecated]
            to_streamed_response_wrapper(
                answers.simulate,  # pyright: ignore[reportDeprecated],
            )
        )


class AsyncAnswersResourceWithStreamingResponse:
    def __init__(self, answers: AsyncAnswersResource) -> None:
        self._answers = answers

        self.benchmark = (  # pyright: ignore[reportDeprecated]
            async_to_streamed_response_wrapper(
                answers.benchmark,  # pyright: ignore[reportDeprecated],
            )
        )
        self.get = (  # pyright: ignore[reportDeprecated]
            async_to_streamed_response_wrapper(
                answers.get,  # pyright: ignore[reportDeprecated],
            )
        )
        self.simulate = (  # pyright: ignore[reportDeprecated]
            async_to_streamed_response_wrapper(
                answers.simulate,  # pyright: ignore[reportDeprecated],
            )
        )
