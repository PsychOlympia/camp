from __future__ import annotations

from enum import Enum, unique
from typing import Union, Protocol
# from uuid import uuid4

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import ForeignKey, Column, Integer, desc
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

    @property
    def type(self):
        return self.__class__.__name__.lower()


class PointOfInterest(db.Model):
    __tablename__ = 'pois'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    _camp_location: Mapped[Union[str, None]] = mapped_column()
    _country_location: Mapped[Union[str, None]] = mapped_column()
    logo: Mapped[Union[str, None]] = mapped_column(default='default.png')
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

    @property
    def type(self):
        return self.__class__.__name__.lower()


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

    @property
    def type(self):
        return self.__class__.__name__.lower()


class ScoreboardEntry(db.Model):
    __tablename__ = 'scoreboard_entries'

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey('teams.id'))
    team: Mapped[Team] = relationship(foreign_keys=[team_id])
    score: Mapped[int] = mapped_column(default=0)
    round: Mapped[int] = mapped_column(ForeignKey('scoreboard.round'))

    @property
    def trend(self) -> Trend:
        previous_entry = db.session.query(ScoreboardEntry).where(
            ScoreboardEntry.team == self.team and ScoreboardEntry.round == self.round - 1
        ).first()
        if previous_entry is None:
            return Trend.FLAT

        current_position = self.position
        previous_position = previous_entry.position

        if current_position == previous_position:
            return Trend.FLAT
        elif current_position > previous_position:
            return Trend.UP
        else:
            return Trend.DOWN

    @property
    def position(self) -> int:
        return db.session.query(ScoreboardEntry).order_by(desc(ScoreboardEntry.score)).all().index(self)


class Scoreboard(db.Model):
    __tablename__ = 'scoreboard'

    round: Mapped[int] = mapped_column(primary_key=True)
    entries: Mapped[list['ScoreboardEntry']] = relationship('ScoreboardEntry', uselist=True, backref='scoreboard')  # TODO


class WebsiteFeedback(db.Model):
    __tablename__ = 'website_feedback'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    user: Mapped[User] = relationship('User', foreign_keys=[user_id])
    keep: Mapped[str] = mapped_column()
    remove: Mapped[str] = mapped_column()
    add: Mapped[str] = mapped_column()
    further_notes: Mapped[str] = mapped_column()


class WiFiFeedback(db.Model):
    __tablename__ = 'wifi_feedback'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    user: Mapped[User] = relationship('User', foreign_keys=[user_id])
    quality: Mapped[int] = mapped_column()
    _coverage: Mapped[str] = mapped_column()
    further_notes: Mapped[str] = mapped_column()

    @hybrid_property
    def coverage(self) -> list[int]:
        return list(map(int, self._coverage.split(',')))

    @coverage.setter
    def coverage(self, value: list[int]) -> None:
        self._coverage = ','.join(map(str, value))
