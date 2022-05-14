from pydantic import BaseModel
from typing import Optional
from datetime import date


class Players(BaseModel):
    id: Optional[int]
    biwenger_id: Optional[int]
    name: Optional[str]
    slug: Optional[str]
    team_id: Optional[int]
    position: Optional[int]

    class Config:
        orm_mode = True


class PlayersInfo(BaseModel):
    id: Optional[int]
    player_id: Optional[int]
    average_three_last_matches: Optional[int]
    average_five_last_matches: Optional[int]
    one_week_delta_price: Optional[int]
    two_weeks_delta_price: Optional[int]
    total_points: Optional[int]
    date_created: Optional[date]

    class Config:
        orm_config = True