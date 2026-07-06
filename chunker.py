import chunkerhelper as ch
import buffer, vector_store
import typing
from sentence_transformers import SentenceTransformer


def _merge_into_chunk(existing: dict, new_messages: list[dict], new_ids: list[str]) -> None:
    addition = ch.format_chunks([new_messages])[0]
    combined_text = existing['chunk_text'] + "\n" + addition
    combined_ids = existing['message_ids'] + new_ids
    new_embedding = ch.model.encode(combined_text, normalize_embeddings=True)
    vector_store.update_chunk(existing['id'], combined_text, new_embedding, combined_ids)


def semantic_chunk() -> list[str]:

    print("fetching unprocessed messages")
    thread_messages = buffer.get_unprocessed_thread_messages()
    reply_messages = buffer.get_unprocessed_reply_messages()
    orphan_messages = buffer.get_unprocessed_orphans()
    print(f"found {len(thread_messages)} thread, {len(reply_messages)} reply, {len(orphan_messages)} orphan messages")

    new_chunks_messages = []
    new_chunks_ids = []
    handled_message_ids = []

    for chunk in ch.chunk_by_thread(thread_messages):
        thread_id = chunk[0]['thread_id']
        ids = [m['message_id'] for m in chunk]
        anchor = buffer.get_last_processed_thread_message(thread_id)
        existing = vector_store.find_chunk_by_message_id(anchor['message_id']) if anchor else None
        if existing:
            _merge_into_chunk(existing, chunk, ids)
        else:
            new_chunks_messages.append(chunk)
            new_chunks_ids.append(ids)
        handled_message_ids.extend(ids)

    for chunk in ch.chunk_by_reply(reply_messages):
        parent_id = chunk[-1]['reply_to']
        ids = [m['message_id'] for m in chunk]
        existing = vector_store.find_chunk_by_message_id(parent_id) if parent_id else None
        if existing:
            _merge_into_chunk(existing, chunk, ids)
        else:
            new_chunks_messages.append(chunk)
            new_chunks_ids.append(ids)
        handled_message_ids.extend(ids)

    if orphan_messages:
        orphan_chunks = ch.chunk_orphan_messages(orphan_messages)
        anchor_msg = buffer.get_last_processed_orphan_message()
        if anchor_msg:
            existing = vector_store.find_chunk_by_message_id(anchor_msg['message_id'])
            if existing:
                anchor_emb = ch.model.encode(anchor_msg['content'])
                first_emb = ch.model.encode(orphan_chunks[0][0]['content'])
                score = ch.model.similarity(anchor_emb, first_emb)
                if score >= 0.6:
                    first_chunk = orphan_chunks.pop(0)
                    ids = [m['message_id'] for m in first_chunk]
                    _merge_into_chunk(existing, first_chunk, ids)
                    handled_message_ids.extend(ids)
        for chunk in orphan_chunks:
            ids = [m['message_id'] for m in chunk]
            new_chunks_messages.append(chunk)
            new_chunks_ids.append(ids)
            handled_message_ids.extend(ids)

    if new_chunks_messages:
        formatted_chunks = ch.format_chunks(new_chunks_messages)
        print(f"encoding {len(formatted_chunks)} new chunks")
        chunk_embeddings = ch.model.encode(formatted_chunks, batch_size=15, normalize_embeddings=True)
        print("storing new chunks in vector store")
        vector_store.add_chunks(formatted_chunks, chunk_embeddings, new_chunks_ids)

    return handled_message_ids
