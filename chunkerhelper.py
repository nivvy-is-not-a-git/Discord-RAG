from sentence_transformers import SentenceTransformer
from typing import Any


model = SentenceTransformer('all-MiniLM-L6-v2')



def chunk_by_thread(messages:list[dict]) -> list[list[dict[str, Any]]]:
    chunks = []
    current_chunk_id = None
    current_chunk = []
    
    for message in messages:   #O(n) runtime, ordering by thread_id in query ensures no thread messages are skipped
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





def build_chain (msg_lookup:dict[str, Any], current_chunk:list[dict[str, Any]], message:dict[str]) -> None:
    new_message = msg_lookup.pop(message)  #pop message from msg_lookup as it's now visited 
    current_chunk.append(new_message)
    if (new_message['reply_to'] in msg_lookup):   #recursive build_chain call if the current message has a parent message that exists in our message list
        build_chain(msg_lookup, current_chunk, new_message['reply_to'])    
    else:
        return
        

def chunk_by_reply(messages:list[dict[str, Any]])->list[list[dict[str, Any]]]:
    chunks = []
    current_chunk = []
    msg_lookup={}
    for m in messages:
        msg_lookup[m['message_id']] = m
    
    for m in list(msg_lookup.keys()):  #list of keys initially to create the snapshot of keys and avoid Runtime error when list shrinks
        if m in msg_lookup:
            build_chain(msg_lookup, current_chunk, m)
            chunks.append(current_chunk) #append created chunk to list of chunks
            current_chunk = []  #reset for next chain 
    return chunks
                
def chunk_orphan_messages(messages:list[dict[str, Any]])->list[list[dict[str, Any]]]:
    chunks = []
    current_chunk = []
    embeddings = model.encode([message['content'] for message in messages], batch_size = 15)
    threshold = 0.6
    for i in range(len(embeddings)-1):
        current_chunk.append(messages[i])
        score = model.similarity(embeddings[i], embeddings[i+1])
        if score < threshold:
            chunks.append(current_chunk)
            current_chunk = []
    if messages:
        current_chunk.append(messages[-1])
    chunks.append(current_chunk)
    
    return chunks


def format_chunks(chunks: list[dict[str, Any]]) ->list[str]:
    formatted_chunks = []

    for chunk in chunks:
        message_chunk = []
        for message in chunk:
            message_chunk.append(f"[{message['author']}]: { message['content']}")
        formatted_chunks.append("\n".join(message_chunk))
        
    return formatted_chunks