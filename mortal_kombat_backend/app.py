from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from datetime import date

app = Flask(__name__)
CORS(app)

# --- Configuração do Banco de Dados ---
DATABASE = os.path.join(os.path.dirname(__file__), os.path.pardir, 'mortal_kombat.db')

# Função para obter a conexão com o banco de dados
def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise

# --- Rotas ---


@app.route('/api/jogos', methods=['GET'])
def get_jogos():
    conn = get_db_connection()
    try:
        jogos_cursor = conn.execute('''
            SELECT
                id_jogo,
                titulo,
                COALESCE(ano_lancamento, ano) AS ano_para_exibir,
                plataforma
            FROM
                jogo
            ORDER BY
                ano_para_exibir ASC
        ''').fetchall()

        jogos = []
        for jogo_row in jogos_cursor:
            ano_formatado = str(jogo_row['ano_para_exibir']) if jogo_row['ano_para_exibir'] is not None else 'N/A'
            jogos.append({
                'id': jogo_row['id_jogo'],
                'titulo': jogo_row['titulo'],
                'ano': ano_formatado,
                'plataforma': jogo_row['plataforma']
            })
        return jsonify(jogos)
    except Exception as e:
        print(f"Erro no backend ao buscar jogos: {e}")
        return jsonify({"error": f"Erro ao buscar jogos no banco de dados: {str(e)}"}), 500
    finally:
        conn.close()

@app.route('/api/personagens', methods=['GET'])
def get_personagens():
    conn = get_db_connection()
    try:
        limit = request.args.get('limit', 8, type=int)
        offset = request.args.get('offset', 0, type=int)

        personagens_cursor = conn.execute(f'''
            SELECT
                MIN(p.id_personagem) AS id_personagem,
                p.nome,
                MAX(p.raca) AS raca,
                MAX(p.status_vida) AS status_vida,
                MAX(p.origem) AS origem,
                MAX(p.alinhamento) AS alinhamento,
                MAX(p.habilidade_principal) AS habilidade_principal_nome,
                MAX(m.nome) AS nome_mundo,
                MAX(m.tipo) AS tipo_mundo,
                (SELECT COUNT(DISTINCT nome) FROM personagem) AS total_personagens_unicos_bd
            FROM
                personagem p
            LEFT JOIN
                mundo m ON p.id_mundo = m.id_mundo
            GROUP BY
                p.nome
            ORDER BY
                RANDOM()
            LIMIT {limit} OFFSET {offset}
        ''').fetchall()

        personagens = []
        total_personagens = 0
        if personagens_cursor:
            total_personagens = personagens_cursor[0]['total_personagens_unicos_bd']

        for p_row in personagens_cursor:
            personagens.append({
                'id': p_row['id_personagem'],
                'nome': p_row['nome'],
                'raca': p_row['raca'],
                'status_vida': p_row['status_vida'],
                'origem': p_row['origem'],
                'alinhamento': p_row['alinhamento'],
                'habilidade_principal': p_row['habilidade_principal_nome'],
                'nome_mundo': p_row['nome_mundo'],
                'tipo_mundo': p_row['tipo_mundo']  
            })

        return jsonify({'personagens': personagens, 'total': total_personagens})

    except Exception as e:
        print(f"Erro no backend ao buscar personagens: {e}")
        return jsonify({"error": f"Erro ao buscar personagens no banco de dados: {str(e)}"}), 500
    finally:
        conn.close()


@app.route('/api/fatalities', methods=['GET'])
def get_fatalities():
    conn = get_db_connection()
    try:
        limit = request.args.get('limit', 9, type=int)
        offset = request.args.get('offset', 0, type=int)

        fatalities_cursor = conn.execute('''
            SELECT
                id_fatality,
                nome,
                tipo,
                brutalidade,
                origem,
                COUNT(*) OVER() AS total_fatalities_bd
            FROM
                fatality
            ORDER BY
                id_fatality ASC -- Ordena por ID para consistência
            LIMIT ? OFFSET ?
        ''', (limit, offset)).fetchall()

        fatalities = []
        total_fatalities = 0
        if fatalities_cursor:
            total_fatalities = fatalities_cursor[0]['total_fatalities_bd']

        for f_row in fatalities_cursor:
            fatalities.append({
                'id': f_row['id_fatality'],
                'nome': f_row['nome'],
                'tipo': f_row['tipo'],
                'brutalidade': f_row['brutalidade'],
                'origem': f_row['origem']
            })

        return jsonify({'fatalities': fatalities, 'total': total_fatalities})

    except Exception as e:
        print(f"Erro no backend ao buscar fatalities: {e}")
        return jsonify({"error": f"Erro ao buscar fatalities no banco de dados: {str(e)}"}), 500
    finally:
        conn.close()


@app.route('/api/armas', methods=['GET'])
def get_armas():
    conn = get_db_connection()
    try:
        limit = request.args.get('limit', 9, type=int)
        offset = request.args.get('offset', 0, type=int)

        
        armas_cursor = conn.execute('''
            SELECT
                MIN(id_arma) AS id_arma, 
                nome,
                MAX(tipo) AS tipo, -- Pega um tipo representativo
                MAX(raridade) AS raridade, -- Pega uma raridade representativa
                MAX(alcance) AS alcance, -- Pega um alcance representativo
                MAX(dano) AS dano, -- Pega um dano representativo
                (SELECT COUNT(DISTINCT nome) FROM arma) AS total_armas_unicas_bd 
            FROM
                arma
            GROUP BY
                nome
            ORDER BY
                nome ASC 
            LIMIT ? OFFSET ?
        ''', (limit, offset)).fetchall()

        armas = []
        total_armas = 0
        if armas_cursor: 
            total_armas = armas_cursor[0]['total_armas_unicas_bd']

        for a_row in armas_cursor:
            armas.append({
                'id': a_row['id_arma'],
                'nome': a_row['nome'],
                'tipo': a_row['tipo'],
                'raridade': a_row['raridade'],
                'alcance': a_row['alcance'],
                'dano': a_row['dano']
            })

        return jsonify({'armas': armas, 'total': total_armas})

    except Exception as e:
        print(f"Erro no backend ao buscar armas: {e}")
        return jsonify({"error": f"Erro ao buscar armas no banco de dados: {str(e)}"}), 500
    finally:
        conn.close()


# Rodar a aplicação
if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        print(f"ATENÇÃO: O arquivo do banco de dados '{DATABASE}' NÃO foi encontrado.")
        print("Por favor, crie o banco de dados e as tabelas, ou verifique o caminho.")
    app.run(debug=True)
