# Importamos la librería principal de ChromaDB para crear y gestionar bases de datos vectoriales
import chromadb
# Importamos el módulo os para acceder a variables de entorno del sistema operativo
import os
# Importamos load_dotenv para cargar variables de entorno desde archivo .env
from dotenv import load_dotenv

# Importamos las funciones de embedding predefinidas de ChromaDB
from chromadb.utils import embedding_functions

# Cargamos las variables de entorno desde el archivo .env al entorno de ejecución
load_dotenv()

# Obtenemos la API key de OpenAI desde las variables de entorno para autenticación
openai_api_key = os.getenv("OPENAI_API_KEY")

# Creamos una función de embedding específica de OpenAI que usará su API
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai_api_key,  # Pasamos la API key para autenticación
    model_name="text-embedding-3-small"  # Especificamos el modelo de embedding a usar
)
# Creamos un cliente persistente de ChromaDB que guardará los datos en disco
croma_client = chromadb.PersistentClient(path="./db/chroma_persist")

# Creamos o obtenemos una colección existente llamada "my_story" con la función de embedding de OpenAI
collection = croma_client.get_or_create_collection(
    "my_story",  # Nombre de la colección donde se almacenarán los documentos
    embedding_function=openai_ef,  # Especificamos que use la función de embedding de OpenAI
)

# Definimos una lista de documentos de texto con sus IDs únicos
documents = [
    {"id": "doc1", "text": "Hello, world!"},  # Documento simple de saludo
    {"id": "doc2", "text": "How are you today?"},  # Documento de pregunta
    {"id": "doc3", "text": "Goodbye, see you later!"},  # Documento de despedida
    {
        "id": "doc4",
        "text": "Microsoft is a technology company that develops software. It was founded by Bill Gates and Paul Allen in 1975.",  # Documento sobre Microsoft
    },
    {
        "id": "doc5",
        "text": "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think like humans and mimic their actions.",  # Documento sobre IA
    },
    {
        "id": "doc6",
        "text": "Machine Learning (ML) is a subset of AI that focuses on the development of algorithms that allow computers to learn from and make predictions based on data.",  # Documento sobre ML
    },
    {
        "id": "doc7",
        "text": "Deep Learning is a subset of Machine Learning that uses neural networks with many layers to analyze various factors of data.",  # Documento sobre Deep Learning
    },
    {
        "id": "doc8",
        "text": "Natural Language Processing (NLP) is a branch of AI that helps computers understand, interpret, and respond to human language.",  # Documento sobre NLP
    },
    {
        "id": "doc9",
        "text": "AI can be categorized into two types: Narrow AI, which is designed to perform a narrow task, and General AI, which can perform any intellectual task that a human can do.",  # Documento sobre tipos de IA
    },
    {
        "id": "doc10",
        "text": "Computer Vision is a field of AI that enables computers to interpret and make decisions based on visual data from the world.",  # Documento sobre Computer Vision
    },
    {
        "id": "doc11",
        "text": "Reinforcement Learning is an area of Machine Learning where an agent learns to make decisions by taking actions in an environment to achieve maximum cumulative reward.",  # Documento sobre Reinforcement Learning
    },
    {
        "id": "doc12",
        "text": "The Turing Test, proposed by Alan Turing, is a measure of a machine's ability to exhibit intelligent behavior equivalent to, or indistinguishable from, that of a human.",  # Documento sobre Turing Test
    },
]

# Iteramos sobre cada documento en la lista para insertarlo en la colección
for doc in documents:
    # Usamos upsert para insertar o actualizar el documento en la colección
    # upsert significa "update or insert" - si el ID existe, actualiza; si no, inserta
    collection.upsert(ids=doc["id"], documents=[doc["text"]])

# Definimos el texto de consulta que queremos buscar en la base de datos
query_text = "find document related to python"

# Realizamos la consulta semántica en la colección
results = collection.query(
    query_texts=[query_text],  # Lista de textos de consulta (en este caso solo uno)
    n_results=3,  # Número máximo de resultados a retornar
)

# Iteramos sobre los resultados encontrados para mostrarlos
for idx, document in enumerate(results["documents"][0]):  # results["documents"][0] contiene la lista de documentos del primer query
    doc_id = results["ids"][0][idx]  # Obtenemos el ID del documento actual
    distance = results["distances"][0][idx]  # Obtenemos la distancia de similitud (menor = más similar)

    # Imprimimos la información del resultado encontrado
    print(
        f"\nFor the query: {query_text}, \n Found similar document: {document} (ID: {doc_id}, Distance: {distance})\n"
    )
