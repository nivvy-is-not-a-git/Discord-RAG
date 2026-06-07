from __future__ import annotations
import discord
import os
from typing import Any
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()


def get_conn():
    return psycopg.connect(os.getenv("DATABASE_URL"))


def init_db() -> None:
    # messages table schema (created in Supabase dashboard):
    # message_id   text primary key
    # author       text not null
    # content      text
    # channel      text not null
    # timestamp    text not null
    # discord_link text not null
    # reply_to     text
    # thread_id    text
    # thread_name  text
    # is_processed integer default 0
    pass


def store_message(message: discord.Message, thread_id: str | None = None, thread_name: str | None = None) -> None:
    content = message.clean_content

    reply_to = str(message.reference.message_id) if message.reference else None

    for attachment in message.attachments:  # since cdn urls have 24 hr expiry due to discord policy, raw attachments will not be ingested
        if attachment.content_type and attachment.content_type.startswith("image/"):
            content += " [image attached]"
        elif attachment.content_type and attachment.content_type.startswith("video/"):
            content += " [video attached]"
        elif attachment.content_type and attachment.content_type.startswith("audio/"):
            content += " [audio attached]"
        else:
            content += " [file attached]"

    con = get_conn()
    con.execute("""
        INSERT INTO messages VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (message_id) DO NOTHING
    """, (str(message.id), message.author.display_name, content, message.channel.name,
          message.created_at, message.jump_url, reply_to,
          str(thread_id) if thread_id else None, thread_name, 0))
    con.commit()
    con.close()


def get_unprocessed() -> list[dict[str, Any]]:
    con = get_conn()
    rows = con.cursor(row_factory=dict_row).execute("SELECT * FROM messages WHERE is_processed = 0").fetchall()
    con.close()
    return rows


def mark_processed(message_ids: list[str]) -> None:
    con = get_conn()
    con.execute("""
        UPDATE messages SET is_processed = 1
        WHERE message_id = ANY(%s)
    """, (message_ids,))
    con.commit()
    con.close()


def get_last_message_id(channel_name: str) -> int | None:
    con = get_conn()
    row = con.cursor(row_factory=dict_row).execute("""
        SELECT message_id FROM messages
        WHERE channel = %s
        ORDER BY timestamp DESC
        LIMIT 1
    """, (channel_name,)).fetchone()
    con.close()
    return int(row["message_id"]) if row else None


def get_unprocessed_thread_messages() -> list[dict[str, Any]]:
    con = get_conn()
    rows = con.cursor(row_factory=dict_row).execute("""
        SELECT * FROM messages
        WHERE is_processed = 0 AND thread_id IS NOT NULL
        ORDER BY thread_id, timestamp ASC
    """).fetchall()
    con.close()
    return rows


def get_unprocessed_reply_messages() -> list[dict[str, Any]]:
    con = get_conn()
    rows = con.cursor(row_factory=dict_row).execute("""
        SELECT * FROM messages
        WHERE is_processed = 0 AND reply_to IS NOT NULL
        ORDER BY reply_to
    """).fetchall()
    con.close()
    return rows


def get_unprocessed_orphans() -> list[dict[str, Any]]:
    con = get_conn()
    rows = con.cursor(row_factory=dict_row).execute("""
        SELECT * FROM messages
        WHERE is_processed = 0 AND reply_to IS NULL AND thread_id IS NULL
        ORDER BY timestamp DESC
    """).fetchall()
    con.close()
    return rows
