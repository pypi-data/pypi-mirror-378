# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import team_member_update_params
from .._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
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
from ..types.team_member_list_response import TeamMemberListResponse
from ..types.team_member_remove_response import TeamMemberRemoveResponse
from ..types.team_member_update_response import TeamMemberUpdateResponse

__all__ = ["TeamMembersResource", "AsyncTeamMembersResource"]


class TeamMembersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TeamMembersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ComposioHQ/composio-base-py#accessing-raw-response-data-eg-headers
        """
        return TeamMembersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TeamMembersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ComposioHQ/composio-base-py#with_streaming_response
        """
        return TeamMembersResourceWithStreamingResponse(self)

    def update(
        self,
        id: str,
        *,
        email: str | Omit = omit,
        name: str | Omit = omit,
        role: Literal["ADMIN", "DEVELOPER"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TeamMemberUpdateResponse:
        """
        Update the details of an existing team member

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._put(
            f"/api/v3/team-members/update/{id}",
            body=maybe_transform(
                {
                    "email": email,
                    "name": name,
                    "role": role,
                },
                team_member_update_params.TeamMemberUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TeamMemberUpdateResponse,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TeamMemberListResponse:
        """Retrieve a list of all team members in the current organization"""
        return self._get(
            "/api/v3/team-members/list",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TeamMemberListResponse,
        )

    def invite(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Send an invitation to a new team member to join the organization"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/api/v3/team-members/invite",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def remove(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TeamMemberRemoveResponse:
        """
        Remove a team member from the organization and revoke their access

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/api/v3/team-members/remove/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TeamMemberRemoveResponse,
        )


class AsyncTeamMembersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTeamMembersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ComposioHQ/composio-base-py#accessing-raw-response-data-eg-headers
        """
        return AsyncTeamMembersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTeamMembersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ComposioHQ/composio-base-py#with_streaming_response
        """
        return AsyncTeamMembersResourceWithStreamingResponse(self)

    async def update(
        self,
        id: str,
        *,
        email: str | Omit = omit,
        name: str | Omit = omit,
        role: Literal["ADMIN", "DEVELOPER"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TeamMemberUpdateResponse:
        """
        Update the details of an existing team member

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._put(
            f"/api/v3/team-members/update/{id}",
            body=await async_maybe_transform(
                {
                    "email": email,
                    "name": name,
                    "role": role,
                },
                team_member_update_params.TeamMemberUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TeamMemberUpdateResponse,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TeamMemberListResponse:
        """Retrieve a list of all team members in the current organization"""
        return await self._get(
            "/api/v3/team-members/list",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TeamMemberListResponse,
        )

    async def invite(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Send an invitation to a new team member to join the organization"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/api/v3/team-members/invite",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def remove(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TeamMemberRemoveResponse:
        """
        Remove a team member from the organization and revoke their access

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/api/v3/team-members/remove/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TeamMemberRemoveResponse,
        )


class TeamMembersResourceWithRawResponse:
    def __init__(self, team_members: TeamMembersResource) -> None:
        self._team_members = team_members

        self.update = to_raw_response_wrapper(
            team_members.update,
        )
        self.list = to_raw_response_wrapper(
            team_members.list,
        )
        self.invite = to_raw_response_wrapper(
            team_members.invite,
        )
        self.remove = to_raw_response_wrapper(
            team_members.remove,
        )


class AsyncTeamMembersResourceWithRawResponse:
    def __init__(self, team_members: AsyncTeamMembersResource) -> None:
        self._team_members = team_members

        self.update = async_to_raw_response_wrapper(
            team_members.update,
        )
        self.list = async_to_raw_response_wrapper(
            team_members.list,
        )
        self.invite = async_to_raw_response_wrapper(
            team_members.invite,
        )
        self.remove = async_to_raw_response_wrapper(
            team_members.remove,
        )


class TeamMembersResourceWithStreamingResponse:
    def __init__(self, team_members: TeamMembersResource) -> None:
        self._team_members = team_members

        self.update = to_streamed_response_wrapper(
            team_members.update,
        )
        self.list = to_streamed_response_wrapper(
            team_members.list,
        )
        self.invite = to_streamed_response_wrapper(
            team_members.invite,
        )
        self.remove = to_streamed_response_wrapper(
            team_members.remove,
        )


class AsyncTeamMembersResourceWithStreamingResponse:
    def __init__(self, team_members: AsyncTeamMembersResource) -> None:
        self._team_members = team_members

        self.update = async_to_streamed_response_wrapper(
            team_members.update,
        )
        self.list = async_to_streamed_response_wrapper(
            team_members.list,
        )
        self.invite = async_to_streamed_response_wrapper(
            team_members.invite,
        )
        self.remove = async_to_streamed_response_wrapper(
            team_members.remove,
        )
