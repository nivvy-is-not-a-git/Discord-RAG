import buffer
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def vsearch(query_string: str, threshold: float = 0.45) -> list[tuple[str, list[str]]]:
    print(f"searching for: {query_string}")
    con = buffer.get_conn()
    register_vector(con)

    query_embedding = model.encode(query_string)
    rows = con.execute("""
        SELECT chunk_text, message_ids
        FROM chunks
        WHERE -(embedding <#> %s) >= %s
        ORDER BY embedding <#> %s LIMIT 5
        """, (query_embedding, threshold, query_embedding)).fetchall()
    con.close()
    return rows
