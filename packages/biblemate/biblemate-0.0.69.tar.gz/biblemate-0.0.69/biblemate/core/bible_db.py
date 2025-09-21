import numpy as np
import sqlite3, apsw
import json, os, re, requests
from agentmake.utils.online import get_local_ip
from agentmake import OllamaAI, AGENTMAKE_USER_DIR, agentmake, getDictionaryOutput
from agentmake.utils.rag import get_embeddings, cosine_similarity_matrix
from prompt_toolkit.shortcuts import ProgressBar
from biblemate import config, OLLAMA_NOT_FOUND
from agentmake.plugins.uba.lib.BibleBooks import BibleBooks


# api
def run_uba_api(command: str) -> str:
    UBA_API_LOCAL_PORT = int(os.getenv("UBA_API_LOCAL_PORT")) if os.getenv("UBA_API_LOCAL_PORT") else 8080
    UBA_API_ENDPOINT = os.getenv("UBA_API_ENDPOINT") if os.getenv("UBA_API_ENDPOINT") else f"http://{get_local_ip()}:{UBA_API_LOCAL_PORT}/plain" # use dynamic local ip if endpoint is not specified
    UBA_API_TIMEOUT = int(os.getenv("UBA_API_TIMEOUT")) if os.getenv("UBA_API_TIMEOUT") else 10
    UBA_API_PRIVATE_KEY = os.getenv("UBA_API_PRIVATE_KEY") if os.getenv("UBA_API_PRIVATE_KEY") else ""

    endpoint = UBA_API_ENDPOINT
    private = f"private={UBA_API_PRIVATE_KEY}&" if UBA_API_PRIVATE_KEY else ""
    url = f"""{endpoint}?{private}cmd={command}"""
    try:
        response = requests.get(url, timeout=UBA_API_TIMEOUT)
        response.encoding = "utf-8"
        return response.text.strip()
    except Exception as err:
        return f"An error occurred: {err}"

# local
def search_bible(request:str, book:int=0) -> str:
    bible_file = os.path.join(AGENTMAKE_USER_DIR, "biblemate", "data", "bibles", f"{config.default_bible}.bible")
    if os.path.isfile(bible_file):
        # extract the search string
        try:
            schema = {
                "name": "search_bible",
                "description": "search the bible; search string must be given",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_string": {
                            "type": "string",
                            "description": "search string for searching the bible",
                        },
                    },
                    "required": ["search_string"],
                },
            }
            search_string = getDictionaryOutput(request, schema=schema, backend=config.backend)["search_string"]
        except:
            search_string = agentmake(request, system="biblemate/identify_search_string")[-1].get("content", "").strip()
            search_string = re.sub(r"^.*?(```search_string|```)(.+?)```.*?$", r"\2", search_string, flags=re.DOTALL).strip()
        search_string = re.sub('''^['"]*(.+?)['"]*$''', r"\1", search_string).strip()
        # perform the searches
        abbr = BibleBooks.abbrev["eng"]
        db = BibleVectorDatabase(bible_file)
        exact_matches = [f"({abbr[str(b)][0]} {c}:{v}) {content.strip()}" for b, c, v, content in db.search_verses_partial([search_string], book=book)]
        if os.path.getsize(bible_file) > 380000000:
            semantic_matches = [f"({abbr[str(b)][0]} {c}:{v}) {content.strip()}" for b, c, v, content in db.search_meaning(search_string, top_k=config.max_semantic_matches, book=book)]
        else:
            semantic_matches = []
        exact_matches_content = "\n- ".join(exact_matches)
        semantic_matches_content = "\n- ".join(semantic_matches)
        output = f'''# Search for `{search_string}`

## Exact Matches [{len(exact_matches)} verse(s)]

{"- " if exact_matches else ""}{exact_matches_content}

## Semantic Matches [{len(semantic_matches)} verse(s)]

{"- " if semantic_matches else ""}{semantic_matches_content}'''
        if not os.path.getsize(bible_file) > 380000000:
            output += f"[{OLLAMA_NOT_FOUND}]"
        return output
    return ""


class BibleVectorDatabase:
    """
    Sqlite Vector Database via `apsw`
    https://rogerbinns.github.io/apsw/pysqlite.html

    Requirement: Install `Ollama` separately

    ```usage
    from biblemate.core.bible_db import BibleVectorDatabase
    db = BibleVectorDatabase('my_bible.bible') # edit 'my_bible.bible' to your bible file path
    db.add_vectors() # add vectors to the database
    results = db.search_meaning("Jesus love", 10)
    ```
    """

    def __init__(self, uba_bible_path: str=None):
        if not uba_bible_path:
            uba_bible_path = os.path.join(AGENTMAKE_USER_DIR, "biblemate", "data", "bibles", f"{config.default_bible}.bible")
        # check if file exists
        if os.path.isfile(uba_bible_path) and uba_bible_path.endswith(".bible"):
            # Download embedding model
            self.embedding_model = "paraphrase-multilingual"
            OllamaAI.downloadModel(self.embedding_model) # requires installing Ollama
            # init
            self.conn = apsw.Connection(uba_bible_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA auto_vacuum = FULL;")
            self._create_table()

    def __del__(self):
        if not self.conn is None:
            self.conn.close()

    def clean_up(self):
        self.cursor.execute("VACUUM;")
        self.cursor.execute("PRAGMA auto_vacuum = FULL;")

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book INTEGER,
                chapter INTEGER,
                verse INTEGER,
                text TEXT,
                vector TEXT
            )
        """
        )

    def getAllVerses(self):
        query = "SELECT * FROM Verses ORDER BY Book, Chapter, Verse"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def add_vectors(self):
        allVerses = self.getAllVerses()

        with ProgressBar() as pb:
            for book, chapter, verse, scripture in pb(allVerses):
                vector = get_embeddings([scripture], self.embedding_model)
                self.add_vector(book, chapter, verse, scripture, vector)
        self.clean_up()

    def add_vector(self, book, chapter, verse, text, vector):
        vector_str = json.dumps(vector.tolist())
        self.cursor.execute("SELECT COUNT(*) FROM vectors WHERE text = ?", (text,))
        if self.cursor.fetchone()[0] == 0:  # Ensure no duplication
            try:
                self.cursor.execute("INSERT INTO vectors (book, chapter, verse, text, vector) VALUES (?, ?, ?, ?, ?)", (book, chapter, verse, text, vector_str))
            except sqlite3.IntegrityError:
                pass  # Ignore duplicate entries

    def search_vector(self, query_vector, top_k=3, book=0):
        q = "SELECT text, vector FROM vectors"
        if book:
            q += " WHERE book = ?"
            args = (book,)
        else:
            args = ()
        self.cursor.execute(q, args)
        rows = self.cursor.fetchall()
        if not rows:
            return []
        
        texts, vectors = zip(*[(row[0], np.array(json.loads(row[1]))) for row in rows])
        document_matrix = np.vstack(vectors)
        
        similarities = cosine_similarity_matrix(query_vector, document_matrix)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [texts[i] for i in top_indices]

    def search_meaning(self, query, top_k=3, book=0):
        queries = self.search_vector(get_embeddings([query], self.embedding_model)[0], top_k=top_k, book=book)
        return self.search_verses(queries)

    def search_verses(self, queries: list, book: int=0):
        allVerses = []
        for query in queries:
            allVerses += self.search_verse(query, book=book)
        return allVerses

    def search_verses_partial(self, queries: list, book: int=0):
        allVerses = []
        for query in queries:
            allVerses += self.search_verse(query, partial=True, book=book)
        return allVerses

    def search_verse(self, query: str, partial: bool=False, book: int=0):
        book_search = f"Book = {book} AND " if book else ""
        full_match = f'''SELECT * FROM Verses WHERE {book_search}Scripture = ? ORDER BY Book, Chapter, Verse'''
        partial_match = f'''SELECT * FROM Verses WHERE {book_search}Scripture LIKE ? ORDER BY Book, Chapter, Verse'''
        self.cursor.execute(partial_match if partial else full_match, (f"""%{query}%""" if partial else query,))
        return self.cursor.fetchall()