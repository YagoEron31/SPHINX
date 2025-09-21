import sqlite3


class dbManager():
    def __init__(self, caminho_banco):
        self.banco = caminho_banco


    def conexao(self):
        conexao = sqlite3.connect(self.banco)
        conexao.autocommit = True
        cursor = conexao.cursor
        return conexao, cursor


    def adicionarUsuario(self, nome, email, senha, cargo):
        conexao, cursor = self.conexao
        query = "SELECT * FROM usuarios WHERE email=?;"
        cursor.execute(query, (email))
        if not cursor.fetchall():
            conexao.close()
            resposta =  "Email já cadastrado"

        query = "INSERT INTO usuarios (nome, email, senha, cargo) VALUES (?, ?, ?, ?);"

        cursor.execute(query, (nome, email, senha, cargo))
        resposta = "Usuário cadastrado"
        conexao.close()
        return resposta


    def adicionarProduto(self, nome, descrição, categoria, preco, estoque):
        conexao, cursor = self.conexao
        query = "INSERT INTO produtos (nome, descricao, categoria, preco, estoque) VALUES (?, ?, ?, ?, ?);"
        
        cursor.execute(query, (nome, descrição, categoria, preco, estoque))
        conexao.close()
        return

    
    def adicionarProdutoACarrinho(self, id_carrinho, id_produto, quantidade):
        conexao, cursor = self.conexao
        query = "INSERT INTO itens_carrinho (id_produto, id_carrinho, quantidade) VALUES (?, ?, ?)"
        if self.quantidadeEmEstoque(id_produto) >= quantidade:
            cursor.execute(query, (id_produto, id_carrinho, quantidade))
            resposta = "Produto adicionado ao carrinho"
        else: resposta = "Não há produtos suficientes em estoque"
        conexao.close()
        return resposta
    

    def quantidadeEmEstoque(self, id_produto):
        conexao, cursor = self.conexao
        query = "SELECT estoque FROM produtos WHERE id = ?;"
        cursor.execute(query, (id_produto))
        quantidade = cursor.fetchone()
        conexao.close()
        return quantidade


    def controlarEstoque(self, id_produto, quantidade): # quantidade pode ser negativo para diminuir do estoque
        conexao, cursor = self.conexao
        query = "UPDATE produtos SET estoque = estoque + ? WHERE id = ?;"
        cursor.execute(query, (quantidade, id_produto))
        quantidade = self.quantidadeEmEstoque(id_produto)

        if quantidade < 0:
            self.controlarEstoque(id_produto, abs(quantidade))
        conexao.close()

        return "Quantidade atualizada"


    def removerProduto(self, id_produto):
        conexao, cursor = self.conexao
        query = "DELETE FROM produtos WHERE id = ?;"
        cursor.execute(query, (id_produto))
        conexao.close()
        return "Produto deletado"


    def verificarUsuario(self, usuario, senha):
        conexao, cursor = self.conexao
        query = "SELECT * FROM usuarios WHERE usuario = ? and senha = ?;"
        cursor.execute(query, (usuario, senha))
        if not cursor.fetchall():
            conexao.close()
            return False

        conexao.close()
        return True

