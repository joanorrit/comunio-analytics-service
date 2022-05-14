import time

import requests
from fastapi import APIRouter, Depends, HTTPException
from ..database import db
from ..Transformers.PlayersTransformer import PlayersTransformer
from .. import crud
import json

ELEMENTS_PER_PAGE = 100
GET_ALL_PLAYERS_ENDPOINT = (
    "https://cf.biwenger.com/api/v2/competitions/la-liga/data?lang=en&score=5"
)
GET_SINGLE_PLAYER_INFO = "https://cf.biwenger.com/api/v2/players/la-liga/"
SCORE_SYSTEM = "5"  # sofaScore + AS

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)


@router.post("/import-biwenger-players")
async def populate_database(db=Depends(db), page: int = 0):
    la_liga_players_info = await get_all_players_in_la_liga()
    la_liga_players = la_liga_players_info["data"]["players"]

    num_of_calls_made = 0
    processed_players = 0
    iterations = 0
    for la_liga_player in la_liga_players.items():
        iterations = iterations + 1

        if iterations < page * ELEMENTS_PER_PAGE:
            continue
        if processed_players > ELEMENTS_PER_PAGE:
            break

        la_liga_player = la_liga_player[1]

        player_info_dict = await get_single_player_info(la_liga_player["slug"])
        num_of_calls_made = await exceeded_calls_sleep(num_of_calls_made)

        # CHECK! I should be able to remove this!
        if "data" not in player_info_dict:
            continue

        players_transformer = PlayersTransformer()

        player = players_transformer.transform_player(la_liga_player)
        player_model = crud.save_players_model(db, player)

        player_info = players_transformer.transform_player_info(
            player_model, player_info_dict
        )
        crud.save_player_info_model(db, player_info)

        processed_players = processed_players + 1

    return {
        "msg": "ok",
        "processed_players": processed_players
    }


async def exceeded_calls_sleep(num_of_calls_made):
    """
    Sleeps by some seconds when our guess of biwenger's
    api rate limit has been exceeded.
    :param num_of_calls_made:
    :return:
    """
    num_of_calls_made = num_of_calls_made + 1
    if (num_of_calls_made % 1) == 0:
        # sleep 1 sec every 1 calls
        time.sleep(1)
    return num_of_calls_made


async def get_single_player_info(player_slug):
    query_params = "?lang=en&fields=*%2Cteam%2Cfitness%2Creports(points%2Chome%2Cevents%2Cstatus(status%2CstatusInfo)%2Cmatch(*%2Cround%2Chome%2Caway)%2Cstar)%2Cprices%2Ccompetition%2Cseasons%2Cnews%2Cthreads"
    url = GET_SINGLE_PLAYER_INFO + player_slug + query_params
    raw_player_info = {}
    try:
        raw_player_info = requests.get(url)
        if raw_player_info.status_code == 429:
            print('failed in get single player')
            raw_player_info = await retry_get_single_player_call(raw_player_info, url)
    except (requests.exceptions.ConnectionError, requests.exceptions.SSLError):
        print('connection error')
        raw_player_info = await retry_get_single_player_call(raw_player_info, url)

    try:
        player_info_dict = raw_player_info.json()
    except json.decoder.JSONDecodeError:
        # CHECK! It sometimes fails for some reason. Catching the error here and
        # printing the response what will show the http status.
        print(raw_player_info)
        return []

    return player_info_dict


async def retry_get_single_player_call(raw_player_info, url):
    status_code = 429
    retries_count = 0
    while status_code != 200 and retries_count < 6:
        print('retrying....')
        # sleep 3 min an try again. Not try more than 6 * 3 min.
        time.sleep(180)
        raw_player_info = requests.get(url)
        status_code = raw_player_info.status_code
        retries_count = retries_count + 1
    if status_code != 200:
        raise HTTPException(429, detail='Why this guys do not let me make a few stupid calls')
    return raw_player_info


async def get_all_players_in_la_liga():
    response = requests.get(GET_ALL_PLAYERS_ENDPOINT)
    return response.json()


def get_average_last_games(matches_info, number_of_last_games):
    if len(matches_info) < number_of_last_games:
        return -1
    sum = 0
    for i in range(1, number_of_last_games + 1):

        if "points" not in matches_info[-i]:
            continue
        sum += matches_info[-i]["points"][SCORE_SYSTEM]
    return sum / number_of_last_games
