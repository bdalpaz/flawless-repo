from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app) # Habilita o CORS para permitir requisições do frontend

# --- Configurações do Banco de Dados ---
# ATENÇÃO: Substitua 'sua_senha_do_postgres' pela senha real do seu usuário postgres!
DB_HOST = "localhost"
DB_NAME = "mortal_kombat_db"
DB_USER = "postgres"
DB_PASS = "sua_senha_do_postgres" # <--- Mude AQUI!

# Função para conectar ao banco de dados
def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST,
                            database=DB_NAME,
                            user=DB_USER,
                            password=DB_PASS)
    return conn

# --- Endpoint de Teste ---
@app.route('/')
def home():
    return "Backend do Mortal Kombat está rodando!"

@app.route('/personagens')
def get_personagens():
    conn = None
    cur = None
    personagens = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id_personagem, nome, raca, idade, alinhamento FROM Personagem;')
        # FetchAll busca todas as linhas. desc é o nome da coluna no banco
        # Usa uma list comprehension para formatar os resultados em um dicionário
        personagens = [
            {"id": row[0], "nome": row[1], "raca": row[2], "idade": row[3], "alinhamento": row[4]}
            for row in cur.fetchall()
        ]
    except Exception as e:
        print(f"Erro ao buscar personagens: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    return jsonify(personagens)

if __name__ == '__main__':
    app.run(debug=True) # debug=True reinicia o servidor automaticamente em caso de mudanças
