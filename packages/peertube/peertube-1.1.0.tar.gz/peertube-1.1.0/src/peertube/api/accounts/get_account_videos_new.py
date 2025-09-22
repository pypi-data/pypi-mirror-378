from typing import Any

from peertube.api.base.endpoint_base import BaseEndpoint
from peertube.client import AuthenticatedClient, Client
from peertube.models.get_account_videos_include import GetAccountVideosInclude
from peertube.models.get_account_videos_nsfw import GetAccountVideosNsfw
from peertube.models.get_account_videos_skip_count import GetAccountVideosSkipCount
from peertube.models.get_account_videos_sort import GetAccountVideosSort
from peertube.models.nsfw_flag import NSFWFlag
from peertube.models.video_list_response import VideoListResponse
from peertube.models.video_privacy_set import VideoPrivacySet
from peertube.types import UNSET, Response, Unset


class GetAccountVideosEndpoint(BaseEndpoint):
    """Endpoint for getting videos of an account."""

    @property
    def path(self) -> str:
        """API path for the endpoint."""
        return "/api/v1/accounts/{name}/videos"

    @property
    def method(self) -> str:
        """HTTP method for the endpoint."""
        return "get"

    @property
    def response_model(self) -> type[VideoListResponse] | None:
        """Response model class."""
        return VideoListResponse

    def _get_kwargs(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Build request kwargs with parameter processing."""
        name = args[0]  # First positional argument

        # Map parameter names to API parameter names
        param_mapping = {
            "start": "start",
            "count": "count",
            "skipCount": "skip_count",
            "sort": "sort",
            "nsfw": "nsfw",
            "nsfwFlagsIncluded": "nsfw_flags_included",
            "nsfwFlagsExcluded": "nsfw_flags_excluded",
            "isLive": "is_live",
            "includeScheduledLive": "include_scheduled_live",
            "categoryOneOf": "category_one_of",
            "licenceOneOf": "licence_one_of",
            "languageOneOf": "language_one_of",
            "tagsOneOf": "tags_one_of",
            "tagsAllOf": "tags_all_of",
            "isLocal": "is_local",
            "include": "include",
            "hasHLSFiles": "has_hls_files",
            "hasWebVideoFiles": "has_web_video_files",
            "host": "host",
            "autoTagOneOf": "auto_tag_one_of",
            "privacyOneOf": "privacy_one_of",
            "excludeAlreadyWatched": "exclude_already_watched",
            "search": "search",
        }

        # Build params dict with proper mapping
        params = {}
        for api_param, kwarg_name in param_mapping.items():
            if kwarg_name in kwargs:
                value = kwargs[kwarg_name]
                if hasattr(value, "value"):
                    params[api_param] = value.value
                else:
                    params[api_param] = value

        # Filter out UNSET and None values
        params = {k: v for k, v in params.items() if v is not Unset and v is not None}

        return {
            "method": self.method,
            "url": self.path.format(name=name),
            "params": params,
        }


# Backward compatibility functions
def sync_detailed(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    skip_count: Unset | GetAccountVideosSkipCount = GetAccountVideosSkipCount.FALSE,
    sort: Unset | GetAccountVideosSort = UNSET,
    nsfw: Unset | GetAccountVideosNsfw = UNSET,
    nsfw_flags_included: Unset | NSFWFlag = UNSET,
    nsfw_flags_excluded: Unset | NSFWFlag = UNSET,
    is_live: Unset | bool = UNSET,
    include_scheduled_live: Unset | bool = UNSET,
    category_one_of: Unset | int | list[int] = UNSET,
    licence_one_of: Unset | int | list[int] = UNSET,
    language_one_of: Unset | list[str] | str = UNSET,
    tags_one_of: Unset | list[str] | str = UNSET,
    tags_all_of: Unset | list[str] | str = UNSET,
    is_local: Unset | bool = UNSET,
    include: Unset | GetAccountVideosInclude = UNSET,
    has_hls_files: Unset | bool = UNSET,
    has_web_video_files: Unset | bool = UNSET,
    host: Unset | str = UNSET,
    auto_tag_one_of: Unset | list[str] | str = UNSET,
    privacy_one_of: Unset | VideoPrivacySet = UNSET,
    exclude_already_watched: Unset | bool = UNSET,
    search: Unset | str = UNSET,
) -> Response[VideoListResponse]:
    """List videos of an account

    Args:
        name: The account name.
        client: The HTTP client instance.
        start: Starting index for pagination.
        count: Number of items per page. Default: 15.
        skip_count: Whether to skip count. Default: GetAccountVideosSkipCount.FALSE.
        sort: Sort videos by criteria.
        nsfw: NSFW parameter.
        nsfw_flags_included: NSFW flags to include.
        nsfw_flags_excluded: NSFW flags to exclude.
        is_live: Whether videos are live.
        include_scheduled_live: Whether to include scheduled live videos.
        category_one_of: Category filter.
        licence_one_of: Licence filter.
        language_one_of: Language filter.
        tags_one_of: Tags filter (one of).
        tags_all_of: Tags filter (all of).
        is_local: Whether videos are local.
        include: What to include.
        has_hls_files: Whether videos have HLS files.
        has_web_video_files: Whether videos have web video files.
        host: Host filter.
        auto_tag_one_of: Auto tags filter.
        privacy_one_of: Privacy filter.
        exclude_already_watched: Whether to exclude already watched videos.
        search: Search query.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VideoListResponse]
    """
    endpoint = GetAccountVideosEndpoint()
    return endpoint.sync_detailed(
        name,
        client=client,
        start=start,
        count=count,
        skip_count=skip_count,
        sort=sort,
        nsfw=nsfw,
        nsfw_flags_included=nsfw_flags_included,
        nsfw_flags_excluded=nsfw_flags_excluded,
        is_live=is_live,
        include_scheduled_live=include_scheduled_live,
        category_one_of=category_one_of,
        licence_one_of=licence_one_of,
        language_one_of=language_one_of,
        tags_one_of=tags_one_of,
        tags_all_of=tags_all_of,
        is_local=is_local,
        include=include,
        has_hls_files=has_hls_files,
        has_web_video_files=has_web_video_files,
        host=host,
        auto_tag_one_of=auto_tag_one_of,
        privacy_one_of=privacy_one_of,
        exclude_already_watched=exclude_already_watched,
        search=search,
    )


def sync(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    skip_count: Unset | GetAccountVideosSkipCount = GetAccountVideosSkipCount.FALSE,
    sort: Unset | GetAccountVideosSort = UNSET,
    nsfw: Unset | GetAccountVideosNsfw = UNSET,
    nsfw_flags_included: Unset | NSFWFlag = UNSET,
    nsfw_flags_excluded: Unset | NSFWFlag = UNSET,
    is_live: Unset | bool = UNSET,
    include_scheduled_live: Unset | bool = UNSET,
    category_one_of: Unset | int | list[int] = UNSET,
    licence_one_of: Unset | int | list[int] = UNSET,
    language_one_of: Unset | list[str] | str = UNSET,
    tags_one_of: Unset | list[str] | str = UNSET,
    tags_all_of: Unset | list[str] | str = UNSET,
    is_local: Unset | bool = UNSET,
    include: Unset | GetAccountVideosInclude = UNSET,
    has_hls_files: Unset | bool = UNSET,
    has_web_video_files: Unset | bool = UNSET,
    host: Unset | str = UNSET,
    auto_tag_one_of: Unset | list[str] | str = UNSET,
    privacy_one_of: Unset | VideoPrivacySet = UNSET,
    exclude_already_watched: Unset | bool = UNSET,
    search: Unset | str = UNSET,
) -> VideoListResponse | None:
    """List videos of an account

    Args:
        name: The account name.
        client: The HTTP client instance.
        start: Starting index for pagination.
        count: Number of items per page. Default: 15.
        skip_count: Whether to skip count. Default: GetAccountVideosSkipCount.FALSE.
        sort: Sort videos by criteria.
        nsfw: NSFW parameter.
        nsfw_flags_included: NSFW flags to include.
        nsfw_flags_excluded: NSFW flags to exclude.
        is_live: Whether videos are live.
        include_scheduled_live: Whether to include scheduled live videos.
        category_one_of: Category filter.
        licence_one_of: Licence filter.
        language_one_of: Language filter.
        tags_one_of: Tags filter (one of).
        tags_all_of: Tags filter (all of).
        is_local: Whether videos are local.
        include: What to include.
        has_hls_files: Whether videos have HLS files.
        has_web_video_files: Whether videos have web video files.
        host: Host filter.
        auto_tag_one_of: Auto tags filter.
        privacy_one_of: Privacy filter.
        exclude_already_watched: Whether to exclude already watched videos.
        search: Search query.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VideoListResponse | None
    """
    endpoint = GetAccountVideosEndpoint()
    return endpoint.sync(
        name,
        client=client,
        start=start,
        count=count,
        skip_count=skip_count,
        sort=sort,
        nsfw=nsfw,
        nsfw_flags_included=nsfw_flags_included,
        nsfw_flags_excluded=nsfw_flags_excluded,
        is_live=is_live,
        include_scheduled_live=include_scheduled_live,
        category_one_of=category_one_of,
        licence_one_of=licence_one_of,
        language_one_of=language_one_of,
        tags_one_of=tags_one_of,
        tags_all_of=tags_all_of,
        is_local=is_local,
        include=include,
        has_hls_files=has_hls_files,
        has_web_video_files=has_web_video_files,
        host=host,
        auto_tag_one_of=auto_tag_one_of,
        privacy_one_of=privacy_one_of,
        exclude_already_watched=exclude_already_watched,
        search=search,
    )


async def asyncio_detailed(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    skip_count: Unset | GetAccountVideosSkipCount = GetAccountVideosSkipCount.FALSE,
    sort: Unset | GetAccountVideosSort = UNSET,
    nsfw: Unset | GetAccountVideosNsfw = UNSET,
    nsfw_flags_included: Unset | NSFWFlag = UNSET,
    nsfw_flags_excluded: Unset | NSFWFlag = UNSET,
    is_live: Unset | bool = UNSET,
    include_scheduled_live: Unset | bool = UNSET,
    category_one_of: Unset | int | list[int] = UNSET,
    licence_one_of: Unset | int | list[int] = UNSET,
    language_one_of: Unset | list[str] | str = UNSET,
    tags_one_of: Unset | list[str] | str = UNSET,
    tags_all_of: Unset | list[str] | str = UNSET,
    is_local: Unset | bool = UNSET,
    include: Unset | GetAccountVideosInclude = UNSET,
    has_hls_files: Unset | bool = UNSET,
    has_web_video_files: Unset | bool = UNSET,
    host: Unset | str = UNSET,
    auto_tag_one_of: Unset | list[str] | str = UNSET,
    privacy_one_of: Unset | VideoPrivacySet = UNSET,
    exclude_already_watched: Unset | bool = UNSET,
    search: Unset | str = UNSET,
) -> Response[VideoListResponse]:
    """List videos of an account

    Args:
        name: The account name.
        client: The HTTP client instance.
        start: Starting index for pagination.
        count: Number of items per page. Default: 15.
        skip_count: Whether to skip count. Default: GetAccountVideosSkipCount.FALSE.
        sort: Sort videos by criteria.
        nsfw: NSFW parameter.
        nsfw_flags_included: NSFW flags to include.
        nsfw_flags_excluded: NSFW flags to exclude.
        is_live: Whether videos are live.
        include_scheduled_live: Whether to include scheduled live videos.
        category_one_of: Category filter.
        licence_one_of: Licence filter.
        language_one_of: Language filter.
        tags_one_of: Tags filter (one of).
        tags_all_of: Tags filter (all of).
        is_local: Whether videos are local.
        include: What to include.
        has_hls_files: Whether videos have HLS files.
        has_web_video_files: Whether videos have web video files.
        host: Host filter.
        auto_tag_one_of: Auto tags filter.
        privacy_one_of: Privacy filter.
        exclude_already_watched: Whether to exclude already watched videos.
        search: Search query.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VideoListResponse]
    """
    endpoint = GetAccountVideosEndpoint()
    return await endpoint.asyncio_detailed(
        name,
        client=client,
        start=start,
        count=count,
        skip_count=skip_count,
        sort=sort,
        nsfw=nsfw,
        nsfw_flags_included=nsfw_flags_included,
        nsfw_flags_excluded=nsfw_flags_excluded,
        is_live=is_live,
        include_scheduled_live=include_scheduled_live,
        category_one_of=category_one_of,
        licence_one_of=licence_one_of,
        language_one_of=language_one_of,
        tags_one_of=tags_one_of,
        tags_all_of=tags_all_of,
        is_local=is_local,
        include=include,
        has_hls_files=has_hls_files,
        has_web_video_files=has_web_video_files,
        host=host,
        auto_tag_one_of=auto_tag_one_of,
        privacy_one_of=privacy_one_of,
        exclude_already_watched=exclude_already_watched,
        search=search,
    )


async def asyncio(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    skip_count: Unset | GetAccountVideosSkipCount = GetAccountVideosSkipCount.FALSE,
    sort: Unset | GetAccountVideosSort = UNSET,
    nsfw: Unset | GetAccountVideosNsfw = UNSET,
    nsfw_flags_included: Unset | NSFWFlag = UNSET,
    nsfw_flags_excluded: Unset | NSFWFlag = UNSET,
    is_live: Unset | bool = UNSET,
    include_scheduled_live: Unset | bool = UNSET,
    category_one_of: Unset | int | list[int] = UNSET,
    licence_one_of: Unset | int | list[int] = UNSET,
    language_one_of: Unset | list[str] | str = UNSET,
    tags_one_of: Unset | list[str] | str = UNSET,
    tags_all_of: Unset | list[str] | str = UNSET,
    is_local: Unset | bool = UNSET,
    include: Unset | GetAccountVideosInclude = UNSET,
    has_hls_files: Unset | bool = UNSET,
    has_web_video_files: Unset | bool = UNSET,
    host: Unset | str = UNSET,
    auto_tag_one_of: Unset | list[str] | str = UNSET,
    privacy_one_of: Unset | VideoPrivacySet = UNSET,
    exclude_already_watched: Unset | bool = UNSET,
    search: Unset | str = UNSET,
) -> VideoListResponse | None:
    """List videos of an account

    Args:
        name: The account name.
        client: The HTTP client instance.
        start: Starting index for pagination.
        count: Number of items per page. Default: 15.
        skip_count: Whether to skip count. Default: GetAccountVideosSkipCount.FALSE.
        sort: Sort videos by criteria.
        nsfw: NSFW parameter.
        nsfw_flags_included: NSFW flags to include.
        nsfw_flags_excluded: NSFW flags to exclude.
        is_live: Whether videos are live.
        include_scheduled_live: Whether to include scheduled live videos.
        category_one_of: Category filter.
        licence_one_of: Licence filter.
        language_one_of: Language filter.
        tags_one_of: Tags filter (one of).
        tags_all_of: Tags filter (all of).
        is_local: Whether videos are local.
        include: What to include.
        has_hls_files: Whether videos have HLS files.
        has_web_video_files: Whether videos have web video files.
        host: Host filter.
        auto_tag_one_of: Auto tags filter.
        privacy_one_of: Privacy filter.
        exclude_already_watched: Whether to exclude already watched videos.
        search: Search query.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VideoListResponse | None
    """
    endpoint = GetAccountVideosEndpoint()
    return await endpoint.asyncio(
        name,
        client=client,
        start=start,
        count=count,
        skip_count=skip_count,
        sort=sort,
        nsfw=nsfw,
        nsfw_flags_included=nsfw_flags_included,
        nsfw_flags_excluded=nsfw_flags_excluded,
        is_live=is_live,
        include_scheduled_live=include_scheduled_live,
        category_one_of=category_one_of,
        licence_one_of=licence_one_of,
        language_one_of=language_one_of,
        tags_one_of=tags_one_of,
        tags_all_of=tags_all_of,
        is_local=is_local,
        include=include,
        has_hls_files=has_hls_files,
        has_web_video_files=has_web_video_files,
        host=host,
        auto_tag_one_of=auto_tag_one_of,
        privacy_one_of=privacy_one_of,
        exclude_already_watched=exclude_already_watched,
        search=search,
    )
