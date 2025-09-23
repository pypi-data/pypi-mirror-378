import httpx
from enum import StrEnum
from fastapi import status, HTTPException, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from starlette.requests import HTTPConnection
from typing import (
    Annotated,
    Callable,
    Generator,
    Generic,
    Literal,
    Optional,
    TypeVar,
    Union,
    overload,
)
from maleo.enums.connection import Header
from maleo.types.string import OptionalString


class Scheme(StrEnum):
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"


class Source(StrEnum):
    HEADER = "header"
    STATE = "state"


class Authorization(BaseModel):
    scheme: Scheme = Field(..., description="Authorization's scheme")
    credentials: str = Field(..., description="Authorization's credentials")

    @overload
    @classmethod
    def extract(
        cls, source: Source, *, conn: HTTPConnection, auto_error: Literal[False]
    ) -> Optional["Authorization"]: ...
    @overload
    @classmethod
    def extract(
        cls, source: Source, *, conn: HTTPConnection, auto_error: Literal[True] = True
    ) -> "Authorization": ...
    @classmethod
    def extract(
        cls,
        source: Source = Source.STATE,
        *,
        conn: HTTPConnection,
        auto_error: bool = True,
    ) -> Optional["Authorization"]:
        if source is Source.HEADER:
            # Extract authorization from Authorization header
            token = conn.headers.get(Header.AUTHORIZATION.value, "")
            scheme, _, credentials = token.partition(" ")
            if token and scheme and credentials and scheme.lower() == "bearer":
                return cls(scheme=Scheme.BEARER_TOKEN, credentials=credentials)
            # Extract authorization from X-API-Key Header
            api_key = conn.headers.get(Header.X_API_KEY)
            if api_key is not None:
                return cls(scheme=Scheme.API_KEY, credentials=api_key)
            if auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or unable to determine authorization",
                )
            return None
        elif source is Source.STATE:
            authorization = conn.state.authorization
            if not isinstance(authorization, Authorization):
                if auto_error:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Invalid type of authorization state: {type(authorization)}",
                    )
                else:
                    return None
            return authorization

    @classmethod
    def assign_to_state(
        cls,
        conn: HTTPConnection,
        /,
    ):
        authorization = cls.extract(Source.HEADER, conn=conn, auto_error=False)
        conn.state.authorization = authorization

    @overload
    @classmethod
    def as_dependency(
        cls, *, source: Optional[Source] = None, auto_error: Literal[False]
    ) -> Callable[..., Optional["Authorization"]]: ...
    @overload
    @classmethod
    def as_dependency(
        cls, *, source: Optional[Source] = None, auto_error: Literal[True] = True
    ) -> Callable[..., "Authorization"]: ...
    @classmethod
    def as_dependency(
        cls, *, source: Optional[Source] = None, auto_error: bool = True
    ) -> Union[
        Callable[
            [HTTPConnection, Optional[HTTPAuthorizationCredentials], OptionalString],
            Optional["Authorization"],
        ],
        Callable[
            [HTTPConnection, Optional[HTTPAuthorizationCredentials], OptionalString],
            "Authorization",
        ],
    ]:
        def dependency(
            conn: HTTPConnection,
            bearer: Annotated[
                Optional[HTTPAuthorizationCredentials],
                Security(HTTPBearer(auto_error=False)),
            ],
            api_key: Annotated[
                OptionalString,
                Security(APIKeyHeader(name=Header.X_API_KEY.value, auto_error=False)),
            ],
        ) -> Optional["Authorization"]:
            if source is None:
                if bearer is not None:
                    return cls(
                        scheme=Scheme.BEARER_TOKEN, credentials=bearer.credentials
                    )
                if api_key is not None:
                    return cls(scheme=Scheme.API_KEY, credentials=api_key)
                if auto_error:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or unable to determine authorization",
                    )
                return None

            return cls.extract(source, conn=conn, auto_error=auto_error)

        return dependency


OptionalAuthorization = Optional[Authorization]
OptionalAuthorizationT = TypeVar("OptionalAuthorizationT", bound=OptionalAuthorization)


class AuthorizationMixin(BaseModel, Generic[OptionalAuthorizationT]):
    authorization: OptionalAuthorizationT = Field(
        ...,
        description="Authorization",
    )


class APIKeyAuth(httpx.Auth):
    def __init__(self, api_key: str) -> None:
        self._auth_header = self._build_auth_header(api_key)

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers[Header.X_API_KEY.value] = self._auth_header
        yield request

    def _build_auth_header(self, api_key: str) -> str:
        return api_key


class BearerAuth(httpx.Auth):
    def __init__(self, token: str) -> None:
        self._auth_header = self._build_auth_header(token)

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers[Header.AUTHORIZATION] = self._auth_header
        yield request

    def _build_auth_header(self, token: str) -> str:
        return f"Bearer {token}"


@overload
def generate_httpx_auth(
    scheme: Literal[Scheme.API_KEY], *, credentials: str
) -> APIKeyAuth: ...
@overload
def generate_httpx_auth(
    scheme: Literal[Scheme.BEARER_TOKEN], *, credentials: str
) -> BearerAuth: ...
def generate_httpx_auth(
    scheme: Scheme = Scheme.BEARER_TOKEN, *, credentials: str
) -> Union[
    APIKeyAuth,
    BearerAuth,
]:
    if scheme is Scheme.API_KEY:
        return APIKeyAuth(api_key=credentials)
    elif scheme is Scheme.BEARER_TOKEN:
        return BearerAuth(token=credentials)
