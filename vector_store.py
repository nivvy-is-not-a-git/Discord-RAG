import buffer
from typing import Any
from pgvector.psycopg import register_vector

def add_chunks(formatted_chunks: list[str], chunk_embeddings: Any, message_ids: list[list[str]]) -> None:
    print(f"inserting {len(formatted_chunks)} chunks into db")
    con =  buffer.get_conn()
    cur = con.cursor()
    register_vector(con)
    data = []
    for content, embedding, ids in zip(formatted_chunks, chunk_embeddings, message_ids):
        data.append((content, embedding, ids))
    cur.executemany("""
        INSERT INTO chunks (chunk_text, embedding, message_ids) VALUES (%s, %s, %s)
    """, data)
    con.commit()
    con.close()



     


