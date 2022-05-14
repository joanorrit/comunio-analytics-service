from sqlalchemy.orm import Session
from . import schema, models
from sqlalchemy.exc import IntegrityError
from .models import Players
from sqlalchemy.sql import text
from .database import engine
from .endpoints.public import ELEMENTS_PER_PAGE

# models.Base.metadata.tables['players']  # CHECK!! This is how you get the fucking name!!


def save_players_model(db: Session, info: schema.Players):
    players_model = models.Players(**info.dict())

    try:
        db.add(players_model)
        db.commit()  # CHECK! Should find a way of committing only one to the database
        db.refresh(players_model)
    except IntegrityError:
        db.rollback()
        # db.query(Players).filter(Players.slug == players_model.slug).update(
        #     {
        #         Players.biwenger_id: players_model.biwenger_id,
        #         Players.name: players_model.name,
        #         Players.team_id: players_model.team_id,
        #         Players.position: players_model.position,
        #     }
        # )
        # # CHECK! Remove this query. Probably the update return player I am querying here.
        players_model = db.query(Players).filter(Players.slug == players_model.slug)[0]

    return players_model


def save_player_info_model(db: Session, info: schema.PlayersInfo):
    players_info_model = models.PlayersInfo(**info.dict())
    db.add(players_info_model)
    db.commit()
    db.refresh(players_info_model)
    return players_info_model


def get_filtered_top_players(page):
    offset = page * ELEMENTS_PER_PAGE
    response = []
    with engine.connect() as con:
        sql = text(
            "SELECT ranked_players.name, ranked_players.three_avg,"
            " ranked_players.five_avg, ranked_players.date FROM ( SELECT"
            " players.name as name, players_info.average_three_last_matches AS"
            " three_avg, players_info.average_five_last_matches AS five_avg,"
            " players_info.date_created AS date, RANK() OVER (PARTITION BY"
            " players.slug ORDER BY players_info.date_created DESC) dest_rank"
            " FROM players JOIN players_info ON players.id ="
            " players_info.player_id ) AS ranked_players WHERE dest_rank = 1"
            " ORDER BY ranked_players.five_avg DESC, ranked_players.three_avg"
            " DESC limit :elm_per_page OFFSET :offset;"
        )
        result = con.execute(sql, {"elm_per_page": ELEMENTS_PER_PAGE, "offset": offset})
    for row in result:
        response.append(row)
    return response


def get_points_by_lineup(biwenger_ids):
    biwenger_ids_sql = tuple(biwenger_ids)
    response = []
    with engine.connect() as con:
        sql = text(
            "SELECT SUM(ranked_players.three_avg) FROM ( SELECT players.name as name, players_info.average_five_last_matches AS three_avg, players_info.average_five_last_matches AS five_avg, players_info.date_created AS date, players.biwenger_id as biwenger_id, RANK() OVER (PARTITION BY players.slug ORDER BY players_info.date_created DESC) dest_rank FROM players JOIN players_info ON players.id = players_info.player_id) AS ranked_players WHERE dest_rank = 1 AND ranked_players.biwenger_id IN :biwenger_ids_sql;"
        )
        result = con.execute(sql, {"biwenger_ids_sql": biwenger_ids_sql})
    for row in result:
        response.append(row)
    return response[0][0]
