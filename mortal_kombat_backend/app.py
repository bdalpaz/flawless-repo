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

# --- Rotas da API ---

# Rota para listar todos os jogos
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

# Rota para listar todos os personagens com paginação
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
                (SELECT COUNT(DISTINCT nome) FROM personagem) AS total_personagens_unicos_bd -- Alternativa mais segura para o total único
            FROM
                personagem p 
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
                'habilidade_principal': p_row['habilidade_principal_nome']
            })
        
        
        return jsonify({'personagens': personagens, 'total': total_personagens})

    except Exception as e:
         print(f"Erro no backend ao buscar personagens: {e}")
         return jsonify({"error": f"Erro ao buscar personagens no banco de dados: {str(e)}"}), 500
    finally:
        conn.close()

        
# Rota para obter detalhes de um personagem específico por ID (completa com JOINs)
@app.route('/api/personagens/<int:personagem_id>', methods=['GET'])
def get_personagem_detalhes(personagem_id):
    conn = get_db_connection()
    try:
        personagem_info = conn.execute(
            '''
            SELECT 
                p.id_personagem, 
                p.nome, 
                p.raca, 
                p.idade, 
                p.status_vida, 
                p.origem, 
                p.alinhamento,
                p.habilidade_principal, 
                p.id_fatality, 
                m.nome AS nome_mundo, 
                m.tipo AS tipo_mundo,
                t.tipo AS tipo_transformacao,
                t.forma AS forma_transformacao,
                c.nome AS nome_cla,
                c.simbolo AS simbolo_cla,
                a.nome AS nome_arma,
                a.tipo AS tipo_arma,
                a.dano AS dano_arma
            FROM 
                personagem p  
            LEFT JOIN 
                mundo m ON p.id_mundo = m.id_mundo 
            LEFT JOIN 
                transformacao t ON p.id_transformacao = t.id_transformacao 
            LEFT JOIN
                cla c ON p.id_cla = c.id_cla 
            LEFT JOIN
                arma a ON p.id_arma = a.id_arma 
            WHERE 
                p.id_personagem = ?
            ''', (personagem_id,)
      ).fetchone()

        if personagem_info is None:
            return jsonify({'message': 'Personagem não encontrado'}), 404
        
        personagem_data = dict(personagem_info)
        personagem_data['id'] = personagem_data.pop('id_personagem')

    except Exception as e:
         print(f"Erro no backend ao buscar personagens: {e}")
         return jsonify({"error": f"Erro ao buscar personagens no banco de dados: {str(e)}"}), 500
    finally:
        conn.close()
       


# Rota para listar todos os fatalities com paginação
@app.route('/api/fatalities', methods=['GET'])
def get_fatalities():
    conn = get_db_connection()
    try:
        limit = request.args.get('limit', 9, type=int) 
        offset = request.args.get('offset', 0, type=int)

        fatalities_cursor = conn.execute(f'''
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
                RANDOM()
            LIMIT {limit} OFFSET {offset}
        ''').fetchall()

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
        # Pega os parâmetros 'limit' e 'offset' da URL, com valores padrão
        limit = request.args.get('limit', 9, type=int) 
        offset = request.args.get('offset', 0, type=int)

        # Consulta a tabela 'arma'
        armas_cursor = conn.execute(f'''
            SELECT 
                id_arma,
                nome,
                tipo,
                raridade,
                alcance,
                dano,
                COUNT(*) OVER() AS total_armas_bd 
            FROM
                arma
            ORDER BY 
                RANDOM()
            LIMIT {limit} OFFSET {offset}
        ''').fetchall()

        armas = []
        total_armas = 0
        if armas_cursor: # Pega o total do primeiro registro (já que COUNT(*) OVER() retorna o mesmo para todos)
            total_armas = armas_cursor[0]['total_armas_bd']

        for a_row in armas_cursor:
            armas.append({
                'id': a_row['id_arma'],
                'nome': a_row['nome'],
                'tipo': a_row['tipo'],
                'raridade': a_row['raridade'],
                'alcance': a_row['alcance'],
                'dano': a_row['dano']
            })
        
        # Retorna os dados das armas e o total para o frontend
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