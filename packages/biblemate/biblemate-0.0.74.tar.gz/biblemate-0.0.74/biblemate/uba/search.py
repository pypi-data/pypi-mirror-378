from biblemate import config
from agentmake.utils.rag import get_embeddings, cosine_similarity_matrix
import os, apsw, json
import numpy as np
from typing import Union

class UBASearches
    
    @staticmethod
    def search_data(db_file: str, sql_table: str, query: str, top_k: int=3) -> Union[list, str]:
        """search `dictionary.db` or `encyclopedia.db` for a query"""
        if not os.path.isfile(db_file):
            return "Invalid database file."
        with apsw.Connection(db_file) as connection:
            cursor = connection.cursor()
            # search for an exact match
            if "|" in query:
                path, query = query.split("|", 1)
                cursor.execute(f"SELECT * FROM {sql_table} WHERE path = ? AND entry = ?;", (path, query))
            else:
                cursor.execute(f"SELECT * FROM {sql_table} WHERE entry = ?;", (query,))
            rows = cursor.fetchall()
            if not rows: # perform similarity search if no an exact match
                # convert query to vector
                query_vector = get_embeddings([query], config.embedding_model)
                # fetch all entries
                cursor.execute(f"SELECT entry, entry_vector FROM {sql_table}")
                cursor.fetchall()
                if not rows:
                    return []
                # build a matrix
                entries, entry_vectors = zip(*[(row[0], np.array(json.loads(row[1]))) for row in rows])
                document_matrix = np.vstack(entry_vectors)
                # perform a similarity search
                similarities = cosine_similarity_matrix(query_vector, document_matrix)
                top_indices = np.argsort(similarities)[::-1][:top_k]
                # return top matches
                return [entries[i] for i in top_indices]
            elif len(rows) == 1: # single exact match
                return rows[0][1] # return content directly if there is an exact match
            else:
                return [f"{path}|{entry}" for path, _, entry, _ in rows]