from fastapi import APIRouter, Depends, HTTPException
from .. import crud
from dotenv import load_dotenv
import requests
import os
from os.path import join, dirname
from pathlib import Path
import pathlib
import sys

ELEMENTS_PER_PAGE = 15
GET_LINEUP_ENDPOINT = 'https://biwenger.as.com/api/v2/rounds/league/'

router = APIRouter(
    prefix="/public",
    tags=["public"],
    responses={404: {"description": "Not found"}},
)

# CHECK! Import settings. We can probably do this in a nicely way.
load_dotenv()


@router.get("/get-top-players")
async def get_top_players(page: int = 0):
    return crud.get_filtered_top_players(page)


async def get_users_lineup(round_id):
    headers = {
        "x-league": os.environ.get("X_LEAGUE"),
        "authorization": os.environ.get("AUTH_TOKEN"),
        "x-user": os.environ.get("X_USER")
    }
    response = requests.get(GET_LINEUP_ENDPOINT + round_id, headers=headers)
    return response.json()


@router.get("/get-round-prediction/{round_id}")
async def get_round_prediction(round_id):
    round_info = await get_users_lineup(round_id)

    users_info = round_info["data"]["league"]["standings"]
    users_prediction = {}
    for user_info in users_info:
        if "lineup" not in user_info:
            return {"msg": "This round hasn't begun yet!"}

        points = crud.get_points_by_lineup(user_info["lineup"]["players"])
        users_prediction[user_info["name"]] = points

    test = {k: v for k, v in sorted(users_prediction.items(), key=lambda item: item[1], reverse=True)}
    return test

