import sqlite3

DB_PATH = "buffer.db"

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        message_id      TEXT PRIMARY KEY,
        author          TEXT NOT NULL,
        content         TEXT,
        channel         TEXT NOT NULL,
        timestamp       TEXT NOT NULL,
        discord_link    TEXT NOT NULL,
        reply_to        TEXT,
        thread_id       TEXT,
        thread_name     TEXT,
        is_processed    INTEGER DEFAULT 0)
""")
    
    con.commit()
    con.close()

   
def store_message(message, thread_id = None, thread_name = None):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    content=message.clean_content

    reply_to = str(message.reference.message_id) if message.reference else None

    for attachment in message.attachments: #since cdn urls have 24 hr expiry due to discord policy, raw attachments will not be ingested
        if attachment.content_type and attachment.content_type.startswith("image/"):
            content += " [image attached]"
        elif attachment.content_type and attachment.content_type.startswith("video/"):
            content += " [video attached]"
        elif attachment.content_type and attachment.content_type.startswith("audio/"):
            content += " [audio attached]"
        else:
            content += " [file attached]"
    
        
    cur.execute("""
        INSERT OR IGNORE INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (str(message.id), message.author.display_name, content, message.channel.name, message.created_at.isoformat(), message.jump_url, reply_to, str(thread_id) if thread_id else None, thread_name, 0))
    con.commit()
    con.close()




def get_unprocessed():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute(f"""
    SELECT * FROM messages 
    WHERE is_processed IS 0
""")
    
    rows = cur.fetchall()  


    con.close()
    return [dict(row) for row in rows]


def mark_processed(message_ids):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    placeholders = ",".join(["?" for _ in message_ids]) #promoting safe parameterization , dynamic placeholders for list of message_ids


    cur.execute(f"""
        UPDATE messages
        SET is_processed = 1
        WHERE message_id IN ({placeholders})
""", message_ids)
    con.commit()
    con.close()




def get_last_message_id(channel_name):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    cur.execute("""
        SELECT message_id FROM messages 
        WHERE channel = ? 
        ORDER BY timestamp DESC 
        LIMIT 1
    """, (channel_name,))
    
    row = cur.fetchone()
    con.close()
    
    return int(row["message_id"]) if row else None

def get_unprocessed_thread_messages():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    cur.execute("""
        SELECT * FROM messages 
        WHERE is_processed = 0 and thread_id IS NOT NULL
        ORDER BY thread_id, timestamp ASC 
    """)
    
    rows = cur.fetchall()

    con.close()

    return [dict(row) for row in rows]    
