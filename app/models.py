from __future__ import annotations

from typing import Union

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import ForeignKey, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

db = SQLAlchemy()
migrate = Migrate(db=db)


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
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column()
    team_id: Mapped[Union[int, None]] = mapped_column(ForeignKey('teams.id'))
    team: Mapped[Union['Team', None]] = relationship(foreign_keys=[team_id], back_populates='members')
    roles: Mapped[list[Role]] = relationship('Role', secondary=user_role_table, backref='users')


class Team(db.Model):
    __tablename__ = 'teams'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    members: Mapped[list[User]] = relationship('User', back_populates='team')


class Scoreboard(db.Model):
    __tablename__ = 'scoreboard'

    id: Mapped[int] = mapped_column(primary_key=True)
