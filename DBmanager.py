import sqlite3


class dbManager():
    def __init__(self, caminho_banco):
        self.banco = caminho_banco


    def conexao(self):
        conexao = sqlite3.connect(self.banco)
        cursor = conexao.cursor()
        return conexao, cursor


    def criarTabelas(self):
        conexao, cursor = self.conexao()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                cargo INTEGER DEFAULT 0
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                categoria TEXT,
                preco REAL,
                estoque INTEGER,
                imagem TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS noticias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                conteudo TEXT NOT NULL,
                data_publicacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                imagem TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_carrinho (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_produto INTEGER,
                id_carrinho INTEGER,
                quantidade INTEGER,
                FOREIGN KEY(id_produto) REFERENCES produtos(id)
            );
        """)
        conexao.commit()
        conexao.close()

    # Tabela para registrar as compras finalizadas (Histórico)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER,
                data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
                valor_total REAL,
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id_usuario)
            );
        """)
        
        # Tabela para os itens de uma venda finalizada (Snapshot do momento da compra)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_venda (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_venda INTEGER,
                id_produto INTEGER,
                quantidade INTEGER,
                preco_unitario REAL,
                FOREIGN KEY(id_venda) REFERENCES vendas(id),
                FOREIGN KEY(id_produto) REFERENCES produtos(id)
            );
        """)

    def adicionarUsuario(self, usuario, email, senha, cargo):
        conexao, cursor = self.conexao()
        query = "SELECT * FROM usuarios WHERE email = ?;"
        cursor.execute(query, (email,))
        if cursor.fetchone(): 
            conexao.close()
            resposta = "Email já cadastrado"
            return
        
        query = "INSERT INTO usuarios (usuario, email, senha, cargo) VALUES (?, ?, ?, ?);"

        cursor.execute(query, (usuario, email, senha, cargo))
        conexao.commit()
        resposta = "Usuário cadastrado"
        conexao.close()
        return resposta


    def adicionarProdutoAoBanco(self, nome, descricao, categoria, preco, estoque, imagem=None):
        conexao, cursor = self.conexao()
        query = "INSERT INTO produtos (nome, descricao, categoria, preco, estoque, imagem) VALUES (?, ?, ?, ?, ?, ?);"
        
        cursor.execute(query, (nome, descricao, categoria, preco, estoque, imagem))
        conexao.commit()
        conexao.close()
        return

    def obterProdutos(self):
        conexao, cursor = self.conexao()
        query = "SELECT * FROM produtos;"
        cursor.execute(query)
        produtos = cursor.fetchall()
        conexao.close()
        # Convert to list of dicts for easier handling
        lista_produtos = []
        for p in produtos:
            lista_produtos.append({
                "id": p[0],
                "nome": p[1],
                "descricao": p[2],
                "categoria": p[3],
                "preco": p[4],
                "estoque": p[5],
                "imagem": p[6] if len(p) > 6 else None
            })
        return lista_produtos

    def obterProdutoPorId(self, id_produto):
        conexao, cursor = self.conexao()
        query = "SELECT * FROM produtos WHERE id = ?;"
        cursor.execute(query, (id_produto,))
        p = cursor.fetchone()
        conexao.close()
        if p:
            return {
                "id": p[0],
                "nome": p[1],
                "descricao": p[2],
                "categoria": p[3],
                "preco": p[4],
                "estoque": p[5],
                "imagem": p[6] if len(p) > 6 else None
            }
        return None

    def atualizarProduto(self, id_produto, nome, descricao, categoria, preco, estoque, imagem=None):
        conexao, cursor = self.conexao()
        if imagem:
            query = "UPDATE produtos SET nome=?, descricao=?, categoria=?, preco=?, estoque=?, imagem=? WHERE id=?;"
            cursor.execute(query, (nome, descricao, categoria, preco, estoque, imagem, id_produto))
        else:
            query = "UPDATE produtos SET nome=?, descricao=?, categoria=?, preco=?, estoque=? WHERE id=?;"
            cursor.execute(query, (nome, descricao, categoria, preco, estoque, id_produto))
        conexao.commit()
        conexao.close()
        return "Produto atualizado"
    
    def adicionarProdutoACarrinho(self, id_carrinho, id_produto, quantidade):
        conexao, cursor = self.conexao()
        query = "INSERT INTO itens_carrinho (id_produto, id_carrinho, quantidade) VALUES (?, ?, ?)"
        if self.quantidadeEmEstoque(id_produto) >= quantidade:
            cursor.execute(query, (id_produto, id_carrinho, quantidade))
            resposta = "Produto adicionado ao carrinho"
        else: resposta = "Não há produtos suficientes em estoque"
        conexao.commit()
        conexao.close()
        return resposta
    

    def quantidadeEmEstoque(self, id_produto):
        conexao, cursor = self.conexao()
        query = "SELECT estoque FROM produtos WHERE id = ?;"
        cursor.execute(query, (id_produto,))
        res = cursor.fetchone()
        quantidade = res[0] if res else 0

        conexao.close()
        return quantidade


    def controlarEstoque(self, id_produto, quantidade): # quantidade pode ser negativo para diminuir do estoque
        conexao, cursor = self.conexao()
        query = "UPDATE produtos SET estoque = estoque + ? WHERE id = ?;"
        cursor.execute(query, (quantidade, id_produto))
        quantidade = self.quantidadeEmEstoque(id_produto)

        if quantidade < 0:
            self.controlarEstoque(id_produto, abs(quantidade))
        conexao.commit()
        conexao.close()

        return "Quantidade atualizada"


    def removerProduto(self, id_produto):
        conexao, cursor = self.conexao()
        query = "DELETE FROM produtos WHERE id = ?;"
        cursor.execute(query, (id_produto,))
        conexao.commit()
        conexao.close()
        return "Produto deletado"


    def verificarUsuario(self, email, senha):
        conexao, cursor = self.conexao()
        query = "SELECT * FROM usuarios WHERE email = ? and senha = ?;"
        cursor.execute(query, (email, senha))
        usuario = cursor.fetchone()
        print(usuario)
        conexao.close()
        if not usuario:
            return False
        return usuario # Returns the full tuple including cargo

    
    def obterUsuarioPorEmail(self, email):
        conexao, cursor = self.conexao()
        query = "SELECT id_usuario, usuario, cargo FROM usuarios WHERE email = ?;"
        cursor.execute(query, (email,))
        usuario = cursor.fetchone()
        if not usuario:
            conexao.close()
            return False
        
        conexao.close()
        return usuario

    # --- Noticias ---
    def adicionarNoticia(self, titulo, conteudo, imagem=None):
        conexao, cursor = self.conexao()
        query = "INSERT INTO noticias (titulo, conteudo, imagem) VALUES (?, ?, ?);"
        cursor.execute(query, (titulo, conteudo, imagem))
        conexao.commit()
        conexao.close()
        return "Notícia adicionada"

    def obterNoticias(self):
        conexao, cursor = self.conexao()
        query = "SELECT * FROM noticias ORDER BY data_publicacao DESC;"
        cursor.execute(query)
        noticias = cursor.fetchall()
        conexao.close()
        lista_noticias = []
        for n in noticias:
            lista_noticias.append({
                "id": n[0],
                "titulo": n[1],
                "conteudo": n[2],
                "data": n[3],
                "imagem": n[4]
            })
        return lista_noticias

    def obterNoticiaPorId(self, id_noticia):
        conexao, cursor = self.conexao()
        query = "SELECT * FROM noticias WHERE id = ?;"
        cursor.execute(query, (id_noticia,))
        n = cursor.fetchone()
        conexao.close()
        if n:
            return {
                "id": n[0],
                "titulo": n[1],
                "conteudo": n[2],
                "data": n[3],
                "imagem": n[4]
            }
        return None

    def atualizarNoticia(self, id_noticia, titulo, conteudo, imagem=None):
        conexao, cursor = self.conexao()
        if imagem:
            query = "UPDATE noticias SET titulo=?, conteudo=?, imagem=? WHERE id=?;"
            cursor.execute(query, (titulo, conteudo, imagem, id_noticia))
        else:
            query = "UPDATE noticias SET titulo=?, conteudo=? WHERE id=?;"
            cursor.execute(query, (titulo, conteudo, id_noticia))
        conexao.commit()
        conexao.close()
        return "Notícia atualizada"

    def removerNoticia(self, id_noticia):
        conexao, cursor = self.conexao()
        query = "DELETE FROM noticias WHERE id = ?;"
        cursor.execute(query, (id_noticia,))
        conexao.commit()

        def verCarrinho(self, id_usuario):
        conexao, cursor = self.conexao()
        # Fazemos um JOIN para pegar os detalhes do produto baseado no ID que está no carrinho
        query = """
            SELECT ic.id, p.nome, p.preco, ic.quantidade, (p.preco * ic.quantidade) as total_item, p.imagem, p.id
            FROM itens_carrinho ic
            JOIN produtos p ON ic.id_produto = p.id
            WHERE ic.id_carrinho = ?;
        """
        # Nota: Estou assumindo que id_carrinho será o id do usuário logado
        cursor.execute(query, (id_usuario,))
        itens = cursor.fetchall()
        conexao.close()
        
        lista_carrinho = []
        for i in itens:
            lista_carrinho.append({
                "id_item_carrinho": i[0], # ID para remover depois se precisar
                "produto": i[1],
                "preco_unitario": i[2],
                "quantidade": i[3],
                "total_item": i[4],
                "imagem": i[5],
                "id_produto": i[6]
            })
        return lista_carrinho
        conexao.close()
        return "Notícia deletada"

    def removerDoCarrinho(self, id_item_carrinho):
        conexao, cursor = self.conexao()
        query = "DELETE FROM itens_carrinho WHERE id = ?;"
        cursor.execute(query, (id_item_carrinho,))
        conexao.commit()
        conexao.close()
        return "Item removido"


    def finalizarCompra(self, id_usuario):
        conexao, cursor = self.conexao()
        try:
            # 1. Pega os itens do carrinho desse usuário
            cursor.execute("SELECT id_produto, quantidade FROM itens_carrinho WHERE id_carrinho = ?", (id_usuario,))
            itens = cursor.fetchall()
            
            if not itens:
                return False, "Carrinho vazio"

            # 2. Verifica estoque e calcula total
            total = 0
            lista_para_venda = [] # Lista temporária para salvar detalhes
            
            for id_prod, qtd_compra in itens:
                # Pega preço e estoque atual do produto
                cursor.execute("SELECT preco, estoque FROM produtos WHERE id = ?", (id_prod,))
                prod = cursor.fetchone()
                preco, estoque_atual = prod
                
                if estoque_atual < qtd_compra:
                    raise Exception(f"Produto ID {id_prod} sem estoque suficiente.")
                
                total += preco * qtd_compra
                lista_para_venda.append((id_prod, qtd_compra, preco))

            # 3. Cria a Venda
            cursor.execute("INSERT INTO vendas (id_usuario, valor_total) VALUES (?, ?)", (id_usuario, total))
            id_venda = cursor.lastrowid # Pega o ID da venda recém criada

            # 4. Processa os itens: Salva em itens_venda e Baixa Estoque
            for id_prod, qtd, preco in lista_para_venda:
                # Salva histórico
                cursor.execute("""
                    INSERT INTO itens_venda (id_venda, id_produto, quantidade, preco_unitario) 
                    VALUES (?, ?, ?, ?)
                """, (id_venda, id_prod, qtd, preco))
                
                # Baixa estoque
                cursor.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", (qtd, id_prod))

            # 5. Limpa o carrinho do usuário
            cursor.execute("DELETE FROM itens_carrinho WHERE id_carrinho = ?", (id_usuario,))

            conexao.commit() # Confirma todas as alterações
            return True, "Compra realizada com sucesso!"

        except Exception as e:
            conexao.rollback() # Se der erro, desfaz tudo
            return False, str(e)
        finally:
            conexao.close()




