import pandas as pd
import psycopg2
from psycopg2 import sql
import os

# --- Configurações do Banco de Dados ---
DB_HOST = "localhost"
DB_NAME = "mortal_kombat_db"
DB_USER = "postgres"
DB_PASS = "postgres" 

def get_db_connection():
    """Establish and return a database connection."""
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

def parse_date_optional(date_str):
    """Safely parses date strings, returns None for NaT or unparseable."""
    if pd.isna(date_str) or not isinstance(date_str, str) or not date_str.strip():
        return None
    try:
        # Try parsing as YYYY-MM-DD first (standard)
        return pd.to_datetime(date_str, format='%Y-%m-%d').date()
    except ValueError:
        # Fallback to DD/MM/YYYY if first fails
        try:
            return pd.to_datetime(date_str, format='%d/%m/%Y').date()
        except ValueError:
            print(f"Warning: Could not parse date '{date_str}'. Returning None.")
            return None

def load_simple_csv_to_db(csv_filepath, db_table_name, column_mapping=None, date_columns=None):
    """
    Loads data from a simple CSV into a database table.
    Assumes CSV has a single header row and columns directly map or are specified in column_mapping.
    """
    print(f"\n--- Loading '{csv_filepath}' into '{db_table_name}' ---")
    conn = None
    cur = None
    try:
        if not os.path.exists(csv_filepath):
            print(f"Erro: Arquivo CSV '{csv_filepath}' não encontrado. Pulando.")
            return False

        df = pd.read_csv(csv_filepath)

        # Remove 'Unnamed' columns which often appear from Excel exports if they are empty
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        if df.empty:
            print(f"Aviso: Arquivo CSV '{csv_filepath}' está vazio. Pulando.")
            return False

        # Apply column renaming if mapping is provided
        if column_mapping:
            df = df.rename(columns=column_mapping)
            # Filter DataFrame to only include columns that are targets in the DB
            df_cols_present = [db_col for csv_col, db_col in column_mapping.items() if csv_col in df.columns]
            df = df[df_cols_present]


        # Apply date parsing
        if date_columns:
            for col in date_columns:
                if col in df.columns:
                    df[col] = df[col].apply(parse_date_optional)

        conn = get_db_connection()
        cur = conn.cursor()

        # Get actual DB table columns to ensure correct insertion order and ignore serial PKs from CSV
        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{db_table_name}';")
        db_cols_info = [row[0] for row in cur.fetchall()]

        # Filter DataFrame columns to match DB table columns and exclude auto-increment IDs
        # The db_cols_info list should contain all insertable columns.
        df_cols_for_insert = [
            col for col in df.columns
            if col in db_cols_info and not (col.startswith('id_') and col.replace('id_', '') == db_table_name and col in db_cols_info)
        ]

        if not df_cols_for_insert:
            print(f"Erro: Nenhuma coluna mapeada para a tabela '{db_table_name}' do CSV '{csv_filepath}'. Verifique o mapeamento.")
            return False

        # Construct dynamic INSERT query
        columns_sql = sql.SQL(", ").join(map(sql.Identifier, df_cols_for_insert))
        insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(db_table_name),
            columns_sql,
            sql.SQL(", ").join(sql.Placeholder() * len(df_cols_for_insert))
        )

        for _, row in df.iterrows():
            values = [row[col] for col in df_cols_for_insert]
            cur.execute(insert_query, values)

        conn.commit()
        print(f"Sucesso: {len(df)} linhas carregadas em '{db_table_name}'.")
        return True

    except Exception as e:
        print(f"Falha ao carregar dados para '{db_table_name}' de '{csv_filepath}'. Erro: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def load_personagem_and_junction_data(personagem_csv_filepath):
    """
    Handles loading of Personagem data and its related junction tables
    by resolving foreign keys (names to IDs).
    """
    print(f"\n--- Carregando '{personagem_csv_filepath}' e tabelas de junção ---")
    conn = None
    cur = None
    try:
        if not os.path.exists(personagem_csv_filepath):
            print(f"Erro: Arquivo CSV '{personagem_csv_filepath}' não encontrado. Pulando Personagem e junções.")
            return False

        df_personagem = pd.read_csv(personagem_csv_filepath)
        df_personagem = df_personagem.loc[:, ~df_personagem.columns.str.contains('^Unnamed')] # Clean Unnamed cols

        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch all necessary ID mappings from already populated tables
        cur.execute("SELECT id_cla, nome FROM Cla;")
        cla_map = {row[1]: row[0] for row in cur.fetchall()}

        cur.execute("SELECT id_mundo, nome FROM Mundo;")
        mundo_map = {row[1]: row[0] for row in cur.fetchall()}

        cur.execute("SELECT id_arma, nome FROM Arma;")
        arma_map = {row[1]: row[0] for row in cur.fetchall()}

        cur.execute("SELECT id_transformacao, tipo FROM Transformacao;")
        transformacao_map = {row[1]: row[0] for row in cur.fetchall()} # Assuming 'tipo' is transformation name

        cur.execute("SELECT id_habilidade, nome FROM Habilidade;")
        habilidade_map = {row[1]: row[0] for row in cur.fetchall()}

        cur.execute("SELECT id_jogo, titulo FROM Jogo;")
        jogo_map = {row[1]: row[0] for row in cur.fetchall()}

        # --- Load Personagem ---
        print("  - Inserindo dados na tabela Personagem...")
        personagem_id_map = {} # To map personagem_nome -> id_personagem

        for index, row in df_personagem.iterrows():
            try:
                # Get FK IDs
                id_cla = cla_map.get(row.get('Clã'))
                id_mundo = mundo_map.get(row.get('Mundo'))
                id_arma = arma_map.get(row.get('Arma Principal'))
                id_transformacao = transformacao_map.get(row.get('Transformação'))

                # Prepare values for Personagem table
                # Check for NaNs and replace with None for DB insertion
                nome = row.get('Nome') if pd.notna(row.get('Nome')) else None
                raca = row.get('Raça') if pd.notna(row.get('Raça')) else None
                idade = int(row.get('Idade')) if pd.notna(row.get('Idade')) else None
                status_vida = row.get('Status') if pd.notna(row.get('Status')) else None
                origem = row.get('Origem') if pd.notna(row.get('Origem')) else None
                alinhamento = row.get('Alinhamento') if pd.notna(row.get('Alinhamento')) else None

                # Insert into Personagem and get the generated id_personagem
                insert_query = """
                INSERT INTO Personagem (nome, raca, idade, status_vida, origem, alinhamento, id_cla, id_mundo, id_arma, id_transformacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_personagem;
                """
                cur.execute(insert_query, (nome, raca, idade, status_vida, origem, alinhamento, id_cla, id_mundo, id_arma, id_transformacao))
                personagem_id = cur.fetchone()[0]
                personagem_id_map[nome] = personagem_id # Store for later use in junction tables

            except Exception as e:
                print(f"  Aviso: Falha ao inserir Personagem '{row.get('Nome')}'. Erro: {e}")
        conn.commit()
        print(f"  - Personagens carregados. Mapeamento de IDs: {len(personagem_id_map)} personagens.")
# --- Load Personagem_Habilidade ---
        print("  - Inserindo dados em Personagem_Habilidade...")
        for index, row in df_personagem.iterrows():
            personagem_nome = row.get('Nome')
            habilidades_str = row.get('Habilidades')
            p_id = personagem_id_map.get(personagem_nome)

            if p_id and pd.notna(habilidades_str) and isinstance(habilidades_str, str):
                habilidades = [h.strip() for h in habilidades_str.split(',') if h.strip()]
                for habilidade_nome in habilidades:
                    h_id = habilidade_map.get(habilidade_nome)
                    if h_id:
                        try:
                            cur.execute(
                                "INSERT INTO Personagem_Habilidade (id_personagem, id_habilidade) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                                (p_id, h_id)
                            )
                        except Exception as e:
                            print(f"    Aviso: Falha ao inserir Personagem_Habilidade para {personagem_nome}-{habilidade_nome}. Erro: {e}")
        conn.commit()
        print("  - Personagem_Habilidade processado.")

        # --- Load Personagem_Jogo ---
        print("  - Inserindo dados em Personagem_Jogo...")
        for index, row in df_personagem.iterrows():
            personagem_nome = row.get('Nome')
            jogos_str = row.get('Jogos')
            p_id = personagem_id_map.get(personagem_nome)

            if p_id and pd.notna(jogos_str) and isinstance(jogos_str, str):
                jogos = [j.strip() for j in jogos_str.split(',') if j.strip()]
                for jogo_titulo in jogos:
                    j_id = jogo_map.get(jogo_titulo)
                    if j_id:
                        try:
                            # Assuming 'papel' is not in CSV or can be default
                            cur.execute(
                                "INSERT INTO Personagem_Jogo (id_personagem, id_jogo) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                                (p_id, j_id)
                            )
                        except Exception as e:
                            print(f"    Aviso: Falha ao inserir Personagem_Jogo para {personagem_nome}-{jogo_titulo}. Erro: {e}")
        conn.commit()
        print("  - Personagem_Jogo processado.")

        # --- Load Rivalidade (if not using separate rivalidade.csv) ---
        # Assuming 'Rivais' column in Personagem CSV lists rival names
        # If 'rivalidade - Página1.csv' is comprehensive, use that instead.
        # Given 'rivalidade - Página1.csv' exists, we'll use it in main().
        # So this block is commented out:
        """
        print("  - Processando rivalidades da planilha de Personagem (se aplicável)...")
        for index, row in df_personagem.iterrows():
            personagem1_nome = row.get('Nome')
            rivais_str = row.get('Rivais')
            p1_id = personagem_id_map.get(personagem1_nome)

            if p1_id and pd.notna(rivais_str) and isinstance(rivais_str, str):
                rivais = [r.strip() for r in rivais_str.split(',') if r.strip()]
                for rival_nome in rivais:
                    p2_id = personagem_id_map.get(rival_nome)

                    if p2_id and p1_id != p2_id:
                        # Prevent duplicate rivalry entries (A-B and B-A are the same rivalry)
                        cur.execute(
                            "SELECT COUNT(*) FROM Rivalidade WHERE (id_personagem1 = %s AND id_personagem2 = %s) OR (id_personagem1 = %s AND id_personagem2 = %s);",
                            (p1_id, p2_id, p2_id, p1_id)
                        )
                        if cur.fetchone()[0] == 0: # If rivalry doesn't exist
                            try:
                                # Default values for 'motivo', 'status', 'num_vitorias'
                                cur.execute(
                                    "INSERT INTO Rivalidade (id_personagem1, id_personagem2, motivo, status, num_vitorias) VALUES (%s, %s, %s, %s, %s);",
                                    (p1_id, p2_id, 'Desconhecido', 'Ativa', 0)
                                )
                            except Exception as e:
                                print(f"    Aviso: Falha ao inserir Rivalidade para {personagem1_nome}-{rival_nome}. Erro: {e}")
        conn.commit()
        print("  - Rivalidades da planilha de Personagem processadas.")
        """

    except Exception as e:
        print(f"Falha ao carregar dados de Personagem e junções. Erro: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return True

def load_rivalidade_data(csv_filepath):
    """Loads Rivalidade data from its dedicated CSV."""
    print(f"\n--- Carregando '{csv_filepath}' para a tabela Rivalidade ---")
    conn = None
    cur = None
    try:
        if not os.path.exists(csv_filepath):
            print(f"Erro: Arquivo CSV '{csv_filepath}' não encontrado. Pulando Rivalidade.")
            return False

        df = pd.read_csv(csv_filepath)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id_personagem, nome FROM Personagem;")
        personagem_map = {row[1]: row[0] for row in cur.fetchall()}

        for index, row in df.iterrows():
            personagem1_nome = row.get('Personagem 1')
            personagem2_nome = row.get('Personagem 2')
            motivo = row.get('Motivo') if pd.notna(row.get('Motivo')) else None
            status = row.get('Status') if pd.notna(row.get('Status')) else None
            vitorias_p1 = int(row.get('Vitórias Personagem 1')) if pd.notna(row.get('Vitórias Personagem 1')) else 0
            vitorias_p2 = int(row.get('Vitórias Personagem 2')) if pd.notna(row.get('Vitórias Personagem 2')) else 0

            p1_id = personagem_map.get(personagem1_nome)
            p2_id = personagem_map.get(personagem2_nome)

            if p1_id and p2_id:
                # Prevent self-rivalry and ensure unique (p1, p2) or (p2, p1)
                if p1_id == p2_id:
                    print(f"  Aviso: Rivalidade para o mesmo personagem '{personagem1_nome}' ignorada.")
                    continue
                cur.execute(
                    "SELECT COUNT(*) FROM Rivalidade WHERE (id_personagem1 = %s AND id_personagem2 = %s) OR (id_personagem1 = %s AND id_personagem2 = %s);",
                    (p1_id, p2_id, p2_id, p1_id)
                )
                if cur.fetchone()[0] == 0: # If rivalry doesn't exist
                    try:
                        cur.execute(
                            "INSERT INTO Rivalidade (id_personagem1, id_personagem2, motivo, status, num_vitorias) VALUES (%s, %s, %s, %s, %s);",
                            (p1_id, p2_id, motivo, status, vitorias_p1 + vitorias_p2) # Assuming num_vitorias is total wins for the rivalry
                        )
                    except Exception as e:
                        print(f"    Aviso: Falha ao inserir Rivalidade para {personagem1_nome} vs {personagem2_nome}. Erro: {e}")
            else:
                print(f"  Aviso: Personagem não encontrado para rivalidade: {personagem1_nome} ou {personagem2_nome}. Pulando linha.")
        conn.commit()
        print(f"Sucesso: Dados da tabela Rivalidade carregados.")
        return True
except Exception as e:

        print(f"Falha ao carregar dados de Rivalidade. Erro: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def load_torneio_personagem_data(csv_filepath):
    """Loads Torneio_Personagem data from its dedicated CSV."""
    print(f"\n--- Carregando '{csv_filepath}' para a tabela Torneio_Personagem ---")
    conn = None
    cur = None
    try:
        if not os.path.exists(csv_filepath):
            print(f"Erro: Arquivo CSV '{csv_filepath}' não encontrado. Pulando Torneio_Personagem.")
            return False

        df = pd.read_csv(csv_filepath)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id_personagem, nome FROM Personagem;")
        personagem_map = {row[1]: row[0] for row in cur.fetchall()}

        cur.execute("SELECT id_torneio, nome FROM Torneio;")
        torneio_map = {row[1]: row[0] for row in cur.fetchall()}

        for index, row in df.iterrows():
            personagem_nome = row.get('Nome Personagem')
            torneio_nome = row.get('Nome Torneio')
            posicao_final = row.get('Posição Final') if pd.notna(row.get('Posição Final')) else None

            p_id = personagem_map.get(personagem_nome)
            t_id = torneio_map.get(torneio_nome)

            if p_id and t_id:
                try:
                    cur.execute(
                        "INSERT INTO Torneio_Personagem (id_torneio, id_personagem, posicao_final) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;",
                        (t_id, p_id, posicao_final)
                    )
                except Exception as e:
                    print(f"    Aviso: Falha ao inserir Torneio_Personagem para {personagem_nome}-{torneio_nome}. Erro: {e}")
            else:
                print(f"  Aviso: Personagem ou Torneio não encontrado para participação: {personagem_nome} ou {torneio_nome}. Pulando linha.")
        conn.commit()
        print(f"Sucesso: Dados da tabela Torneio_Personagem carregados.")
        return True

    except Exception as e:
        print(f"Falha ao carregar dados de Torneio_Personagem. Erro: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

# --- Main Execution Block ---
if __name__ == "__main__":
    # --- Grupo 1: Tabelas Independentes ---
    # Colunas no CSV (keys) -> Colunas no Banco (values)
    load_simple_csv_to_db(
        'cla - Página1.csv', 'Cla',
        column_mapping={'id_cla': 'id_cla', 'nome': 'nome', 'regiao': 'regiao', 'lider': 'lider', 'simbolo': 'simbolo', 'fundacao': 'fundacao', 'alinhamento': 'alinhamento'},
        date_columns=['fundacao']
    )
    load_simple_csv_to_db(
        'jogo - Página1.csv', 'Jogo',
        column_mapping={'id_jogo': 'id_jogo', 'titulo': 'titulo', 'ano_lancamento': 'ano_lancamento', 'plataforma': 'plataforma'}
    )
    load_simple_csv_to_db(
        'habilidade - Página1.csv', 'Habilidade',
        column_mapping={'id_habilidade': 'id_habilidade', 'nome': 'nome', 'tipo': 'tipo', 'categoria': 'categoria', 'elemento': 'elemento'}
    )
    load_simple_csv_to_db(
        'arma - Página1.csv', 'Arma', # Corrected filename
        column_mapping={'id_arma': 'id_arma', 'nome': 'nome', 'tipo': 'tipo', 'raridade': 'raridade', 'alcance': 'alcance', 'dano': 'dano'}
    )
    load_simple_csv_to_db(
        'torneio - Página1.csv', 'Torneio',
        column_mapping={'id_torneio': 'id_torneio', 'nome': 'nome', 'ano': 'ano', 'status': 'status_torneio', 'organizador': 'organizador'}
    )

    # --- Se você tiver CSVs para Mundo e Transformacao, adicione-os aqui ---
    # Exemplo:
    # load_simple_csv_to_db('mundo.csv', 'Mundo', column_mapping={'id_mundo': 'id_mundo', ...})
    # load_simple_csv_to_db('transformacao.csv', 'Transformacao', column_mapping={'id_transformacao': 'id_transformacao', ...})
    # É CRÍTICO que Mundo e Transformacao sejam carregados antes de Personagem se Personagem os referencia.

    # --- Grupo 2: Tabela Personagem (depende de Cla, Mundo, Arma, Transformacao) ---
    load_personagem_and_junction_data('personagem - Página1.csv')

    # --- Grupo 3: Tabelas de Junção que podem ter CSVs dedicados ---
    # Se 'rivalidade - Página1.csv' for a fonte principal de rivalidades
    load_rivalidade_data('rivalidade - Página1.csv')

    # Se 'personagem_torneio - Página1.csv' for a fonte principal de participações em torneios
    load_torneio_personagem_data('personagem_torneio - Página1.csv')

    print("\n--- Processo de carregamento de dados finalizado. Verifique o console para avisos/erros. ---")
