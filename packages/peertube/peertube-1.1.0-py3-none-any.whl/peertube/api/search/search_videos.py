import datetime
from http import HTTPStatus
from typing import Any, cast

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.nsfw_flag import NSFWFlag
from peertube.models.search_videos_include import SearchVideosInclude
from peertube.models.search_videos_nsfw import SearchVideosNsfw
from peertube.models.search_videos_search_target import SearchVideosSearchTarget
from peertube.models.search_videos_skip_count import SearchVideosSkipCount
from peertube.models.search_videos_sort import SearchVideosSort
from peertube.models.video_list_response import VideoListResponse
from peertube.models.video_privacy_set import VideoPrivacySet
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    *,
    search: str,
    uuids: Unset | Any = UNSET,
    search_target: Unset | SearchVideosSearchTarget = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    skip_count: Unset | SearchVideosSkipCount = SearchVideosSkipCount.FALSE,
    sort: Unset | SearchVideosSort = UNSET,
    nsfw: Unset | SearchVideosNsfw = UNSET,
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
    include: Unset | SearchVideosInclude = UNSET,
    has_hls_files: Unset | bool = UNSET,
    has_web_video_files: Unset | bool = UNSET,
    host: Unset | str = UNSET,
    auto_tag_one_of: Unset | list[str] | str = UNSET,
    privacy_one_of: Unset | VideoPrivacySet = UNSET,
    exclude_already_watched: Unset | bool = UNSET,
    start_date: Unset | datetime.datetime = UNSET,
    end_date: Unset | datetime.datetime = UNSET,
    originally_published_start_date: Unset | datetime.datetime = UNSET,
    originally_published_end_date: Unset | datetime.datetime = UNSET,
    duration_min: Unset | int = UNSET,
    duration_max: Unset | int = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["search"] = search

    params["uuids"] = uuids
    json_search_target: Unset | str = UNSET
    if not isinstance(search_target, Unset):
        json_search_target = search_target.value

    params["searchTarget"] = json_search_target

    params["start"] = start

    params["count"] = count
    json_skip_count: Unset | str = UNSET
    if not isinstance(skip_count, Unset):
        json_skip_count = skip_count.value

    params["skipCount"] = json_skip_count
    json_sort: Unset | str = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort
    json_nsfw: Unset | str = UNSET
    if not isinstance(nsfw, Unset):
        json_nsfw = nsfw.value

    params["nsfw"] = json_nsfw
    json_nsfw_flags_included: Unset | int = UNSET
    if not isinstance(nsfw_flags_included, Unset):
        json_nsfw_flags_included = nsfw_flags_included.value

    params["nsfwFlagsIncluded"] = json_nsfw_flags_included
    json_nsfw_flags_excluded: Unset | int = UNSET
    if not isinstance(nsfw_flags_excluded, Unset):
        json_nsfw_flags_excluded = nsfw_flags_excluded.value

    params["nsfwFlagsExcluded"] = json_nsfw_flags_excluded

    params["isLive"] = is_live

    params["includeScheduledLive"] = include_scheduled_live
    json_category_one_of: Unset | int | list[int]
    if isinstance(category_one_of, Unset):
        json_category_one_of = UNSET
    elif isinstance(category_one_of, list):
        json_category_one_of = category_one_of

    else:
        json_category_one_of = category_one_of
    params["categoryOneOf"] = json_category_one_of
    json_licence_one_of: Unset | int | list[int]
    if isinstance(licence_one_of, Unset):
        json_licence_one_of = UNSET
    elif isinstance(licence_one_of, list):
        json_licence_one_of = licence_one_of

    else:
        json_licence_one_of = licence_one_of
    params["licenceOneOf"] = json_licence_one_of
    json_language_one_of: Unset | list[str] | str
    if isinstance(language_one_of, Unset):
        json_language_one_of = UNSET
    elif isinstance(language_one_of, list):
        json_language_one_of = language_one_of

    else:
        json_language_one_of = language_one_of
    params["languageOneOf"] = json_language_one_of
    json_tags_one_of: Unset | list[str] | str
    if isinstance(tags_one_of, Unset):
        json_tags_one_of = UNSET
    elif isinstance(tags_one_of, list):
        json_tags_one_of = tags_one_of

    else:
        json_tags_one_of = tags_one_of
    params["tagsOneOf"] = json_tags_one_of
    json_tags_all_of: Unset | list[str] | str
    if isinstance(tags_all_of, Unset):
        json_tags_all_of = UNSET
    elif isinstance(tags_all_of, list):
        json_tags_all_of = tags_all_of

    else:
        json_tags_all_of = tags_all_of
    params["tagsAllOf"] = json_tags_all_of

    params["isLocal"] = is_local
    json_include: Unset | int = UNSET
    if not isinstance(include, Unset):
        json_include = include.value

    params["include"] = json_include

    params["hasHLSFiles"] = has_hls_files

    params["hasWebVideoFiles"] = has_web_video_files

    params["host"] = host
    json_auto_tag_one_of: Unset | list[str] | str
    if isinstance(auto_tag_one_of, Unset):
        json_auto_tag_one_of = UNSET
    elif isinstance(auto_tag_one_of, list):
        json_auto_tag_one_of = auto_tag_one_of

    else:
        json_auto_tag_one_of = auto_tag_one_of
    params["autoTagOneOf"] = json_auto_tag_one_of
    json_privacy_one_of: Unset | int = UNSET
    if not isinstance(privacy_one_of, Unset):
        json_privacy_one_of = privacy_one_of.value

    params["privacyOneOf"] = json_privacy_one_of

    params["excludeAlreadyWatched"] = exclude_already_watched
    json_start_date: Unset | str = UNSET
    if not isinstance(start_date, Unset):
        json_start_date = start_date.isoformat()
    params["startDate"] = json_start_date
    json_end_date: Unset | str = UNSET
    if not isinstance(end_date, Unset):
        json_end_date = end_date.isoformat()
    params["endDate"] = json_end_date
    json_originally_published_start_date: Unset | str = UNSET
    if not isinstance(originally_published_start_date, Unset):
        json_originally_published_start_date = (
            originally_published_start_date.isoformat()
        )
    params["originallyPublishedStartDate"] = json_originally_published_start_date
    json_originally_published_end_date: Unset | str = UNSET
    if not isinstance(originally_published_end_date, Unset):
        json_originally_published_end_date = originally_published_end_date.isoformat()
    params["originallyPublishedEndDate"] = json_originally_published_end_date

    params["durationMin"] = duration_min

    params["durationMax"] = duration_max
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/search/videos",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | VideoListResponse | None:
    if response.status_code == 200:
        response_200 = VideoListResponse.from_dict(response.json())

        return response_200
    if response.status_code == 500:
        response_500 = cast("Any", None)
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | VideoListResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    search: str,
    uuids: Unset | Any = UNSET,
    search_target: Unset | SearchVideosSearchTarget = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    skip_count: Unset | SearchVideosSkipCount = SearchVideosSkipCount.FALSE,
    sort: Unset | SearchVideosSort = UNSET,
    nsfw: Unset | SearchVideosNsfw = UNSET,
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
    include: Unset | SearchVideosInclude = UNSET,
    has_hls_files: Unset | bool = UNSET,
    has_web_video_files: Unset | bool = UNSET,
    host: Unset | str = UNSET,
    auto_tag_one_of: Unset | list[str] | str = UNSET,
    privacy_one_of: Unset | VideoPrivacySet = UNSET,
    exclude_already_watched: Unset | bool = UNSET,
    start_date: Unset | datetime.datetime = UNSET,
    end_date: Unset | datetime.datetime = UNSET,
    originally_published_start_date: Unset | datetime.datetime = UNSET,
    originally_published_end_date: Unset | datetime.datetime = UNSET,
    duration_min: Unset | int = UNSET,
    duration_max: Unset | int = UNSET,
) -> Response[Any | VideoListResponse]:
    """Search for videos on the PeerTube instance with detailed response information.
    Performs a video search on the PeerTube instance using various filtering criteria. If the user
    can make a remote URI search and the search string is a URI, the PeerTube instance will fetch
    the remote object and add it to its database for interaction via the REST API.

    Args:
        client: The authenticated or unauthenticated client for making requests.
        search: String to search for. Can be a video title, description, or URI.
        uuids: Filter results to specific video UUIDs.
        search_target: Whether to search locally or use search index. If search index is enabled
            by the administrator, you can override the default search target.
        start: Starting index for pagination (0-based).
        count: Maximum number of videos to return per page. Default: 15.
        skip_count: Whether to skip the total count calculation for performance.
        sort: Sort videos by criteria. Prefix with `-` for descending order. Options include:
            `hot` (Reddit-like algorithm considering views, likes, dislikes, comments, and date), `best` (like hot but includes user history), `trending` (recent views), `views` (total view count), `publishedAt` (publication date).
        nsfw: Filter for NSFW content (show all, only NSFW, or only safe content).
        nsfw_flags_included: Include videos with specific NSFW flags. Can be combined with
            bitwise OR: 0 = NONE, 1=VIOLENT, 2 = EXPLICIT_SEX.
        nsfw_flags_excluded: Exclude videos with specific NSFW flags. Can be combined with
            bitwise OR: 0 = NONE, 1=VIOLENT, 2 = EXPLICIT_SEX.
        is_live: Filter for live videos only.
        include_scheduled_live: Include scheduled live videos in results.
        category_one_of: Filter by video category IDs. Can be a single ID or list of IDs.
        licence_one_of: Filter by video licence IDs. Can be a single ID or list of IDs.
        language_one_of: Filter by language codes. Can be a single language or list of languages.
        tags_one_of: Filter videos that have at least one of the specified tags.
        tags_all_of: Filter videos that have all of the specified tags.
        is_local: Filter for local videos only (hosted on this instance).
        include: Include additional video information in results. Administrators and moderators
            only. Can be combined with bitwise OR: 0 = NONE, 1=NOT_PUBLISHED_STATE, 2=BLACKLISTED, 4=BLOCKED_OWNER, 8=FILES, 16=CAPTIONS, 32 = VIDEO_SOURCE.
        has_hls_files: Filter for videos that have HLS streaming files.
        has_web_video_files: Filter for videos that have web-compatible video files.
        host: Filter by the hostname where videos are hosted.
        auto_tag_one_of: Filter by automatically generated tags.
        privacy_one_of: Filter by video privacy settings (public, unlisted, private, internal).
        exclude_already_watched: Exclude videos that the current user has already watched.
        start_date: Filter for videos published after this date.
        end_date: Filter for videos published before this date.
        originally_published_start_date: Filter for videos originally published after this date.
        originally_published_end_date: Filter for videos originally published before this date.
        duration_min: Filter for videos with at least this duration (in seconds).
        duration_max: Filter for videos with at most this duration (in seconds).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response object containing the status code, headers, and parsed video list data or error information.
    """

    kwargs = _get_kwargs(
        search=search,
        uuids=uuids,
        search_target=search_target,
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
        start_date=start_date,
        end_date=end_date,
        originally_published_start_date=originally_published_start_date,
        originally_published_end_date=originally_published_end_date,
        duration_min=duration_min,
        duration_max=duration_max,
    )

    response = client.get_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    search: str,
    uuids: Unset | Any = UNSET,
    search_target: Unset | SearchVideosSearchTarget = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    skip_count: Unset | SearchVideosSkipCount = SearchVideosSkipCount.FALSE,
    sort: Unset | SearchVideosSort = UNSET,
    nsfw: Unset | SearchVideosNsfw = UNSET,
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
    include: Unset | SearchVideosInclude = UNSET,
    has_hls_files: Unset | bool = UNSET,
    has_web_video_files: Unset | bool = UNSET,
    host: Unset | str = UNSET,
    auto_tag_one_of: Unset | list[str] | str = UNSET,
    privacy_one_of: Unset | VideoPrivacySet = UNSET,
    exclude_already_watched: Unset | bool = UNSET,
    start_date: Unset | datetime.datetime = UNSET,
    end_date: Unset | datetime.datetime = UNSET,
    originally_published_start_date: Unset | datetime.datetime = UNSET,
    originally_published_end_date: Unset | datetime.datetime = UNSET,
    duration_min: Unset | int = UNSET,
    duration_max: Unset | int = UNSET,
) -> Any | VideoListResponse | None:
    """Search for videos on the PeerTube instance.
    Performs a video search on the PeerTube instance using various filtering criteria. If the user
    can make a remote URI search and the search string is a URI, the PeerTube instance will fetch
    the remote object and add it to its database for interaction via the REST API.

    Args:
        client: The authenticated or unauthenticated client for making requests.
        search: String to search for. Can be a video title, description, or URI.
        uuids: Filter results to specific video UUIDs.
        search_target: Whether to search locally or use search index. If search index is enabled
            by the administrator, you can override the default search target.
        start: Starting index for pagination (0-based).
        count: Maximum number of videos to return per page. Default: 15.
        skip_count: Whether to skip the total count calculation for performance.
        sort: Sort videos by criteria. Prefix with `-` for descending order. Options include:
            `hot` (Reddit-like algorithm considering views, likes, dislikes, comments, and date), `best` (like hot but includes user history), `trending` (recent views), `views` (total view count), `publishedAt` (publication date).
        nsfw: Filter for NSFW content (show all, only NSFW, or only safe content).
        nsfw_flags_included: Include videos with specific NSFW flags. Can be combined with
            bitwise OR: 0 = NONE, 1=VIOLENT, 2 = EXPLICIT_SEX.
        nsfw_flags_excluded: Exclude videos with specific NSFW flags. Can be combined with
            bitwise OR: 0 = NONE, 1=VIOLENT, 2 = EXPLICIT_SEX.
        is_live: Filter for live videos only.
        include_scheduled_live: Include scheduled live videos in results.
        category_one_of: Filter by video category IDs. Can be a single ID or list of IDs.
        licence_one_of: Filter by video licence IDs. Can be a single ID or list of IDs.
        language_one_of: Filter by language codes. Can be a single language or list of languages.
        tags_one_of: Filter videos that have at least one of the specified tags.
        tags_all_of: Filter videos that have all of the specified tags.
        is_local: Filter for local videos only (hosted on this instance).
        include: Include additional video information in results. Administrators and moderators
            only. Can be combined with bitwise OR: 0 = NONE, 1=NOT_PUBLISHED_STATE, 2=BLACKLISTED, 4=BLOCKED_OWNER, 8=FILES, 16=CAPTIONS, 32 = VIDEO_SOURCE.
        has_hls_files: Filter for videos that have HLS streaming files.
        has_web_video_files: Filter for videos that have web-compatible video files.
        host: Filter by the hostname where videos are hosted.
        auto_tag_one_of: Filter by automatically generated tags.
        privacy_one_of: Filter by video privacy settings (public, unlisted, private, internal).
        exclude_already_watched: Exclude videos that the current user has already watched.
        start_date: Filter for videos published after this date.
        end_date: Filter for videos published before this date.
        originally_published_start_date: Filter for videos originally published after this date.
        originally_published_end_date: Filter for videos originally published before this date.
        duration_min: Filter for videos with at least this duration (in seconds).
        duration_max: Filter for videos with at most this duration (in seconds).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        The parsed video list response data, or None if the search index is unavailable.
    """

    return sync_detailed(
        client=client,
        search=search,
        uuids=uuids,
        search_target=search_target,
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
        start_date=start_date,
        end_date=end_date,
        originally_published_start_date=originally_published_start_date,
        originally_published_end_date=originally_published_end_date,
        duration_min=duration_min,
        duration_max=duration_max,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    search: str,
    uuids: Unset | Any = UNSET,
    search_target: Unset | SearchVideosSearchTarget = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    skip_count: Unset | SearchVideosSkipCount = SearchVideosSkipCount.FALSE,
    sort: Unset | SearchVideosSort = UNSET,
    nsfw: Unset | SearchVideosNsfw = UNSET,
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
    include: Unset | SearchVideosInclude = UNSET,
    has_hls_files: Unset | bool = UNSET,
    has_web_video_files: Unset | bool = UNSET,
    host: Unset | str = UNSET,
    auto_tag_one_of: Unset | list[str] | str = UNSET,
    privacy_one_of: Unset | VideoPrivacySet = UNSET,
    exclude_already_watched: Unset | bool = UNSET,
    start_date: Unset | datetime.datetime = UNSET,
    end_date: Unset | datetime.datetime = UNSET,
    originally_published_start_date: Unset | datetime.datetime = UNSET,
    originally_published_end_date: Unset | datetime.datetime = UNSET,
    duration_min: Unset | int = UNSET,
    duration_max: Unset | int = UNSET,
) -> Response[Any | VideoListResponse]:
    """Search for videos on the PeerTube instance asynchronously with detailed response information.
    Performs an asynchronous video search on the PeerTube instance using various filtering criteria.
    If the user can make a remote URI search and the search string is a URI, the PeerTube instance
    will fetch the remote object and add it to its database for interaction via the REST API.

    Args:
        client: The authenticated or unauthenticated client for making requests.
        search: String to search for. Can be a video title, description, or URI.
        uuids: Filter results to specific video UUIDs.
        search_target: Whether to search locally or use search index. If search index is enabled
            by the administrator, you can override the default search target.
        start: Starting index for pagination (0-based).
        count: Maximum number of videos to return per page. Default: 15.
        skip_count: Whether to skip the total count calculation for performance.
        sort: Sort videos by criteria. Prefix with `-` for descending order. Options include:
            `hot` (Reddit-like algorithm considering views, likes, dislikes, comments, and date), `best` (like hot but includes user history), `trending` (recent views), `views` (total view count), `publishedAt` (publication date).
        nsfw: Filter for NSFW content (show all, only NSFW, or only safe content).
        nsfw_flags_included: Include videos with specific NSFW flags. Can be combined with
            bitwise OR: 0 = NONE, 1=VIOLENT, 2 = EXPLICIT_SEX.
        nsfw_flags_excluded: Exclude videos with specific NSFW flags. Can be combined with
            bitwise OR: 0 = NONE, 1=VIOLENT, 2 = EXPLICIT_SEX.
        is_live: Filter for live videos only.
        include_scheduled_live: Include scheduled live videos in results.
        category_one_of: Filter by video category IDs. Can be a single ID or list of IDs.
        licence_one_of: Filter by video licence IDs. Can be a single ID or list of IDs.
        language_one_of: Filter by language codes. Can be a single language or list of languages.
        tags_one_of: Filter videos that have at least one of the specified tags.
        tags_all_of: Filter videos that have all of the specified tags.
        is_local: Filter for local videos only (hosted on this instance).
        include: Include additional video information in results. Administrators and moderators
            only. Can be combined with bitwise OR: 0 = NONE, 1=NOT_PUBLISHED_STATE, 2=BLACKLISTED, 4=BLOCKED_OWNER, 8=FILES, 16=CAPTIONS, 32 = VIDEO_SOURCE.
        has_hls_files: Filter for videos that have HLS streaming files.
        has_web_video_files: Filter for videos that have web-compatible video files.
        host: Filter by the hostname where videos are hosted.
        auto_tag_one_of: Filter by automatically generated tags.
        privacy_one_of: Filter by video privacy settings (public, unlisted, private, internal).
        exclude_already_watched: Exclude videos that the current user has already watched.
        start_date: Filter for videos published after this date.
        end_date: Filter for videos published before this date.
        originally_published_start_date: Filter for videos originally published after this date.
        originally_published_end_date: Filter for videos originally published before this date.
        duration_min: Filter for videos with at least this duration (in seconds).
        duration_max: Filter for videos with at most this duration (in seconds).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response object containing the status code, headers, and parsed video list data or error information.
    """

    kwargs = _get_kwargs(
        search=search,
        uuids=uuids,
        search_target=search_target,
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
        start_date=start_date,
        end_date=end_date,
        originally_published_start_date=originally_published_start_date,
        originally_published_end_date=originally_published_end_date,
        duration_min=duration_min,
        duration_max=duration_max,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    search: str,
    uuids: Unset | Any = UNSET,
    search_target: Unset | SearchVideosSearchTarget = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    skip_count: Unset | SearchVideosSkipCount = SearchVideosSkipCount.FALSE,
    sort: Unset | SearchVideosSort = UNSET,
    nsfw: Unset | SearchVideosNsfw = UNSET,
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
    include: Unset | SearchVideosInclude = UNSET,
    has_hls_files: Unset | bool = UNSET,
    has_web_video_files: Unset | bool = UNSET,
    host: Unset | str = UNSET,
    auto_tag_one_of: Unset | list[str] | str = UNSET,
    privacy_one_of: Unset | VideoPrivacySet = UNSET,
    exclude_already_watched: Unset | bool = UNSET,
    start_date: Unset | datetime.datetime = UNSET,
    end_date: Unset | datetime.datetime = UNSET,
    originally_published_start_date: Unset | datetime.datetime = UNSET,
    originally_published_end_date: Unset | datetime.datetime = UNSET,
    duration_min: Unset | int = UNSET,
    duration_max: Unset | int = UNSET,
) -> Any | VideoListResponse | None:
    """Search for videos on the PeerTube instance asynchronously.
    Performs an asynchronous video search on the PeerTube instance using various filtering criteria.
    If the user can make a remote URI search and the search string is a URI, the PeerTube instance
    will fetch the remote object and add it to its database for interaction via the REST API.

    Args:
        client: The authenticated or unauthenticated client for making requests.
        search: String to search for. Can be a video title, description, or URI.
        uuids: Filter results to specific video UUIDs.
        search_target: Whether to search locally or use search index. If search index is enabled
            by the administrator, you can override the default search target.
        start: Starting index for pagination (0-based).
        count: Maximum number of videos to return per page. Default: 15.
        skip_count: Whether to skip the total count calculation for performance.
        sort: Sort videos by criteria. Prefix with `-` for descending order. Options include:
            `hot` (Reddit-like algorithm considering views, likes, dislikes, comments, and date), `best` (like hot but includes user history), `trending` (recent views), `views` (total view count), `publishedAt` (publication date).
        nsfw: Filter for NSFW content (show all, only NSFW, or only safe content).
        nsfw_flags_included: Include videos with specific NSFW flags. Can be combined with
            bitwise OR: 0 = NONE, 1=VIOLENT, 2 = EXPLICIT_SEX.
        nsfw_flags_excluded: Exclude videos with specific NSFW flags. Can be combined with
            bitwise OR: 0 = NONE, 1=VIOLENT, 2 = EXPLICIT_SEX.
        is_live: Filter for live videos only.
        include_scheduled_live: Include scheduled live videos in results.
        category_one_of: Filter by video category IDs. Can be a single ID or list of IDs.
        licence_one_of: Filter by video licence IDs. Can be a single ID or list of IDs.
        language_one_of: Filter by language codes. Can be a single language or list of languages.
        tags_one_of: Filter videos that have at least one of the specified tags.
        tags_all_of: Filter videos that have all of the specified tags.
        is_local: Filter for local videos only (hosted on this instance).
        include: Include additional video information in results. Administrators and moderators
            only. Can be combined with bitwise OR: 0 = NONE, 1=NOT_PUBLISHED_STATE, 2=BLACKLISTED, 4=BLOCKED_OWNER, 8=FILES, 16=CAPTIONS, 32 = VIDEO_SOURCE.
        has_hls_files: Filter for videos that have HLS streaming files.
        has_web_video_files: Filter for videos that have web-compatible video files.
        host: Filter by the hostname where videos are hosted.
        auto_tag_one_of: Filter by automatically generated tags.
        privacy_one_of: Filter by video privacy settings (public, unlisted, private, internal).
        exclude_already_watched: Exclude videos that the current user has already watched.
        start_date: Filter for videos published after this date.
        end_date: Filter for videos published before this date.
        originally_published_start_date: Filter for videos originally published after this date.
        originally_published_end_date: Filter for videos originally published before this date.
        duration_min: Filter for videos with at least this duration (in seconds).
        duration_max: Filter for videos with at most this duration (in seconds).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        The parsed video list response data, or None if the search index is unavailable.
    """

    return (
        await asyncio_detailed(
            client=client,
            search=search,
            uuids=uuids,
            search_target=search_target,
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
            start_date=start_date,
            end_date=end_date,
            originally_published_start_date=originally_published_start_date,
            originally_published_end_date=originally_published_end_date,
            duration_min=duration_min,
            duration_max=duration_max,
        )
    ).parsed
