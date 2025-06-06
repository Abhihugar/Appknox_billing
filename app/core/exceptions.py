from typing import Any

from fastapi import HTTPException, status


class InvalidToken(HTTPException):
    def __init__(
        self,
        detail: Any = "Invalid token",
        headers: dict[str, Any] = None,
    ) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
        self.headers = headers


class NotAuthorized(HTTPException):
    def __init__(
        self,
        detail: Any = "Invalid Credentials",
        headers: dict[str, Any] = {"WWW-Authenticate": "Bearer"},
    ) -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
        self.headers = headers


class PermissionDenied(HTTPException):
    def __init__(
        self,
        detail: Any = "You don't have permission",
        headers: dict[str, Any] = None,
    ) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
        self.headers = headers


class InvalidUser(HTTPException):
    def __init__(
        self,
        detail: Any = "User is Blocked/Inactive",
        headers: dict[str, Any] = None,
    ) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
        self.headers = headers


class DuplicateEntry(HTTPException):
    def __init__(
        self,
        detail: Any = "Item already exists",
        headers: dict[str, Any] = None,
    ) -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
        self.headers = headers


class DBError(HTTPException):
    def __init__(
        self,
        detail: Any = "DB Error",
        headers: dict[str, Any] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )
        self.headers = headers


class ItemNotFound(HTTPException):
    def __init__(
        self,
        detail: Any = "Item not found",
        headers: dict[str, Any] = None,
    ) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        self.headers = headers


class ServerError(HTTPException):
    def __init__(
        self,
        detail: Any = "Server Error",
        headers: dict[str, Any] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )
        self.headers = headers



