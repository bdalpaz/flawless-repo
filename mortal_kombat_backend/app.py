# app.py

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from datetime import date 

app = Flask(__name__)
CORS(app) 

# --- Configuração do Banco de Dados ---
# O caminho está correto para a sua estrutura de pastas
DATABASE = os.path.join(os.path.dirname(__file__), os.path.pardir, 'mortal_kombat.db') 

# Função para obter uma conexão com o banco de dados
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
    # REMOVIDO: O print de depuração das tabelas
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
                MIN(p.id_personagem) AS id_personagem, -- Use o alias 'p' aqui também
                p.nome,
                MAX(p.raca) AS raca,
                MAX(p.status_vida) AS status_vida,
                MAX(p.origem) AS origem,
                MAX(p.alinhamento) AS alinhamento,
                MAX(p.habilidade_principal) AS habilidade_principal_nome,
                -- A contagem do total é um pouco mais complexa com GROUP BY e OVER(),
                -- vamos separá-la para evitar conflitos, ou simplificar o COUNT OVER.
                -- Para este erro específico, o problema está nas colunas selecionadas.
                -- Vamos manter o COUNT(*) OVER() mas garantir que as outras colunas estejam bem definidas.
                (SELECT COUNT(DISTINCT nome) FROM personagem) AS total_personagens_unicos_bd -- Alternativa mais segura para o total único
            FROM
                personagem p -- Dando um alias 'p' para a tabela
            GROUP BY
                p.nome
            ORDER BY
                RANDOM() 
            LIMIT {limit} OFFSET {offset}
        ''').fetchall()

        personagens = []
        total_personagens = 0 
        if personagens_cursor: 
            # Pega o total do primeiro registro (que é o mesmo para todos)
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
                p.habilidade_principal, -- ADICIONADO: Seleciona a habilidade principal
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
        limit = request.args.get('limit', 9, type=int) # Padrão: 9 fatalities por vez
        offset = request.args.get('offset', 0, type=int) # Padrão: Começa do 0

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
                nome ASC -- Ou por id_fatality ASC
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


# Rodar a aplicação
if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        print(f"ATENÇÃO: O arquivo do banco de dados '{DATABASE}' NÃO foi encontrado.")
        print("Por favor, crie o banco de dados e as tabelas, ou verifique o caminho.")
    app.run(debug=True)