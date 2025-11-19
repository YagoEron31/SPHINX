import hashlib
from DBmanager import dbManager

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

db = dbManager("banco.db")
db.criarTabelas()

email = "admin@sphinx.com"
senha_plain = "adminsphinx"
senha_hash = hash_password(senha_plain)
usuario = "Admin"

# Check if exists
existing = db.obterUsuarioPorEmail(email)
if existing:
    # Update password to ensure it is hashed
    conexao, cursor = db.conexao()
    cursor.execute("UPDATE usuarios SET senha = ?, cargo = 1 WHERE email = ?", (senha_hash, email))
    conexao.commit()
    conexao.close()
    print(f"User {email} updated with hashed password.")
else:
    db.adicionarUsuario(usuario, email, senha_hash, 1)
    print(f"Admin user created: {email}")
