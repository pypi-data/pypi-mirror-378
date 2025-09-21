# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = [
    "MemoryListParams",
    "Filters",
    "FiltersOr",
    "FiltersOrOr",
    "FiltersOrOrUnionMember0",
    "FiltersOrOrOr",
    "FiltersOrOrAnd",
    "FiltersAnd",
    "FiltersAndAnd",
    "FiltersAndAndUnionMember0",
    "FiltersAndAndOr",
    "FiltersAndAndAnd",
]


class MemoryListParams(TypedDict, total=False):
    container_tags: Annotated[SequenceNotStr[str], PropertyInfo(alias="containerTags")]
    """Optional tags this document should be containerized by.

    This can be an ID for your user, a project ID, or any other identifier you wish
    to use to group documents.
    """

    filters: Filters
    """Optional filters to apply to the search. Can be a JSON string or Query object."""

    include_content: Annotated[bool, PropertyInfo(alias="includeContent")]
    """Whether to include the content field in the response.

    Warning: This can make responses significantly larger.
    """

    limit: Union[str, float]
    """Number of items per page"""

    order: Literal["asc", "desc"]
    """Sort order"""

    page: Union[str, float]
    """Page number to fetch"""

    sort: Literal["createdAt", "updatedAt"]
    """Field to sort by"""


class FiltersOrOrUnionMember0(TypedDict, total=False):
    key: Required[str]

    value: Required[str]

    filter_type: Annotated[Literal["metadata", "numeric", "array_contains"], PropertyInfo(alias="filterType")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[object], PropertyInfo(alias="OR")]]


class FiltersOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[object], PropertyInfo(alias="AND")]]


FiltersOrOr: TypeAlias = Union[FiltersOrOrUnionMember0, FiltersOrOrOr, FiltersOrOrAnd]


class FiltersOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOr], PropertyInfo(alias="OR")]]


class FiltersAndAndUnionMember0(TypedDict, total=False):
    key: Required[str]

    value: Required[str]

    filter_type: Annotated[Literal["metadata", "numeric", "array_contains"], PropertyInfo(alias="filterType")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[object], PropertyInfo(alias="OR")]]


class FiltersAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[object], PropertyInfo(alias="AND")]]


FiltersAndAnd: TypeAlias = Union[FiltersAndAndUnionMember0, FiltersAndAndOr, FiltersAndAndAnd]


class FiltersAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAnd], PropertyInfo(alias="AND")]]


Filters: TypeAlias = Union[FiltersOr, FiltersAnd]
