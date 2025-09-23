from collections.abc import Iterable, Sequence
from Crypto.PublicKey.RSA import RsaKey
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from pydantic import BaseModel, Field, model_validator
from typing import Generic, Literal, Optional, Self, Tuple, TypeVar, Union, overload
from typing_extensions import Annotated
from uuid import UUID
from maleo.crypto.token import decode, encode
from maleo.enums.expiration import Expiration
from maleo.types.datetime import OptionalDatetime
from maleo.types.integer import OptionalInteger
from maleo.types.misc import BytesOrString
from maleo.types.string import ListOfStrings, OptionalListOfStrings, OptionalString
from maleo.types.uuid import OptionalUUID


class ConversionDestination(StrEnum):
    BASE = "base"
    TENANT = "tenant"
    SYSTEM = "system"


class Domain(StrEnum):
    TENANT = "tenant"
    SYSTEM = "system"


class Claim(BaseModel):
    iss: Annotated[OptionalString, Field(None, description="Issuer")] = None
    sub: Annotated[UUID, Field(..., description="Subject")]
    aud: Annotated[OptionalString, Field(None, description="Audience")] = None
    exp: Annotated[int, Field(..., description="Expired at")]
    iat: Annotated[int, Field(..., description="Issued at")]

    @classmethod
    def new_timestamp(
        cls, iat_dt: OptionalDatetime = None, exp_in: Expiration = Expiration.EXP_15MN
    ) -> Tuple[int, int]:
        if iat_dt is None:
            iat_dt = datetime.now(tz=timezone.utc)
        exp_dt = iat_dt + timedelta(seconds=exp_in.value)
        return int(iat_dt.timestamp()), int(exp_dt.timestamp())


OrganizationT = TypeVar("OrganizationT", bound=OptionalUUID)


class Credential(BaseModel, Generic[OrganizationT]):
    d: Domain = Field(..., description="Domain")
    o: OrganizationT = Field(..., description="Organization")
    r: Annotated[ListOfStrings, Field(..., min_length=1, description="Roles")]


class OldToken(Claim):
    iat_dt: Annotated[datetime, Field(..., description="Issued At Timestamp")]
    exp_dt: Annotated[datetime, Field(..., description="Expired At Timestamp")]
    sr: Annotated[str, Field(..., description="System role")]
    u_i: Annotated[int, Field(..., description="User's ID")]
    u_uu: Annotated[UUID, Field(..., description="User's UUID")]
    u_u: Annotated[str, Field(..., description="User's Username")]
    u_e: Annotated[str, Field(..., description="User's Email")]
    u_ut: Annotated[str, Field(..., description="User's type")]
    o_i: Annotated[OptionalInteger, Field(None, description="Organization's ID")] = None
    o_uu: Annotated[OptionalUUID, Field(None, description="Organization's UUID")] = None
    o_k: Annotated[OptionalString, Field(None, description="Organization's Key")] = None
    o_ot: Annotated[OptionalString, Field(None, description="Organization's type")] = (
        None
    )
    uor: Annotated[
        OptionalListOfStrings,
        Field(None, description="Organization's type", min_length=1),
    ] = None


class GenericToken(
    Credential[OrganizationT],
    Claim,
    Generic[OrganizationT],
):
    @classmethod
    def from_string(
        cls,
        token: str,
        key: Union[RsaKey, BytesOrString],
        audience: str | Iterable[str] | None = None,
        subject: OptionalString = None,
        issuer: str | Sequence[str] | None = None,
        leeway: float | timedelta = 0,
    ) -> "GenericToken[OrganizationT]":
        obj = decode(token, key, audience, subject, issuer, leeway)
        return cls.model_validate(obj)

    @property
    def scopes(self) -> ListOfStrings:
        return [f"{str(self.d)}:{str(r)}" for r in self.r]

    @model_validator(mode="after")
    def validate_credential(self) -> Self:
        return self

    @overload
    def to_string(
        self,
        key: RsaKey,
    ) -> str: ...
    @overload
    def to_string(
        self,
        key: BytesOrString,
        *,
        password: OptionalString = None,
    ) -> str: ...
    def to_string(
        self,
        key: Union[RsaKey, BytesOrString],
        *,
        password: OptionalString = None,
    ) -> str:
        if isinstance(key, RsaKey):
            return encode(
                payload=self.model_dump(mode="json", exclude_none=True),
                key=key,
            )
        else:
            return encode(
                payload=self.model_dump(mode="json", exclude_none=True),
                key=key,
                password=password,
            )


class BaseToken(GenericToken[OptionalUUID]):
    @classmethod
    def from_string(
        cls,
        token: str,
        key: Union[RsaKey, BytesOrString],
        audience: str | Iterable[str] | None = None,
        subject: OptionalString = None,
        issuer: str | Sequence[str] | None = None,
        leeway: float | timedelta = 0,
    ) -> "BaseToken":
        obj = decode(token, key, audience, subject, issuer, leeway)
        return cls.model_validate(obj)

    @classmethod
    def new(
        cls,
        *,
        sub: UUID,
        d: Domain,
        o: OptionalUUID = None,
        r: ListOfStrings,
        iss: OptionalString = None,
        aud: OptionalString = None,
        iat_dt: OptionalDatetime = None,
        exp_in: Expiration = Expiration.EXP_15MN,
    ) -> "BaseToken":
        iat, exp = cls.new_timestamp(iat_dt, exp_in)
        return cls(iss=iss, sub=sub, aud=aud, exp=exp, iat=iat, d=d, o=o, r=r)

    @overload
    def to_string(
        self,
        key: RsaKey,
    ) -> str: ...
    @overload
    def to_string(
        self,
        key: BytesOrString,
        *,
        password: OptionalString = None,
    ) -> str: ...
    def to_string(
        self,
        key: Union[RsaKey, BytesOrString],
        *,
        password: OptionalString = None,
    ) -> str:
        if isinstance(key, RsaKey):
            return encode(
                payload=self.model_dump(mode="json", exclude_none=True),
                key=key,
            )
        else:
            return encode(
                payload=self.model_dump(mode="json", exclude_none=True),
                key=key,
                password=password,
            )


class TenantToken(GenericToken[UUID]):
    d: Domain = Domain.TENANT

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        if self.d is not Domain.TENANT:
            raise ValueError(f"Value of 'd' claim must be {Domain.TENANT}")
        if not isinstance(self.o, UUID):
            raise ValueError(f"Value of 'o' claim must be an UUID. Value: {self.o}")
        return self

    @classmethod
    def new(
        cls,
        *,
        sub: UUID,
        o: UUID,
        r: ListOfStrings,
        iss: OptionalString = None,
        aud: OptionalString = None,
        iat_dt: OptionalDatetime = None,
        exp_in: Expiration = Expiration.EXP_15MN,
    ) -> "TenantToken":
        iat, exp = cls.new_timestamp(iat_dt, exp_in)
        return cls(iss=iss, sub=sub, aud=aud, exp=exp, iat=iat, o=o, r=r)

    def to_base(self) -> BaseToken:
        return BaseToken.model_validate(self.model_dump())


class SystemToken(GenericToken[None]):
    d: Domain = Domain.SYSTEM
    o: None = None

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        if self.d is not Domain.SYSTEM:
            raise ValueError(f"Value of 'd' claim must be {Domain.SYSTEM}")
        if self.o is not None:
            raise ValueError(f"Value of 'o' claim must be None. Value: {self.o}")
        return self

    @classmethod
    def new(
        cls,
        *,
        sub: UUID,
        r: ListOfStrings,
        iss: OptionalString = None,
        aud: OptionalString = None,
        iat_dt: OptionalDatetime = None,
        exp_in: Expiration = Expiration.EXP_15MN,
    ) -> "SystemToken":
        iat, exp = cls.new_timestamp(iat_dt, exp_in)
        return cls(iss=iss, sub=sub, aud=aud, exp=exp, iat=iat, r=r)

    def to_base(self) -> BaseToken:
        return BaseToken.model_validate(self.model_dump())


AnyToken = Union[BaseToken, TenantToken, SystemToken]
AnyTokenT = TypeVar("AnyTokenT", bound=AnyToken)
OptionalAnyToken = Optional[AnyToken]
OptionalAnyTokenT = TypeVar("OptionalAnyTokenT", bound=OptionalAnyToken)


class TokenMixin(BaseModel, Generic[OptionalAnyTokenT]):
    token: OptionalAnyTokenT = Field(..., description="Token")


@overload
def convert(
    destination: Literal[ConversionDestination.BASE],
    *,
    token: Union[TenantToken, SystemToken],
) -> BaseToken: ...
@overload
def convert(
    destination: Literal[ConversionDestination.TENANT],
    *,
    token: BaseToken,
) -> TenantToken: ...
@overload
def convert(
    destination: Literal[ConversionDestination.SYSTEM],
    *,
    token: BaseToken,
) -> SystemToken: ...
def convert(
    destination: ConversionDestination,
    *,
    token: AnyToken,
) -> AnyToken:
    if destination is ConversionDestination.BASE:
        if isinstance(token, SystemToken):
            return BaseToken.model_validate(token.model_dump())
        elif isinstance(token, TenantToken):
            return BaseToken.model_validate(token.model_dump())
        elif isinstance(token, BaseToken):
            return token
    elif destination is ConversionDestination.TENANT:
        if isinstance(token, SystemToken):
            raise TypeError(
                "Failed converting SystemToken to TenantToken",
                "Both tokens can not be converted into one another",
            )
        elif isinstance(token, TenantToken):
            return token
        elif isinstance(token, BaseToken):
            return TenantToken.model_validate(token.model_dump())
    elif destination is ConversionDestination.SYSTEM:
        if isinstance(token, SystemToken):
            return token
        elif isinstance(token, TenantToken):
            raise TypeError(
                "Failed converting TenantToken to SystemToken",
                "Both tokens can not be converted into one another",
            )
        elif isinstance(token, BaseToken):
            return SystemToken.model_validate(token.model_dump())
