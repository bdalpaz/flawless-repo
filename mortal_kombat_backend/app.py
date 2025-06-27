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
                MAX(t.tipo) AS tipo_transformacao,  -- ADICIONADO: Tipo da transformação
                MAX(t.forma) AS forma_transformacao, -- ADICIONADO: Forma da transformação
                (SELECT COUNT(DISTINCT nome) FROM personagem) AS total_personagens_unicos_bd
            FROM
                personagem p
            LEFT JOIN
                mundo m ON p.id_mundo = m.id_mundo
            LEFT JOIN
                transformacao t ON p.id_transformacao = t.id_transformacao -- ADICIONADO: Junção com a tabela transformação
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
                'tipo_mundo': p_row['tipo_mundo'],
                'tipo_transformacao': p_row['tipo_transformacao'], 
                'forma_transformacao': p_row['forma_transformacao']
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

        # CORREÇÃO PRINCIPAL AQUI PARA DUPLICAÇÃO E PERSONAGEM RESPONSÁVEL
        # Usamos uma CTE (Common Table Expression) ou subconsulta para pegar o personagem principal
        # e depois fazemos a junção para garantir unicidade do Fatality.
        fatalities_cursor = conn.execute(f'''
            WITH FatalityPersonagem AS (
                SELECT
                    f.id_fatality,
                    f.nome,
                    f.tipo,
                    f.brutalidade,
                    f.origem,
                    MIN(p.nome) AS nome_personagem_responsavel -- Pega o primeiro personagem que tem esse fatality
                FROM
                    fatality f
                LEFT JOIN
                    personagem p ON f.id_fatality = p.id_fatality
                GROUP BY
                    f.id_fatality, f.nome, f.tipo, f.brutalidade, f.origem
            )
            SELECT
                fp.id_fatality,
                fp.nome,
                fp.tipo,
                fp.brutalidade,
                fp.origem,
                fp.nome_personagem_responsavel,
                (SELECT COUNT(*) FROM Fatality) AS total_fatalities_bd -- Conta o total de fatalities na tabela Fatality (sem junções)
            FROM
                FatalityPersonagem fp
            ORDER BY
                fp.nome ASC -- Ordena por nome do fatality (ou RANDOM() se preferir)
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
                'origem': f_row['origem'],
                'personagem_responsavel': f_row['nome_personagem_responsavel']
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

        armas_cursor = conn.execute(f'''
            SELECT
                a.id_arma,
                a.nome,
                a.tipo,
                a.raridade,
                a.alcance,
                a.dano,
                MIN(p.nome) AS nome_personagem_responsavel, -- ADDED: Name of the responsible character
                (SELECT COUNT(DISTINCT id_arma) FROM arma) AS total_armas_bd -- Count of unique weapons
            FROM
                arma a
            LEFT JOIN
                personagem p ON a.id_arma = p.id_arma -- ADDED: Join with personagem table
            GROUP BY
                a.id_arma, a.nome, a.tipo, a.raridade, a.alcance, a.dano -- Group by all non-aggregated columns from arma
            ORDER BY
                a.nome ASC -- Or RANDOM() if you prefer random order
            LIMIT ? OFFSET ?
        ''', (limit, offset)).fetchall()

        armas = []
        total_armas = 0
        if armas_cursor:
            total_armas = armas_cursor[0]['total_armas_bd']
 
        for a_row in armas_cursor:
            armas.append({
                'id': a_row['id_arma'],
                'nome': a_row['nome'],
                'tipo': a_row['tipo'],
                'raridade': a_row['raridade'],
                'alcance': a_row['alcance'],
                'dano': a_row['dano'],
                'personagem_responsavel': a_row['nome_personagem_responsavel'] # ADDED to JSON
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
