import buffer
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def vector_search(query_string: str) -> list[tuple[str, list[str]]]:
    con = buffer.get_conn()
    register_vector(con)

    query_embedding = model.encode(query_string)
    rows = con.execute("""
        SELECT chunk_text, message_ids
        FROM chunks
        ORDER BY embedding <#> %s LIMIT 5
        """, (query_embedding,)).fetchall()
    con.close()
    return rows
