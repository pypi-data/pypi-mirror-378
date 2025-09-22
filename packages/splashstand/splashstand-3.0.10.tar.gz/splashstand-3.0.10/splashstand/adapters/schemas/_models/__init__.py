import typing as t
from datetime import date, time, timedelta
from uuid import UUID

import arrow
import uuid_utils
from acb.depends import depends
from inflection import titleize, underscore
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_utils import (
    ArrowType,
    ChoiceType,
    ColorType,
    CountryType,
    CurrencyType,
    EmailType,
    LocaleType,
)
from sqlalchemy_utils.types import PhoneNumberType, URLType
from sqlmodel import Field, SQLModel

data_type_map = dict(
    Boole=bool,
    Date=date,
    DateTime=ArrowType,
    Duration=timedelta,
    Time=time,
    Number=float,
    Integer=int,
    Float=float,
    Text=str,
    CssSelectorType=str,
    PronounceableText=str,
    URL=URLType,
    XPathType=str,
    choice=ChoiceType,
    email=EmailType,
    currency=CurrencyType,
    phonenumber=PhoneNumberType,
    country=CountryType,
    locale=LocaleType,
    color=ColorType,
)


def primary_key_factory() -> t.Any:
    return UUID(str(uuid_utils.uuid7()))


def get_current_user_id() -> int:
    auth = depends.get()
    return auth.current_user.identity


class ThingMixin(BaseModel, extra="allow", arbitrary_types_allowed=True):
    name: str = Field(index=True)
    description: str | None = Field(default=None)
    url: HttpUrl | None = Field(default=None, sa_type=URLType)
    same_as: HttpUrl | None = Field(default=None, sa_type=URLType)
    visible: bool = Field(default=True, exclude=True)


class SchemaModel(SQLModel, ThingMixin):  # type: ignore
    __table_args__ = {"extend_existing": True}
    __mapper_args__ = {"eager_defaults": True}
    id: t.Optional[UUID] = Field(default_factory=primary_key_factory, primary_key=True)
    date_created: t.Optional[ArrowType] = Field(
        default_factory=arrow.utcnow, alias="created_at", sa_type=ArrowType
    )
    date_modified: t.Optional[ArrowType] = Field(
        default_factory=arrow.utcnow,
        alias="last_edited_at",
        sa_type=ArrowType,
        sa_column_kwargs=dict(onupdate=arrow.utcnow),
    )
    maintainer: t.Optional[str] = Field(
        default_factory=get_current_user_id, alias="created_by"
    )
    editor: t.Optional[str] = Field(
        default_factory=get_current_user_id,
        sa_column_kwargs=dict(onupdate=get_current_user_id),
        alias="last_edited_by",
    )

    @declared_attr  # type: ignore
    @classmethod  # type: ignore
    def __tablename__(cls) -> str:  # type: ignore
        return underscore(cls.__name__)

    def __str__(self) -> str:
        return getattr(self, "name") or titleize(self.__class__.__name__)

    async def save(self) -> None:
        sql = depends.get()
        async with sql.get_session() as session:
            session.add(self)
            await session.commit()
