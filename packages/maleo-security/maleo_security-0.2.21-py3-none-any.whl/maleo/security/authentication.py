from enum import StrEnum
from fastapi import status, HTTPException
from fastapi.requests import HTTPConnection
from pydantic import BaseModel, Field
from starlette.authentication import (
    AuthCredentials as StarletteCredentials,
    BaseUser as StarletteUser,
)
from typing import Callable, Generic, Literal, Optional, TypeVar, Union, overload
from uuid import UUID
from maleo.types.string import (
    ListOfStrings,
    OptionalListOfStrings,
    OptionalSequenceOfStrings,
)
from maleo.types.uuid import OptionalUUID


class ConversionDestination(StrEnum):
    BASE = "base"
    TENANT = "tenant"
    SYSTEM = "system"


class RequestCredentials(StarletteCredentials):
    def __init__(
        self,
        user_id: OptionalUUID = None,
        organization_id: OptionalUUID = None,
        roles: OptionalSequenceOfStrings = None,
        scopes: OptionalSequenceOfStrings = None,
    ):
        super().__init__(scopes)
        self.user_id = user_id
        self.organization_id = organization_id
        self.roles = [] if roles is None else list(roles)


class RequestUser(StarletteUser):
    def __init__(
        self, authenticated: bool = False, username: str = "", email: str = ""
    ) -> None:
        self._authenticated = authenticated
        self._username = username
        self._email = email

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated

    @property
    def display_name(self) -> str:
        return self._username

    @property
    def identity(self) -> str:
        return self._email


UserIdT = TypeVar("UserIdT", bound=OptionalUUID)
OrganizationIdT = TypeVar("OrganizationIdT", bound=OptionalUUID)
RolesT = TypeVar("RolesT", bound=OptionalListOfStrings)
ScopesT = TypeVar("ScopesT", bound=OptionalListOfStrings)


class GenericCredentials(BaseModel, Generic[UserIdT, OrganizationIdT, RolesT, ScopesT]):
    user_id: UserIdT = Field(..., description="User")
    organization_id: OrganizationIdT = Field(..., description="Organization")
    roles: RolesT = Field(..., description="Roles")
    scopes: ScopesT = Field(..., description="Scopes")


class BaseCredentials(
    GenericCredentials[
        OptionalUUID,
        OptionalUUID,
        OptionalListOfStrings,
        OptionalListOfStrings,
    ]
):
    pass


class TenantCredentials(GenericCredentials[UUID, UUID, ListOfStrings, ListOfStrings]):
    pass


class SystemCredentials(GenericCredentials[UUID, None, ListOfStrings, ListOfStrings]):
    organization_id: None = None


AnyCredentials = Union[BaseCredentials, TenantCredentials, SystemCredentials]
AnyCredentialsT = TypeVar("AnyCredentialsT", bound=AnyCredentials)


class CredentialsMixin(BaseModel, Generic[AnyCredentialsT]):
    credentials: AnyCredentialsT = Field(..., description="Credentials")


IsAuthenticatedT = TypeVar("IsAuthenticatedT", bound=bool)


class GenericUser(BaseModel, Generic[IsAuthenticatedT]):
    is_authenticated: IsAuthenticatedT = Field(..., description="Authenticated")
    display_name: str = Field("", description="Username")
    identity: str = Field("", description="Email")


class BaseUser(GenericUser[bool]):
    is_authenticated: bool = Field(..., description="Authenticated")


class AuthenticatedUser(GenericUser[Literal[True]]):
    is_authenticated: Literal[True] = True


AnyUser = Union[BaseUser, AuthenticatedUser]
AnyUserT = TypeVar("AnyUserT", bound=AnyUser)


class UserMixin(BaseModel, Generic[AnyUserT]):
    user: AnyUserT = Field(..., description="User")


class GenericAuthentication(
    UserMixin[AnyUserT],
    CredentialsMixin[AnyCredentialsT],
    Generic[AnyCredentialsT, AnyUserT],
):
    @classmethod
    def _validate_request_credentials(cls, conn: HTTPConnection):
        if not isinstance(conn.auth, RequestCredentials):
            raise HTTPException(
                status_code=401,
                detail=f"Invalid type of request's credentials: '{type(conn.auth)}'",
            )

    @classmethod
    def _validate_request_user(cls, conn: HTTPConnection):
        if not isinstance(conn.user, RequestUser):
            raise HTTPException(
                status_code=401,
                detail=f"Invalid type of request's user: '{type(conn.user)}'",
            )


class BaseAuthentication(GenericAuthentication[BaseCredentials, BaseUser]):
    @classmethod
    def extract(
        cls,
        conn: HTTPConnection,
        /,
    ) -> "BaseAuthentication":
        try:
            # validate credentials
            cls._validate_request_credentials(conn=conn)
            credentials = BaseCredentials.model_validate(
                conn.auth, from_attributes=True
            )

            # validate user
            cls._validate_request_user(conn=conn)
            user = BaseUser.model_validate(conn.user, from_attributes=True)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Unable to validate {cls.__name__}: '{str(e)}'",
            )

        return cls(credentials=credentials, user=user)

    @classmethod
    def as_dependency(cls) -> Callable[..., "BaseAuthentication"]:
        """Create a FastAPI dependency for this authentication."""

        def dependency(conn: HTTPConnection) -> "BaseAuthentication":
            return cls.extract(conn)

        return dependency


class TenantAuthentication(GenericAuthentication[TenantCredentials, AuthenticatedUser]):
    @classmethod
    def extract(
        cls,
        conn: HTTPConnection,
        /,
    ) -> "TenantAuthentication":
        try:
            # validate credentials
            cls._validate_request_credentials(conn=conn)
            credentials = TenantCredentials.model_validate(
                conn.auth, from_attributes=True
            )

            # validate user
            cls._validate_request_user(conn=conn)
            user = AuthenticatedUser.model_validate(conn.user, from_attributes=True)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Unable to validate {cls.__name__}: '{str(e)}'",
            )

        return cls(credentials=credentials, user=user)

    @classmethod
    def as_dependency(cls) -> Callable[..., "TenantAuthentication"]:
        """Create a FastAPI dependency for this authentication."""

        def dependency(conn: HTTPConnection) -> "TenantAuthentication":
            return cls.extract(conn)

        return dependency

    def to_base(self) -> BaseAuthentication:
        return BaseAuthentication.model_validate(self.model_dump())


class SystemAuthentication(GenericAuthentication[SystemCredentials, AuthenticatedUser]):
    @classmethod
    def extract(
        cls,
        conn: HTTPConnection,
        /,
    ) -> "SystemAuthentication":
        try:
            # validate credentials
            cls._validate_request_credentials(conn=conn)
            credentials = SystemCredentials.model_validate(
                conn.auth, from_attributes=True
            )

            # validate user
            cls._validate_request_user(conn=conn)
            user = AuthenticatedUser.model_validate(conn.user, from_attributes=True)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Unable to validate {cls.__name__}: '{str(e)}'",
            )

        return cls(credentials=credentials, user=user)

    @classmethod
    def as_dependency(cls) -> Callable[..., "SystemAuthentication"]:
        """Create a FastAPI dependency for this authentication."""

        def dependency(conn: HTTPConnection) -> "SystemAuthentication":
            return cls.extract(conn)

        return dependency

    def to_base(self) -> BaseAuthentication:
        return BaseAuthentication.model_validate(self.model_dump())


AnyAuthentication = Union[
    BaseAuthentication, TenantAuthentication, SystemAuthentication
]
AnyAuthenticationT = TypeVar("AnyAuthenticationT", bound=AnyAuthentication)
OptionalAnyAuthentication = Optional[AnyAuthentication]
OptionalAnyAuthenticationT = TypeVar(
    "OptionalAnyAuthenticationT", bound=OptionalAnyAuthentication
)


class AuthenticationMixin(BaseModel, Generic[OptionalAnyAuthenticationT]):
    authentication: OptionalAnyAuthenticationT = Field(
        ..., description="Authentication"
    )


class OptionalAuthenticationMixin(BaseModel, Generic[AnyAuthenticationT]):
    authentication: Optional[AnyAuthenticationT] = Field(
        ..., description="Authentication. (Optional)"
    )


@overload
def convert(
    destination: Literal[ConversionDestination.BASE],
    *,
    authentication: Union[TenantAuthentication, SystemAuthentication],
) -> BaseAuthentication: ...
@overload
def convert(
    destination: Literal[ConversionDestination.TENANT],
    *,
    authentication: BaseAuthentication,
) -> TenantAuthentication: ...
@overload
def convert(
    destination: Literal[ConversionDestination.SYSTEM],
    *,
    authentication: BaseAuthentication,
) -> BaseAuthentication: ...
def convert(
    destination: ConversionDestination, *, authentication: AnyAuthentication
) -> AnyAuthentication:
    if destination is ConversionDestination.BASE:
        return BaseAuthentication.model_validate(authentication.model_dump())
    elif destination is ConversionDestination.TENANT:
        if isinstance(authentication, SystemAuthentication):
            raise TypeError(
                "Failed converting SystemAuthentication to TenantAuthentication",
                "Both authentications can not be converted into one another",
            )
        return TenantAuthentication.model_validate(authentication.model_dump())
    elif destination is ConversionDestination.SYSTEM:
        if isinstance(authentication, TenantAuthentication):
            raise TypeError(
                "Failed converting TenantAuthentication to SystemAuthentication",
                "Both authentications can not be converted into one another",
            )
        return SystemAuthentication.model_validate(authentication.model_dump())
