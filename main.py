from flask import Flask, render_template, jsonify
from crAPImanager import ApiManager


app = Flask(__name__)

api_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjllMGY1MmZiLTQzZDUtNGMzZS1hNWNmLTY0OTQ2NzIxMzFmOCIsImlhdCI6MTc1Nzg4MTMzOSwic3ViIjoiZGV2ZWxvcGVyL2E3MzM0Yzc5LTkzYWQtYjZlZi0wNDNlLWU3ZDc5NTEyNDFlYyIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI0NS43OS4yMTguNzkiXSwidHlwZSI6ImNsaWVudCJ9XX0.2JIVhW5aGUJuq71nqdOm0LV55qPPrvkzlS7TaNfM0OKZAK5UgiB2v_0aG60Il670IfVWxvWZA8tPSl6ORiEPSg"
api_manager = ApiManager(api_token)

players_tags = {
    "Maurilio": "#2YUCRQPYC",
    "yago": "#LGCL8RVJU",
    "Moros": "#RLJ9JP808",
    "LuffyX": "#U2CJLVJUY",
    "GabMont982": "#PRCR808YJ"
}

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/equipe")
def equipe():
    return render_template("team.html")


app.route("/player/<name>")
def player(name):
    tag = players_tags[name]
    return render_template("player.html", tag=tag)


@app.route("/players/<type>")
def players(type):
    players = {}
    for tag in players_tags.values():
        if type == "basic":
            player = api_manager.getPlayerBasic(tag)
        elif type == "full":
            player = api_manager.getPlayer(tag)

        players[player["name"]] = player
    return jsonify(players), 200


#app.run(host="localhost", port=5000, debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
