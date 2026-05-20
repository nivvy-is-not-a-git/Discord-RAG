import buffer


def chunk_by_thread(messages):
    chunks = []
    current_chunk_id = None
    current_chunk = []
    
    for message in messages:
        if message['thread_id'] == current_chunk_id:
            current_chunk.append(message)
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk_id = message['thread_id']
            current_chunk = [message]
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


chunk_by_thread(buffer.get_unprocessed_thread_messages())


