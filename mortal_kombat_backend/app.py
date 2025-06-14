from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import Error

app = Flask(__name__)


DB_HOST = "localhost"
DB_NAME = "mortal_kombat_db"
DB_USER = "postgres"
DB_PASS = "postgres"
DB_PORT = "5432" 

def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    return conn

@app.route('/personagens', methods=['GET'])
def get_personagens():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"erro": "Não foi possível conectar ao banco de dados"}), 500

    try:
        cur = conn.cursor()
        cur.execute("SELECT id_personagem, Nome, Raca, Status_vida FROM personagem;")
        personagens = cur.fetchall()
        cur.close()
        conn.close()

        # Converte os resultados para um formato JSON mais amigável
        personagens_json = []
        for p in personagens:
            personagens_json.append({
                "id_personagem": p[0],
                "nome": p[1],
                "raca": p[2],
                "status_vida": p[3]
            })
        return jsonify(personagens_json)

    except Error as e:
        print(f"Erro ao buscar personagens: {e}")
        return jsonify({"erro": "Erro ao buscar dados dos personagens"}), 500
    finally:
        if conn:
            conn.close()

# --- Rota de Exemplo: Obter um personagem por ID ---
@app.route('/personagens/<int:personagem_id>', methods=['GET'])
def get_personagem_by_id(personagem_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"erro": "Não foi possível conectar ao banco de dados"}), 500

    try:
        cur = conn.cursor()
        cur.execute("SELECT id_personagem, Nome, Raca, Status_vida FROM personagem WHERE id_personagem = %s;", (personagem_id,))
        personagem = cur.fetchone()
        cur.close()
        conn.close()

        if personagem:
            personagem_json = {
                "id_personagem": personagem[0],
                "nome": personagem[1],
                "raca": personagem[2],
                "status_vida": personagem[3]
            }
            return jsonify(personagem_json)
        else:
            return jsonify({"mensagem": "Personagem não encontrado"}), 404

    except Error as e:
        print(f"Erro ao buscar personagem por ID: {e}")
        return jsonify({"erro": "Erro ao buscar dados do personagem"}), 500
    finally:
        if conn:
            conn.close()

# --- Executar o aplicativo Flask ---
if __name__ == '__main__':
    # ATENÇÃO: Para permitir que seu front-end (em outra porta) acesse o back-end,
    # você precisará habilitar CORS. A maneira mais fácil para desenvolvimento é:
    # pip install flask-cors
    from flask_cors import CORS
    CORS(app) # Habilita CORS para todas as rotas
    app.run(debug=True, port=5000) # O debug=True reinicia o servidor automaticamente em mudanças