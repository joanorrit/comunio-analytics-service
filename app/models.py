from .database import Base
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Players(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)
    slug = Column(String, primary_key=True, default=None, unique=True, index=True)
    biwenger_id = Column(Integer, unique=True)
    name = Column(String, default=None)
    team_id = Column(Integer, default=None)
    position = Column(Integer, default=None)
    players_info_table = relationship('PlayersInfo', back_populates='players_table', cascade="all, delete")


class PlayersInfo(Base):
    __tablename__ = 'players_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer)
    average_three_last_matches = Column(Integer, default=None)
    average_five_last_matches = Column(Integer, default=None)
    one_week_delta_price = Column(Integer, default=None)
    two_weeks_delta_price = Column(Integer, default=None)
    total_points = Column(Integer, default=None)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    players_table = relationship('Players', back_populates='players_info_table')
    __table_args__ = (
        ForeignKeyConstraint(
            ['player_id'],
            ['players.id'],
        ),
    )



