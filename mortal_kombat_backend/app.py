from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import Error
from flask_cors import CORS # Importar CORS

app = Flask(__name__)
CORS(app) # Habilita CORS para todas as rotas (para desenvolvimento)

# --- Configurações do Banco de Dados ---
# ATENÇÃO: Substitua 'seu_usuario', 'sua_senha', 'seu_host', 'sua_porta', 'seu_banco'
DB_HOST = "localhost"
DB_NAME = "seu_banco"
DB_USER = "seu_usuario"
DB_PASS = "sua_senha"
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

# --- Rota para Obter TODOS os Personagens (para a grid inicial) ---
@app.route('/api/personagens', methods=['GET'])
def get_personagens():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"erro": "Não foi possível conectar ao banco de dados"}), 500

    personagens_json = []
    try:
        cur = conn.cursor()
        # Seleciona dados básicos do personagem e o ID da fatality associada
        cur.execute("SELECT id_personagem, Nome, Raca, Status_vida, id_fatality FROM personagem ORDER BY Nome;")
        personagens_data = cur.fetchall()

        for p in personagens_data:
            personagens_json.append({
                "id": p[0],
                "nome": p[1],
                "raca": p[2],
                "status_vida": p[3],
                "id_fatality": p[4] # Usado para buscar detalhes da fatality depois
                # Você pode adicionar um campo 'image' aqui se tiver URLs de imagem na tabela personagem
                # Ex: "image": f"https://seusite.com/imagens/personagens/{p[0]}.png"
                # Ou usar um mapeamento local no JS se as imagens forem estáticas e baseadas no nome
                # Por agora, usaremos um mapeamento no JS para as imagens que você já tem.
            })
        
    except Error as e:
        print(f"Erro ao buscar personagens: {e}")
        return jsonify({"erro": "Erro ao buscar dados dos personagens"}), 500
    finally:
        if conn:
            conn.close()
    return jsonify(personagens_json)


# --- Rota para Obter DETALHES de um Personagem por ID (para o modal) ---
@app.route('/api/personagens/<int:personagem_id>', methods=['GET'])
def get_personagem_detalhes(personagem_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"erro": "Não foi possível conectar ao banco de dados"}), 500

    try:
        cur = conn.cursor()

        # 1. Buscar dados do personagem
        cur.execute("SELECT id_personagem, Nome, Raca, Idade, Status_vida, id_fatality FROM personagem WHERE id_personagem = %s;", (personagem_id,))
        personagem_data = cur.fetchone()
        if not personagem_data:
            return jsonify({"mensagem": "Personagem não encontrado"}), 404

        personagem_dict = {
            "id": personagem_data[0],
            "nome": personagem_data[1],
            "raca": personagem_data[2],
            "idade": personagem_data[3],
            "status_vida": personagem_data[4],
            "id_fatality": personagem_data[5],
            "habilidades": [], # Adicionaremos isso
            "fatality_detalhes": {} # Adicionaremos isso
        }

        # 2. Buscar habilidades do personagem
        cur.execute("""
            SELECT h.Nome, h.Tipo, h.Categoria, h.Elemento
            FROM habilidade h
            JOIN personagem_habilidade ph ON h.id_habilidade = ph.id_habilidade
            WHERE ph.id_personagem = %s;
        """, (personagem_id,))
        habilidades_data = cur.fetchall()
        for h in habilidades_data:
            personagem_dict["habilidades"].append({
                "nome": h[0], "tipo": h[1], "categoria": h[2], "elemento": h[3]
            })

        # 3. Buscar detalhes da Fatality (se id_fatality existir)
        if personagem_dict["id_fatality"]:
            cur.execute("SELECT Nome, Brutalidade, Tipo, Origem FROM fatality WHERE id_fatality = %s;", (personagem_dict["id_fatality"],))
            fatality_data = cur.fetchone()
            if fatality_data:
                personagem_dict["fatality_detalhes"] = {
                    "nome": fatality_data[0],
                    "brutalidade": fatality_data[1],
                    "tipo": fatality_data[2],
                    "origem": fatality_data[3]
                }
        
        cur.close()
        conn.close()
        return jsonify(personagem_dict)

    except Error as e:
        print(f"Erro ao buscar detalhes do personagem: {e}")
        return jsonify({"erro": "Erro ao buscar dados do personagem"}), 500
    finally:
        if conn:
            conn.close()

# --- Rota para Obter TODOS os Jogos (para a timeline) ---
@app.route('/api/jogos', methods=['GET'])
def get_jogos():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"erro": "Não foi possível conectar ao banco de dados"}), 500

    jogos_json = []
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_jogo, Título, Ano, Plataforma FROM jogo ORDER BY Ano;")
        jogos_data = cur.fetchall()

        for j in jogos_data:
            jogos_json.append({
                "id": j[0],
                "titulo": j[1],
                "ano": j[2],
                "plataforma": j[3]
            })
        
    except Error as e:
        print(f"Erro ao buscar jogos: {e}")
        return jsonify({"erro": "Erro ao buscar dados dos jogos"}), 500
    finally:
        if conn:
            conn.close()
    return jsonify(jogos_json)


# --- Executar o aplicativo Flask ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)