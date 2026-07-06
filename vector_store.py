from __future__ import annotations
import buffer
from typing import Any
from pgvector.psycopg import register_vector
from psycopg.rows import dict_row

def add_chunks(formatted_chunks: list[str], chunk_embeddings: Any, message_ids: list[list[str]]) -> None:
    print(f"inserting {len(formatted_chunks)} chunks into db")
    con = buffer.get_conn()
    register_vector(con)
    cur = con.cursor()
    data = []
    for content, embedding, ids in zip(formatted_chunks, chunk_embeddings, message_ids):
        data.append((content, embedding, ids))
    cur.executemany("""
        INSERT INTO chunks (chunk_text, embedding, message_ids) VALUES (%s, %s, %s)
    """, data)
    con.commit()
    con.close()


def find_chunk_by_message_id(message_id: str) -> dict[str, Any] | None:
    con = buffer.get_conn()
    row = con.cursor(row_factory=dict_row).execute("""
        SELECT id, chunk_text, message_ids
        FROM chunks
        WHERE message_ids @> ARRAY[%s]
        LIMIT 1
    """, (message_id,)).fetchone()
    con.close()
    return row


def update_chunk(chunk_id: int, chunk_text: str, embedding: Any, message_ids: list[str]) -> None:
    print(f"merging into existing chunk {chunk_id}, now {len(message_ids)} messages")
    con = buffer.get_conn()
    register_vector(con)
    cur = con.cursor()
    cur.execute("""
        UPDATE chunks
        SET chunk_text = %s, embedding = %s, message_ids = %s
        WHERE id = %s
    """, (chunk_text, embedding, message_ids, chunk_id))
    con.commit()
    con.close()
