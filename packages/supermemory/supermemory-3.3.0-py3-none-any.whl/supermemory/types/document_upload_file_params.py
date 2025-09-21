# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._types import FileTypes
from .._utils import PropertyInfo

__all__ = ["DocumentUploadFileParams"]


class DocumentUploadFileParams(TypedDict, total=False):
    file: Required[FileTypes]
    """File to upload and process"""

    container_tags: Annotated[str, PropertyInfo(alias="containerTags")]
    """Optional JSON string of container tags array.

    This can be an ID for your user, a project ID, or any other identifier you wish
    to use to group documents.
    """

    file_type: Annotated[str, PropertyInfo(alias="fileType")]
    """Optional file type override to force specific processing behavior.

    Valid values: text, pdf, tweet, google_doc, google_slide, google_sheet, image,
    video, notion_doc, webpage, onedrive
    """

    metadata: str
    """Optional metadata for the document as a JSON string.

    This is used to store additional information about the document. Keys must be
    strings and values can be strings, numbers, or booleans.
    """

    mime_type: Annotated[str, PropertyInfo(alias="mimeType")]
    """Required when fileType is 'image' or 'video'.

    Specifies the exact MIME type to use (e.g., 'image/png', 'image/jpeg',
    'video/mp4', 'video/webm')
    """
