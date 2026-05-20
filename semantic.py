import chromadb

chroma_client=chromadb.Client()

collection = chroma_client.create_collection(name="semantic_discord_chunks")
batch_size=1000
for i in range (0, len(chunks), batch_size):
    batch = chunks[i:i+batch_size] #batching embedded chunks for performance/efficiency reasons
    text_list=[]
    combined_text=[]
    documents, ids, metadatas = [], [], []
    for index, message in enumerate (batch):
        
        author=message['author']
        text=f"{author}: {message['content']}"
        ids.append(f"chunk_{i+j}")
        metadata= {


        }
        text_list.append(text)
    combined_text=" ".join(text_list)
    documents.append(combined_text)
     
    metadata={

    }
    collection.add(
        ids=[i],
        document=documents,
        metadata=metadatas
    )