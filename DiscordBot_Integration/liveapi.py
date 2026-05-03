import requests
import certifi
import time

BASE_URL = "https://api.sportdb.dev/api/flashscore/"

API_KEY = "aSl74Gb29gYQWbttVav1P7sduIrJgwrtsP7oXmqS"



headers = { 
    "X-API-KEY": API_KEY
}

class LiveScores:
    def __init__(self, sport, team_name):
        self.sport = sport
        self.team_name = team_name

    def get_livegame(self):
        sport = self.sport

        New_Url = BASE_URL + sport + "/live"

        try:
            time.sleep(20)
            response = requests.get(
            New_Url,
            headers=headers,
            verify=certifi.where(),
            timeout=10
            )

            return response.json()
        
        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
            return None
        
    def get_team(self):
        team_name = self.team_name.lower()
        response = self.get_livegame()

        if not response:
            return None

        for column in response:
            home = column.get("homeName", "").lower()
            away = column.get("awayName", "").lower()

            if team_name in home or team_name in away:
                away_score = column.get("awayScore", "")
                home_score = column.get("homeScore", "")
                info = f"{home} : {home_score}  {away} : {away_score}"
                return info

        return None

