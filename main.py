from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
import requests
from crAPImanager import ApiManager
from DBmanager import dbManager
import os


app = Flask(__name__)
app.secret_key = "07c71db4b8d92f93fa33d2a269657d1ebf638f808b4ee2cb640a2e0a88c13319"

api_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjllMGY1MmZiLTQzZDUtNGMzZS1hNWNmLTY0OTQ2NzIxMzFmOCIsImlhdCI6MTc1Nzg4MTMzOSwic3ViIjoiZGV2ZWxvcGVyL2E3MzM0Yzc5LTkzYWQtYjZlZi0wNDNlLWU3ZDc5NTEyNDFlYyIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI0NS43OS4yMTguNzkiXSwidHlwZSI6ImNsaWVudCJ9XX0.2JIVhW5aGUJuq71nqdOm0LV55qPPrvkzlS7TaNfM0OKZAK5UgiB2v_0aG60Il670IfVWxvWZA8tPSl6ORiEPSg"
api = ApiManager(api_token)

banco_de_dados = dbManager("banco.db")

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
    return render_template("equipe.html")


@app.route("/jogador/<nome>")
def jogador(nome):
    tag = players_tags[nome]
    return render_template("jogador.html", tag=tag)


@app.route("/api/jogador/<tag>/<tipo>")
def api_jogador(tag, tipo):
    tag = tag.replace("%23", "#")
    if tag not in players_tags.values(): return {"response": "tag invalida"}, 404
    if tipo == "basic":
        jogador = api.getPlayerBasic(tag)
    elif tipo == "full":
        jogador = api.getPlayer(tag)
    return jsonify(jogador), 200


@app.route("/api/batalhas/<tag>/<quantidade>")
def api_batalhas(tag, quantidade):
    tag = tag.replace("%23", "#")
    if tag not in players_tags.values(): return {"response": "tag invalida"}, 404
    batalhas = api.getBattleLog(tag, quantidade)
    return jsonify(batalhas), 200


@app.route("/api/equipe")
def api_equipe():
    players = api.getTeamBasic(players_tags)
    return jsonify(players), 200


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    elif request.method == "POST":
        response = request.json
        email = response["email"]
        senha = response["senha"]
        resposta = banco_de_dados.verificarUsuario(email, senha)
        if not resposta:
            flash("Falha no login, email ou senha incorreto!", "danger")
            return jsonify({"success": False, "message": "email ou senha incorreto."}), 401
        
        id, usuario = banco_de_dados.obterUsuarioPorEmail(email)

        session.clear()
        session["id"] = id
        session["usuario"] = usuario

        flash("Login realizado com successo!", "success")
        return jsonify({"success": True, "message": "login feito com sucesso.", "url": url_for("index")}), 200


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "GET":
        return render_template("registro.html")

    elif request.method == "POST":
        response = request.json
        usuario = response["usuario"]
        email = response["email"]
        senha = response["senha"]
        resposta = banco_de_dados.obterUsuarioPorEmail(email)
        if resposta: 
            flash("Falha no cadastro, email já em uso!", "danger")
            return jsonify({"success": False, "message": "Email já cadastrado."}), 409
        
        resposta = banco_de_dados.adicionarUsuario(usuario, email, senha, 0)

        id, usuario = banco_de_dados.obterUsuarioPorEmail(email)
        session.clear()
        session["id"] = id
        session["usuario"] = usuario

        flash("Conta criada com sucesso!", "success")
        return jsonify({"success": True, "message": "Conta criada.", "url": url_for("index")}), 200


@app.route("/logout")
def logout():
    session.clear()
    flash("Você foi desconectado de sua conta!", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    host = os.getenv("HOST", "localhost")
    port = os.getenv("PORT", 5000)
    debug = os.getenv("DEBUG", True)

    app.run(host=host, port=port, debug=debug)


