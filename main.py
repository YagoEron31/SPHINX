from flask import Flask, render_template, jsonify, request
import requests
from crAPImanager import ApiManager
from DBmanager import dbManager
import os

app = Flask(__name__)

api_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjllMGY1MmZiLTQzZDUtNGMzZS1hNWNmLTY0OTQ2NzIxMzFmOCIsImlhdCI6MTc1Nzg4MTMzOSwic3ViIjoiZGV2ZWxvcGVyL2E3MzM0Yzc5LTkzYWQtYjZlZi0wNDNlLWU3ZDc5NTEyNDFlYyIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI0NS43OS4yMTguNzkiXSwidHlwZSI6ImNsaWVudCJ9XX0.2JIVhW5aGUJuq71nqdOm0LV55qPPrvkzlS7TaNfM0OKZAK5UgiB2v_0aG60Il670IfVWxvWZA8tPSl6ORiEPSg"
api_manager = ApiManager(api_token)

db_manager = dbManager("banco.db")

players_tags = {
    "Maurilio": "#2YUCRQPYC",
    "yago": "#LGCL8RVJU",
    "Moros": "#RLJ9JP808",
    "LuffyX": "#U2CJLVJUY",
    "gabzz": "#PRCR808YJ"
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/contato")
def contato():
    return render_template("contato.html")

@app.route("/jogo")
def jogo():
    return render_template("jogo.html")

@app.route("/loja")
def loja():
    return render_template("loja.html")

@app.route("/equipe")
def equipe():
    return render_template("team.html")


@app.route("/jogador/<name>")
def jogador(name):
    tag = players_tags[name]
    return render_template("player.html", tag=tag)


@app.route("/player/<tag>/<type>")
def player(tag, type):
    tag = tag.replace("%23", "#")
    if tag not in players_tags.values(): return {"response": "tag invalida"}, 404
    if type == "basic":
        player = api_manager.getPlayerBasic(tag)
    elif type == "full":
        player = api_manager.getPlayer(tag)
    return jsonify(player), 200


@app.route("/battlelog/<tag>/<count>")
def battlelog(tag, count):
    tag = tag.replace("%23", "#")
    if tag not in players_tags.values(): return {"response": "tag invalida"}, 404
    battlelog = api_manager.getBattleLog(tag, count)
    return jsonify(battlelog), 200


@app.route("/team")
def team():
    players = api_manager.getTeamBasic(players_tags)
    return jsonify(players), 200


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        response = request.json
        usuario = response["usuario"]
        senha = response["senha"]
        resposta = db_manager.verificarUsuario(usuario, senha)
        print(resposta)
        return {"response": resposta}, 200

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("registro.html")
    elif request.method == "POST":
        response = request.json
        usuario = response["usuario"]
        email = response["email"]
        senha = response["senha"]
        resposta = db_manager.adicionarUsuario(usuario, email, senha, 0)
        return {"response": resposta}, 200


@app.route("/logout")
def logout():
    pass


if __name__ == "__main__":
    host = os.getenv("HOST", "localhost")
    port = os.getenv("PORT", 5678)
    debug = os.getenv("DEBUG", True)

    app.run(host=host, port=port, debug=debug)

