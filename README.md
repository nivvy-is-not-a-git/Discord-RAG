# Discord RAG

Turn a Discord server's message history into a searchable knowledge base — ask a question with `/ask` and get an answer sourced from your community's own conversations, with a link back to the original message.

![demo](docs/images/demo-ask.gif)

## What it does

Most Discord knowledge lives in scattered threads, replies, and channels that nobody can search. This bot ingests a server's message history, groups related messages (threads, reply chains, and topically-similar standalone messages) into semantic chunks, embeds them, and stores them in a vector database. A `/ask` slash command then does similarity search over that history and replies with the most relevant passage — plus a jump link to the original Discord message. The bot is accessed either on the web or on Discord as a bot integration. 
<img width="644" height="66" alt="Screenshot 2026-07-21 at 5 40 10 PM" src="https://github.com/user-attachments/assets/903b02b8-1aed-442c-b8b3-c20fd7d906bf" />
<img width="639" height="169" alt="Screenshot 2026-07-21 at 5 40 16 PM" src="https://github.com/user-attachments/assets/f044dd73-381b-42c8-8d90-5f537da2bdb0" />
<img width="642" height="366" alt="Screenshot 2026-07-21 at 5 40 23 PM" src="https://github.com/user-attachments/assets/b1ed66fb-42c6-4e92-adf1-84a697ac554d" />


## Features

- **Full history ingestion** — walks channel history, active threads, and archived threads on startup, resuming from the last-seen message on restart
- **Semantic chunking** — groups messages by thread, by reply chain, or by embedding similarity for standalone messages, and merges new messages into existing chunks instead of duplicating them
- **Live ingestion loop** — polls for new pending messages every 30s and folds them into the vector store automatically
- **`/ask` slash command** — semantic search over the whole server's history via pgvector cosine/inner-product distance, returned with a source link
- **Thread & reply aware** — understands Discord's conversational structure instead of treating messages as a flat list



## How it works

```mermaid
flowchart LR
    A[Discord Messages] --> B[Postgres buffer<br/>raw messages]
    B --> C[Semantic Chunker<br/>thread / reply / orphan grouping]
    C --> D[MiniLM Embeddings]
    D --> E[(Supabase pgvector<br/>chunks table)]
    F["/ask query"] --> G[Embed query]
    G --> E
    E --> H[Top-k matches]
    H --> I[Discord reply<br/>+ source link]

```
Ingest — on startup, the bot scrapes a channel's full history (including threads) into a raw Postgres messages table
Chunk — chunker.py groups unprocessed messages by thread/reply/topic and merges them into existing chunks where they extend a prior conversation
Embed & store — chunks are encoded with sentence-transformers/all-MiniLM-L6-v2 and stored in Supabase via pgvector
Query — a question embeds and runs a similarity search over the chunks table, returning the closest matches with a link back to the source message

## Tech Stack
<img width="384" height="180" alt="Screenshot 2026-07-21 at 5 43 13 PM" src="https://github.com/user-attachments/assets/d58ce78d-8fb9-4850-af58-fcca9cd408ff" />

## Project Structure
bot.py             # Discord client, on_ready ingest, /ask command
api.py             # FastAPI backend for the web frontend
frontend/          # React + Vite web UI
ingest.py          # history scraping + pending-message processing loop
buffer.py          # raw message storage (Postgres)
chunker.py         # semantic chunking / merging logic
chunkerhelper.py   # chunk formatting + embedding model
vector_store.py    # pgvector inserts/updates
vector_search.py   # /ask similarity search

