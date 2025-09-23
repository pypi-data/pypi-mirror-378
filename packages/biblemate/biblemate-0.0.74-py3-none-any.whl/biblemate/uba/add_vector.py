import apsw, re, os, json
from agentmake.utils.rag import get_embeddings
from prompt_toolkit.shortcuts import ProgressBar
from biblemate import config


def add_vector_dictionaries():
    db_file = os.path.join(os.path.expanduser("~"), "UniqueBible", "marvelData", "data", "dictionary.data")
    if os.path.isfile(db_file):
        with apsw.Connection(db_file) as connection:
            cursor = connection.cursor()
            # Check if 'entry' column already exists
            cursor.execute("PRAGMA table_info(Dictionary);")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            if 'entry' not in column_names:
                cursor.execute("ALTER TABLE Dictionary ADD COLUMN entry TEXT;")
                cursor.execute("ALTER TABLE Dictionary ADD COLUMN entry_vector TEXT;")
            # Update 'entry' and 'entry_vector' columns
            cursor.execute("SELECT path, content FROM Dictionary;")
            with ProgressBar() as pb:
                for path, content in pb(cursor.fetchall()):
                    search = re.search(">([^<>]+?)</ref>", content)
                    if search:
                        entry = search.group(1)
                        vector = get_embeddings([entry], config.embedding_model)
                        vector_str = json.dumps(vector.tolist())
                        cursor.execute("UPDATE Dictionary SET entry = ?, entry_vector = ? WHERE path = ?;", (entry, vector_str, path))

def add_vector_encyclopedias():
    db_file = os.path.join(os.path.expanduser("~"), "UniqueBible", "marvelData", "data", "encyclopedia.data")
    if os.path.isfile(db_file):
        with apsw.Connection(db_file) as connection:
            for table in ("DAC", "DCG", "HAS", "ISB", "KIT", "MSC"):
                print(f"Working on table `{table}` ...")
                cursor = connection.cursor()
                # Check if 'entry' column already exists
                cursor.execute(f"PRAGMA table_info({table});")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                if 'entry' not in column_names:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN entry TEXT;")
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN entry_vector TEXT;")
                # Update 'entry' and 'entry_vector' columns
                cursor.execute(f"SELECT path, content FROM {table};")
                with ProgressBar() as pb:
                    for path, content in pb(cursor.fetchall()):
                        search = re.search(">([^<>]+?)</ref>", content)
                        if search:
                            entry = search.group(1)
                            vector = get_embeddings([entry], config.embedding_model)
                            vector_str = json.dumps(vector.tolist())
                            cursor.execute(f"UPDATE {table} SET entry = ?, entry_vector = ? WHERE path = ?;", (entry, vector_str, path))