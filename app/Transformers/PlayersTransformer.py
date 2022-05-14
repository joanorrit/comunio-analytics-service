from ..schema import Players, PlayersInfo

SCORE_SYSTEM = "5"  # sofaScore + AS


class PlayersTransformer:

    def transform_player(self, la_liga_player):
        player = Players()
        player.name = la_liga_player["name"]
        player.slug = la_liga_player["slug"]
        player.biwenger_id = la_liga_player["id"]
        player.position = la_liga_player["position"]
        player.position = la_liga_player["teamID"]
        return player

    def transform_player_info(self, player_model, player_info_dict):
        player_info = PlayersInfo()
        player_info.player_id = player_model.id
        player_info.total_points = player_info_dict["data"]["scoreStats"][SCORE_SYSTEM]["points"]
        player_info.average_three_last_matches = self.get_average_last_games(player_info_dict["data"]["reports"], 3)
        player_info.average_five_last_matches = self.get_average_last_five_games(player_info_dict["data"]["reports"])
        return player_info

    def get_average_last_games(self, matches_info, number_of_last_games):
        if len(matches_info) < number_of_last_games:
            return -1
        sum = 0
        played_matches = 0
        for i in range(1, number_of_last_games + 1):
            if "points" not in matches_info[-i]:
                continue
            score = matches_info[-i]["points"][SCORE_SYSTEM]
            if score is None:
                score = 0
            if score > 12:
                score = 12
            sum += score
            played_matches = played_matches + 1

        return sum / played_matches if played_matches > 0 else 0

    def get_average_last_five_games(self, matches_info):
        number_of_last_games = 5
        if len(matches_info) < number_of_last_games:
            return -1
        sum = 0
        matches_that_player_was_available = 0
        matches_that_player_has_been_injured_or_suspended = 0
        for i in range(1, number_of_last_games + 1):
            if "status" in matches_info[-i] and matches_info[-i]["status"] != {"status": "ok"}:
                # let's save number of matches where player hasn't been able to play, injure, sanction, etc...
                matches_that_player_has_been_injured_or_suspended = matches_that_player_has_been_injured_or_suspended + 1
                continue

            if "points" not in matches_info[-i] and matches_info[-i]["status"] == {"status": "ok"}:
                # if player is not injured count as if he had played (which is the same than counting 0)
                matches_that_player_was_available = matches_that_player_was_available + 1
                continue

            if "points" not in matches_info[-i]:
                continue

            score = matches_info[-i]["points"][SCORE_SYSTEM]
            if score is None:
                score = 0
            if score > 12:
                score = 12
            sum += score
            matches_that_player_was_available = matches_that_player_was_available + 1

        if matches_that_player_has_been_injured_or_suspended <= 2 and ("status" not in matches_info[-1] or matches_info[-1]["status"] != {"status": "ok"}):
            return sum / matches_that_player_was_available if matches_that_player_was_available > 0 else 0
        else:
            return sum / (matches_that_player_was_available + matches_that_player_has_been_injured_or_suspended)