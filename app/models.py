from __future__ import annotations

from enum import Enum, unique
from typing import Union, Protocol
# from uuid import uuid4

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import ForeignKey, Column, Integer
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()
migrate = Migrate(db=db)


def serialize_coordinates(coordinates: tuple[float, float] | None) -> str | None:
    if coordinates is None:
        return None
    lat, lon = coordinates
    return f'{lat},{lon}'


def deserialize_coordinates(value: str | None) -> tuple[float, float] | None:
    if value is None or (isinstance(value, str) and value.strip() == ''):
        return None
    lat, lon = map(lambda coordinate: coordinate.strip(), value.split(','))
    return float(lat), float(lon)


class IsMapItem(Protocol):
    name: str
    camp_location: tuple[float, float] | None
    country_location: tuple[float, float] | None
    logo: str | None
    color: str | None
    linkable: bool


@unique
class Category(Enum):
    TEAM = 'team'
    POINT_OF_INTEREST = 'point of interest'
    WORKSHOP = 'workshop'
    STATION = 'station'


@unique
class Trend(Enum):
    UP = 'up'
    FLAT = 'flat'
    DOWN = 'down'


user_role_table = db.Table(
    'user_roles',
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)


class Role(db.Model):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    # alternative_id: Mapped[str] = mapped_column(unique=True, default_factory=uuid4)
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column()
    team_id: Mapped[Union[int, None]] = mapped_column(ForeignKey('teams.id'))
    team: Mapped[Union['Team', None]] = relationship(foreign_keys=[team_id], back_populates='members')
    roles: Mapped[list[Role]] = relationship('Role', secondary=user_role_table, backref='users')
    logo: Mapped[Union[str, None]] = mapped_column()

    def get_id(self) -> str:
        # return str(self.alternative_id)
        return str(self.id)


class PointOfInterest(db.Model):
    __tablename__ = 'pois'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    _camp_location: Mapped[Union[str, None]] = mapped_column()
    _country_location: Mapped[Union[str, None]] = mapped_column()
    logo: Mapped[Union[str, None]] = mapped_column()
    color: Mapped[Union[str, None]] = mapped_column()
    linkable: Mapped[bool] = mapped_column(default=False)
    category: Mapped[str] = mapped_column(default=Category.POINT_OF_INTEREST.value)

    @hybrid_property
    def camp_location(self) -> tuple[float, float] | None:
        return deserialize_coordinates(self._camp_location)

    @camp_location.setter
    def camp_location(self, value: tuple[float, float] | None) -> None:
        self._camp_location = serialize_coordinates(value)  # type: ignore

    @hybrid_property
    def country_location(self) -> tuple[float, float] | None:
        return deserialize_coordinates(self._country_location)

    @country_location.setter
    def country_location(self, value: tuple[float, float] | None) -> None:
        self._country_location = serialize_coordinates(value)  # type: ignore


class Team(db.Model):
    __tablename__ = 'teams'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    members: Mapped[list[User]] = relationship('User', back_populates='team')
    _camp_location: Mapped[Union[str, None]] = mapped_column()
    _country_location: Mapped[Union[str, None]] = mapped_column()
    logo: Mapped[Union[str, None]] = mapped_column()
    color: Mapped[Union[str, None]] = mapped_column()
    linkable: Mapped[bool] = mapped_column(default=True)
    category: Mapped[str] = mapped_column(default=Category.TEAM.value)

    @hybrid_property
    def camp_location(self) -> tuple[float, float] | None:
        return deserialize_coordinates(self._camp_location)

    @camp_location.setter
    def camp_location(self, value: tuple[float, float] | None) -> None:
        self._camp_location = serialize_coordinates(value)  # type: ignore

    @hybrid_property
    def country_location(self) -> tuple[float, float] | None:
        return deserialize_coordinates(self._country_location)

    @country_location.setter
    def country_location(self, value: tuple[float, float] | None) -> None:
        self._country_location = serialize_coordinates(value)  # type: ignore


class ScoreboardEntry(db.Model):
    __tablename__ = 'scoreboard_entries'
    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey('teams.id'))
    team: Mapped[Team] = relationship(foreign_keys=[team_id])
    score: Mapped[int] = mapped_column(default=0)
    trend: Mapped[Trend] = mapped_column(default=Trend.FLAT)


class Scoreboard(db.Model):
    __tablename__ = 'scoreboard'

    id: Mapped[int] = mapped_column(primary_key=True)
    round: Mapped[int] = mapped_column()
    entry_id: Mapped[int] = mapped_column(ForeignKey('scoreboard_entries.id'))
    entries: Mapped[list['ScoreboardEntry']] = relationship(foreign_keys=[entry_id], uselist=True)
