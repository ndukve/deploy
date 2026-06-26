"""Errors"""

from typing import Sequence, Any, Mapping

from starlette import status
from fastapi.exceptions import HTTPException


class BackendError(RuntimeError):
    """Failure from a dependent backend"""


class DBError(RuntimeError):
    """Undefined DB error"""


class DBFetchError(ValueError, DBError):
    """Various issues when fetching an object that are input dependent"""


class NotFound(DBFetchError, HTTPException):
    """Object was not found"""

    def __init__(self, *args: Sequence[Any], **kwargs: Mapping[str, Any]) -> None:
        """make us also 404 HTTP error"""
        _ = args, kwargs
        # We need to specify the correct superclass init
        super(HTTPException, self).__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
        )


class Deleted(NotFound):
    """Object was deleted"""


class ForbiddenOperation(RuntimeError):
    """Forbidden operation"""
