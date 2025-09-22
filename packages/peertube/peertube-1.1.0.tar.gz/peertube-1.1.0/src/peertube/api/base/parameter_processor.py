from typing import Any

from peertube.types import UNSET, Unset


def process_parameters(params: dict[str, Any]) -> dict[str, Any]:
    """Process and filter parameters, removing UNSET and None values.

    Args:
        params: Dictionary of parameters.

    Returns:
        Filtered dictionary with only set values.
    """
    return {k: v for k, v in params.items() if v is not UNSET and v is not None}


def build_query_params(**kwargs: Unset | Any) -> dict[str, Any]:
    """Build query parameters from keyword arguments, filtering out UNSET and None.

    Args:
        **kwargs: Parameter values.

    Returns:
        Dictionary of query parameters.
    """
    return {
        key: value
        for key, value in kwargs.items()
        if value is not UNSET and value is not None
    }


def process_enum_param(value: Any) -> Any:
    """Process enum parameters, converting to their values if they have a value attribute.

    Args:
        value: The parameter value.

    Returns:
        Processed value.
    """
    if hasattr(value, "value"):
        return value.value
    return value


def build_complex_params(**kwargs: Unset | Any) -> dict[str, Any]:
    """Build complex query parameters with enum processing and filtering.

    Args:
        **kwargs: Parameter values that may include enums.

    Returns:
        Dictionary of processed query parameters.
    """
    params: dict[str, Any] = {}
    for key, value in kwargs.items():
        if value is UNSET or value is None:
            continue
        params[key] = process_enum_param(value)
    return params
