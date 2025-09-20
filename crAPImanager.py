import requests


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

    def getPlayerBasic(self, playerTag):
        url = ApiManager.BASEURLPROXY + "/players/" + playerTag.replace("#", "%23")
        response = requests.get(url, headers=self.headers).json()
        player = {
            "name": response["name"],
            "arena": response["arena"],
            "wins": response["wins"],
            "trophies": response["trophies"],
            "expLevel": response["expLevel"],
        }
        return player
    

    def getPlayer(self, playerTag):
        url = ApiManager.BASEURLPROXY + "/players/" + playerTag.replace("#", "%23")
        response = requests.get(url, headers=self.headers).json()
        return response
    
    
    def getBattleLog(self, playerTag, count=5):
        url = ApiManager.BASEURLPROXY + "/players/" + playerTag.replace("#", "%23") + "/battlelog"
        response = requests.get(url, headers=self.headers).json()
        return response[:int(count)]
