import requests
from datetime import datetime

class ApiManager():
    BASEURL = "https://api.clashroyale.com/v1"
    BASEURLPROXY = "https://proxy.royaleapi.dev/v1"
    def __init__(self, TOKEN):
        self.headers = {"Authorization": f"Bearer {TOKEN}"}
    
    
    def getTeamBasic(self, team: dict):
        players = {}
        for tag in team.values():
            player = self.getPlayerBasic(tag)
            players[player["name"]] = player
        return players
    

    def getPlayer(self, playerTag):
        url = ApiManager.BASEURLPROXY + "/players/" + playerTag.replace("#", "%23")
        response = requests.get(url, headers=self.headers).json()
        current_season_date = datetime.now().strftime("%Y%m")

        response["trophies"] = response["trophies"] if (int(response["trophies"]) < 10000) else response["progress"][f"seasonal-trophy-road-{current_season_date}"]["trophies"]
        response["bestTrophies"] = response["bestTrophies"] if (int(response["bestTrophies"]) < 10000) else response["progress"][f"seasonal-trophy-road-{current_season_date}"]["bestTrophies"]
        response["arena"]["name"] = response["arena"]["name"] if (int(response["trophies"]) < 10000) else "Arenas Sazonais"
        return response
    

    def getPlayerBasic(self, playerTag):
        response = self.getPlayer(playerTag)
        player = {
            "name": response["name"],
            "arena": response["arena"],
            "wins": response["wins"],
            "trophies": response["trophies"],
            "bestTrophies": response["bestTrophies"],
            "expLevel": response["expLevel"],
        }
        
        return player
    
 
    def getBattleLog(self, playerTag, count=5):
        url = ApiManager.BASEURLPROXY + "/players/" + playerTag.replace("#", "%23") + "/battlelog"
        response = requests.get(url, headers=self.headers).json()
        return response[:int(count)]
