import chunkerhelper as ch
import buffer, vector_store
import typing
from sentence_transformers import SentenceTransformer


def semantic_chunk() -> list[str]:
    
    semantic_chunks = []
    message_ids = []
    thread_messages = buffer.get_unprocessed_thread_messages()
    reply_messages = buffer.get_unprocessed_reply_messages()
    orphan_messages = buffer.get_unprocessed_orphans()

    semantic_chunks.extend(ch.chunk_by_reply(reply_messages))
    semantic_chunks.extend(ch.chunk_by_thread(thread_messages))
    semantic_chunks.extend(ch.chunk_orphan_messages(orphan_messages))
    
    for chunk in semantic_chunks:
        m = []
        for message in chunk:
            m.append(message['message_id'])
        message_ids.append(m)

    formatted_chunks = ch.format_chunks(semantic_chunks)  #groups all messages in a chunk into one string separated by newline and author

    chunk_embeddings = ch.model.encode(formatted_chunks, batch_size = 15, normalize_embeddings = True) #normalizing embeddings before storage to reduce normalization computation later on in retrieval
    vector_store.add_chunks(formatted_chunks, chunk_embeddings, message_ids)
    

    return [message for chunk in message_ids for message in chunk]

    




    


