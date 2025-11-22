from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
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
    "gabzzpy": "#20P2CRJ808"
}


@app.route("/")
def index():
    produtos = banco_de_dados.obterProdutos()
    noticias = banco_de_dados.obterNoticias()
    if session.get("id"): # Verifica se tem ID na sessão
        id_usuario = session.get("id")
        
        # Corrigido: usa banco_de_dados em vez de db
        itens = banco_de_dados.verCarrinho(id_usuario)
        return render_template("index.html", quantidade_carrinho=len(itens), produtos=produtos, noticias=noticias)
    return render_template("index.html", quantidade_carrinho=0, produtos=produtos, noticias=noticias)


@app.route("/contato")
def contato():
    return render_template("contato.html")


@app.route("/jogo")
def jogo():
    return render_template("jogo.html")

@app.route("/noticias")
def noticias():
    return render_template("noticias.html", noticias=banco_de_dados.obterNoticias())

@app.route("/noticia/<int:id_noticia>")
def ver_noticia(id_noticia):
    noticia = banco_de_dados.obterNoticiaPorId(id_noticia)
    return render_template("noticia.html", noticia=noticia)

@app.route("/loja")
def loja():
    produtos = banco_de_dados.obterProdutos()
    if session.get("id"): # Verifica se tem ID na sessão
        id_usuario = session.get("id")
        
        # Corrigido: usa banco_de_dados em vez de db
        itens = banco_de_dados.verCarrinho(id_usuario)
        
        return render_template("loja.html", quantidade_carrinho=len(itens), produtos=produtos)
    
    return render_template("loja.html", produtos=produtos, quantidade_carrinho=0)


@app.route("/carrinho/adicionar", methods=["POST"])
def adicionar_carrinho():
    if not session.get("usuario"):
        return jsonify({"success": False, "message": "Faça login para adicionar ao carrinho"}), 401
    
    data = request.json
    id_produto = data.get("id_produto")
    id_carrinho = session.get("id")
    
    # CORREÇÃO: Use banco_de_dados aqui, não db
    resposta = banco_de_dados.adicionarProdutoACarrinho(id_carrinho, id_produto, 1)
    
    if resposta == "Produto adicionado ao carrinho":
        return jsonify({"success": True, "message": resposta}), 200
    else:
        return jsonify({"success": False, "message": resposta}), 400


@app.route("/live")
def live():
    canal = os.getenv("CANAL", "gaules")
    if session.get("id"): # Verifica se tem ID na sessão
        id_usuario = session.get("id")
        
        # Corrigido: usa banco_de_dados em vez de db
        itens = banco_de_dados.verCarrinho(id_usuario)
        
        return render_template("live.html", canal=canal, quantidade_carrinho=len(itens))
    return render_template("live.html", canal=canal, quantidade_carrinho=0)

@app.route("/jogador/<nome>")
def jogador(nome):
    tag = players_tags[nome]
    if session.get("id"): # Verifica se tem ID na sessão
        id_usuario = session.get("id")
        
        # Corrigido: usa banco_de_dados em vez de db
        itens = banco_de_dados.verCarrinho(id_usuario)
        
        return render_template("jogador.html", tag=tag, quantidade_carrinho=len(itens))
    return render_template("jogador.html", tag=tag, quantidade_carrinho=0)


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
        
        id, usuario, cargo = banco_de_dados.obterUsuarioPorEmail(email)

        session.clear()
        session["id"] = id
        session["usuario"] = usuario
        session["cargo"] = cargo

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

        id, usuario, cargo = banco_de_dados.obterUsuarioPorEmail(email)
        session.clear()
        session["id"] = id
        session["usuario"] = usuario
        session["cargo"] = cargo

        flash("Conta criada com sucesso!", "success")
        return jsonify({"success": True, "message": "Conta criada.", "url": url_for("index")}), 200


@app.route("/logout")
def logout():
    session.clear()
    flash("Você foi desconectado de sua conta!", "success")
    return redirect(url_for("index"))

@app.route('/carrinho')
def carrinho():
    if not session.get("id"): # Verifica se tem ID na sessão
        return redirect(url_for('login'))
    
    id_usuario = session.get("id")
    
    # Corrigido: usa banco_de_dados em vez de db
    itens = banco_de_dados.verCarrinho(id_usuario)
    print(itens)
    # Calcula o total geral
    total_geral = sum(item['total_item'] for item in itens)
    
    return render_template('carrinho.html', carrinho=itens, quantidade_carrinho=len(itens), total_geral=total_geral)

@app.route('/carrinho/remover/<int:id_item>', methods=['POST'])
def remover_item(id_item):
    if not session.get("id"):
        return jsonify({"success": False, "message": "Login necessário"}), 401
        
    # Corrigido: usa banco_de_dados em vez de db
    banco_de_dados.removerDoCarrinho(id_item)
    return jsonify({"success": True})


@app.route('/carrinho/atualizar', methods=['POST'])
def atualizar_quantidade():
    if not session.get("id"):
        return jsonify({"success": False, "message": "Login necessário"}), 401
        
    data = request.json
    id_item = data.get("id_item")
    quantidade = data.get("quantidade")
    
    if not id_item or quantidade is None:
        return jsonify({"success": False, "message": "Dados inválidos"}), 400
        
    sucesso, mensagem = banco_de_dados.atualizarQuantidadeItemCarrinho(id_item, int(quantidade))
    
    if sucesso:
        return jsonify({"success": True, "message": mensagem})
    else:
        return jsonify({"success": False, "message": mensagem}), 400


@app.route('/carrinho/finalizar', methods=['POST'])
def finalizar_compra():
    if not session.get("id"):
        return jsonify({"success": False, "message": "Login necessário"}), 401
        
    id_usuario = session.get("id")
    
    # Corrigido: usa banco_de_dados em vez de db
    sucesso, mensagem = banco_de_dados.finalizarCompra(id_usuario)
    
    return jsonify({"success": sucesso, "message": mensagem})


# --- Admin Routes ---

@app.route("/admin")
def admin():
    if not session.get("usuario") or session.get("cargo") != 1:
        flash("Acesso negado.", "danger")
        return redirect(url_for("index"))
    
    produtos = banco_de_dados.obterProdutos()
    noticias = banco_de_dados.obterNoticias()
    return render_template("admin.html", produtos=produtos, noticias=noticias)


@app.route("/admin/produto/adicionar", methods=["POST"])
def admin_adicionar_produto():
    if not session.get("usuario") or session.get("cargo") != 1:
        return jsonify({"success": False, "message": "Acesso negado"}), 403

    data = request.form
    nome = data.get("nome")
    descricao = data.get("descricao")
    categoria = data.get("categoria")
    preco = data.get("preco")
    estoque = data.get("estoque")
    imagem = data.get("imagem")

    banco_de_dados.adicionarProdutoAoBanco(nome, descricao, categoria, preco, estoque, imagem)
    flash("Produto adicionado com sucesso!", "success")
    return redirect(url_for("admin"))


@app.route("/admin/produto/editar/<int:id>", methods=["POST"])
def admin_editar_produto(id):
    if not session.get("usuario") or session.get("cargo") != 1:
        return jsonify({"success": False, "message": "Acesso negado"}), 403
    
    data = request.form
    nome = data.get("nome")
    descricao = data.get("descricao")
    categoria = data.get("categoria")
    preco = data.get("preco")
    estoque = data.get("estoque")
    imagem = data.get("imagem")

    banco_de_dados.atualizarProduto(id, nome, descricao, categoria, preco, estoque, imagem)
    flash("Produto atualizado com sucesso!", "success")
    return redirect(url_for("admin"))


@app.route("/admin/produto/deletar/<int:id>")
def admin_deletar_produto(id):
    if not session.get("usuario") or session.get("cargo") != 1:
        flash("Acesso negado.", "danger")
        return redirect(url_for("index"))
    
    banco_de_dados.removerProduto(id)
    flash("Produto removido com sucesso!", "success")
    return redirect(url_for("admin"))


@app.route("/admin/noticia/adicionar", methods=["POST"])
def admin_adicionar_noticia():
    if not session.get("usuario") or session.get("cargo") != 1:
        return jsonify({"success": False, "message": "Acesso negado"}), 403

    data = request.form
    titulo = data.get("titulo")
    conteudo = data.get("conteudo")
    imagem = data.get("imagem")

    banco_de_dados.adicionarNoticia(titulo, conteudo, imagem)
    flash("Notícia adicionada com sucesso!", "success")
    return redirect(url_for("admin"))


@app.route("/admin/noticia/editar/<int:id>", methods=["POST"])
def admin_editar_noticia(id):
    if not session.get("usuario") or session.get("cargo") != 1:
        return jsonify({"success": False, "message": "Acesso negado"}), 403
    
    data = request.form
    titulo = data.get("titulo")
    conteudo = data.get("conteudo")
    imagem = data.get("imagem")

    banco_de_dados.atualizarNoticia(id, titulo, conteudo, imagem)
    flash("Notícia atualizada com sucesso!", "success")
    return redirect(url_for("admin"))


@app.route("/admin/noticia/deletar/<int:id>")
def admin_deletar_noticia(id):
    if not session.get("usuario") or session.get("cargo") != 1:
        flash("Acesso negado.", "danger")
        return redirect(url_for("index"))
    
    banco_de_dados.removerNoticia(id)
    flash("Notícia removida com sucesso!", "success")
    return redirect(url_for("admin"))


if __name__ == "__main__":
    banco_de_dados.criarTabelas()
    host = os.getenv("HOST", "localhost")
    port = os.getenv("PORT", 5000)
    debug = os.getenv("DEBUG", True)

    app.run(host=host, port=port, debug=debug)
