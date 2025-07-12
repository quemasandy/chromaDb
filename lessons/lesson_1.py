import chromadb

# Usar modo persistente para que puedas ver los archivos en ./chroma_db
client = chromadb.PersistentClient(path="./chroma_db")

# Crear la colección (si no existe)
collection = client.get_or_create_collection("my_collection")

# Definir los documentos
documents = [
    {"id": "doc1", "text": "Hello, world!"},
    {"id": "doc2", "text": "How are you today?"},
    {"id": "doc3", "text": "Goodbye, see you later!"},
]

# Guardar los documentos en ChromaDB
collection.upsert(
    ids=[doc["id"] for doc in documents],
    documents=[doc["text"] for doc in documents]
)

print("\n¡Documentos guardados en ChromaDB!")

# Consultar por ID
result = collection.get(ids=["doc1"])
print("\nConsulta por ID:")
print(result)

# Buscar por texto
query_result = collection.query(query_texts=["Hello"], n_results=1)
print("\nBúsqueda por texto:")
print(query_result)

