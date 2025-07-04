import chromadb
from documents_data import documents

# Usar modo persistente para que puedas ver los archivos en ./chroma_db
client = chromadb.PersistentClient(path="./chroma_db")

# Crear la colección (si no existe)
movie_collection = client.get_or_create_collection("movies")

# Guardar los documentos en ChromaDB
movie_collection.upsert(
    ids=[doc["id"] for doc in documents],
    documents=[doc["text"] for doc in documents]
)

print("\n¡Documentos guardados en ChromaDB!")

# Consultar por ID
result = movie_collection.get(ids=["doc1"])
print("\nConsulta por ID:")
print(result)

# Buscar por texto
query_text = "some gladiator movie" 
query_result = movie_collection.query(query_texts=[query_text], n_results=3)
print("\nBúsqueda por texto:")
print(query_result)


docs = query_result.get("documents")
ids = query_result.get("ids")
distances = query_result.get("distances")

if docs and docs[0] and ids and ids[0] and distances and distances[0]:
    print("\nenumerate(docs[0])", enumerate(docs[0]))
    for idx, document in enumerate(docs[0]):
        doc_id = ids[0][idx]
        distance = distances[0][idx]
        print(
            f"\nPara la consulta: '{query_text}',\n"
            f"Documento similar encontrado:\n"
            f"  ID: {doc_id}\n"
            f"  Texto: {document}\n"
            f"  Distancia semántica: {distance}\n"
        )
else:
    print("\nNo se encontraron resultados válidos para la consulta.")