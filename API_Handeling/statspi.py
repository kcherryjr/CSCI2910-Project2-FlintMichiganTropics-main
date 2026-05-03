import requests
import certifi

API_KEY = "f629d3d9db86bf5e79ffaf4850486002"

headers = {
    "x-apisports-key": API_KEY
}


class TeamStats:
    def __init__(self, sport, team_name, season):
        self.sport = sport
        self.team_name = team_name
        self.season = season

        if self.sport == "football":  # NFL
            self.base_url = "https://v1.american-football.api-sports.io"

        elif self.sport == "baseball":
            self.base_url = "https://v1.baseball.api-sports.io"

        elif self.sport == "hockey":
            self.base_url = "https://v1.hockey.api-sports.io"

        elif self.sport == "soccer":
            self.base_url = "https://v3.football.api-sports.io"

        elif self.sport == "basketball":
            self.base_url = "https://v2.nba.api-sports.io"

        else:
            raise ValueError("Unsupported sport")

    
    def get_team_id(self):
        url = self.base_url + "/teams"

        params = {"search": self.team_name}

        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                verify=certifi.where(),
                timeout=10
            )

            data = response.json()
            teams = data.get("response", [])

            if not teams:
                return None

            for t in teams:
                team_obj = t.get("team") or t
                name = team_obj.get("name", "").lower()

                if self.team_name.lower() in name:
                    return team_obj.get("id")

            return None

        except Exception as e:
            print("Team request failed:", e)
            return None

    
    def build_stats_params(self, team_id):

        league_map = {
            "baseball": 1,
            "hockey": 57,
            "soccer": 253,
            "football": 1
        }

        params = {
            "team": team_id,
            "season": self.season
        }

        if self.sport == "basketball":
            params = {
                "id": team_id,
                "season": self.season
            }
            return params

        league_id = league_map.get(self.sport)
        if league_id:
            params["league"] = league_id

        return params

    
    def get_stats(self):
        team_id = self.get_team_id()

        if not team_id:
            print("Team not found")
            return None

        url = self.base_url + "/teams/statistics"
        params = self.build_stats_params(team_id)

        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                verify=certifi.where(),
                timeout=10
            )

            return response.json()

        except requests.exceptions.RequestException as e:
            print("Stats request failed:", e)
            return None

    
    def process_games(self, games, team_id):
        stats = {
            "preseason": {"wins": 0, "losses": 0},
            "regular": {"wins": 0, "losses": 0},
            "playoffs": {"wins": 0, "losses": 0}
        }

        for g in games:
            teams = g.get("teams", {})
            scores = g.get("scores", {})

        
            home_team = teams.get("home", {})
            away_team = teams.get("away") or teams.get("visitors", {})

            home_id = home_team.get("id")
            away_id = away_team.get("id")

            if not home_id or not away_id:
                continue

        
            if self.sport == "basketball":
                home_score = scores.get("home", {}).get("points")
                away_score = scores.get("visitors", {}).get("points")

                league_type = g.get("league")
                stage_val = g.get("stage")

                if league_type != "standard":
                    continue
            
                if stage_val == 2:
                    key = "regular"
                elif stage_val == 3:
                    key = "playoffs"
                else:
                    key = "preseason"

            else:
                game = g.get("game", {})
                stage = game.get("stage", "").lower()

                home_score = scores.get("home", {}).get("total")
                away_score = scores.get("away", {}).get("total")

            
                if "pre" in stage:
                    key = "preseason"
                elif "playoff" in stage or "post" in stage:
                    key = "playoffs"
                else:
                    key = "regular"

            if home_score is None or away_score is None:
                continue

            is_home = home_id == team_id

            won = (
                (is_home and home_score > away_score) or
                (not is_home and away_score > home_score)
            )

            if won:
                stats[key]["wins"] += 1
            else:
                stats[key]["losses"] += 1

        return stats

    
    def get_game_based_stats(self):
        team_id = self.get_team_id()

        if not team_id:
            return None

        url = self.base_url + "/games"

        params = {
            "team": team_id,
            "season": self.season
        }

        if self.sport == "football":
            params["league"] = 1

        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                verify=certifi.where(),
                timeout=10
            )

            data = response.json()
            games = data.get("response", [])

            if not games:
                return None

            return self.process_games(games, team_id)

        except Exception as e:
            print("Game request failed:", e)
            return None

    
    def get_team_stats(self):

      
        if self.sport in ["football", "basketball"]:
            stats = self.get_game_based_stats()

            if not stats:
                return "No data found"

            return f"""
Preseason: {stats['preseason']['wins']}-{stats['preseason']['losses']}
Regular Season: {stats['regular']['wins']}-{stats['regular']['losses']}
Playoffs: {stats['playoffs']['wins']}-{stats['playoffs']['losses']}
"""

        
        response = self.get_stats()

        if not response:
            return "No response from API"

        data = response.get("response")

        if not data:
            return "No data found"

        if isinstance(data, list):
            if len(data) == 0:
                return "No data found"
            data = data[0]

        if self.sport == "baseball":
            games = data.get("games", {})
            return f"MLB Games: {games.get('played')} | Wins: {games.get('wins')}"

        elif self.sport == "hockey":
            games = data.get("games", {})
            return f"NHL Games: {games.get('played')} | Wins: {games.get('wins')}"

        elif self.sport == "soccer":
            goals = data.get("goals", {})
            return f"Goals For: {goals.get('for', {}).get('total')} | Against: {goals.get('against', {}).get('total')}"



team = TeamStats("basketball", "Los Angeles Lakers", 2024)
print(team.get_team_stats())