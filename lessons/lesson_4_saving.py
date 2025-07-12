import chromadb

# Crear cliente persistente y colección
croma_client = chromadb.PersistentClient(path="./db/chroma_persist")
collection = croma_client.get_or_create_collection("my_story")

# Datos de ejemplo para insertar
documents = [
    {"id": "doc1", "text": "Hello, world!"},  
    {"id": "doc2", "text": "How are you today?"},  
    {"id": "doc3", "text": "Goodbye, see you later!"},  
    {"id": "doc4", "text": "Microsoft is a technology company that develops software. It was founded by Bill Gates and Paul Allen in 1975."},  
]

# Insertar documentos en la colección
for doc in documents:  
    collection.upsert(ids=doc["id"], documents=[doc["text"]])  

# Realizar múltiples queries
query_texts = [
    "find document related to technology company",
    "Hello",
]
results = collection.query(query_texts=query_texts, n_results=2)

def process_query_results(results, query_texts):
    """Procesa los resultados de múltiples queries de ChromaDB de forma segura."""
    # Procesa cada query y sus resultados
    for idx_query, query_text in enumerate(query_texts):
        # Obtiene los resultados para esta query específica
        docs = results.get("documents", [])
        ids = results.get("ids", [])
        distances = results.get("distances", [])
        
        # Verifica que esta query tenga resultados válidos
        if (idx_query >= len(docs) or idx_query >= len(ids) or idx_query >= len(distances) or
            not docs[idx_query] or not ids[idx_query] or not distances[idx_query]):
            print(f"No se encontraron documentos similares para la consulta: {query_text}")
            continue
        
        # Imprime cada documento encontrado
        query_docs, query_ids, query_distances = docs[idx_query], ids[idx_query], distances[idx_query]
        for doc_idx, (document, doc_id, distance) in enumerate(zip(query_docs, query_ids, query_distances)):
            print(f"Query: {query_text}")
            print(f"  Documento #{doc_idx + 1}: {document}")
            print(f"  ID: {doc_id}, Distancia: {distance:.4f}")
            print("-" * 50)

# Procesar resultados
process_query_results(results, query_texts)
