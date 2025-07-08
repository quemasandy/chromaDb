import chromadb  # Importa la librería principal de ChromaDB para interactuar con la base de datos
from chromadb.config import Settings  # Importa la clase Settings para configurar la conexión a ChromaDB
import json  # Importa el módulo json para formatear los resultados de manera legible

# Paso 1: Configuración de ChromaDB
# Define la ruta donde se guardarán los datos de ChromaDB en la raíz del proyecto
# Esto asegura que los datos se almacenen en un directorio específico y accesible
persist_directory = "./chroma_db"  # Directorio donde se guardarán los datos de ChromaDB

# Crea una instancia del cliente de ChromaDB con configuración personalizada
# Settings(persist_directory=...) especifica dónde guardar los datos en disco
# Esto permite persistencia de datos entre ejecuciones del programa
client = chromadb.Client(Settings(persist_directory=persist_directory))

# Paso 2: Crear una colección
# Una colección es un contenedor lógico donde se almacenan los documentos y sus embeddings
# Si la colección ya existe, este método la retorna; si no, la crea
collection = client.get_or_create_collection(name="my_first_collection")

# Paso 3: Insertar documentos simples
# Los documentos pueden ser textos, IDs y metadatos opcionales
# Aquí insertamos tres documentos de ejemplo con IDs únicos
collection.add(
    documents=["Hola mundo", "Aprendiendo ChromaDB", "Buscando información semántica"],  # Lista de textos a almacenar
    ids=["doc1", "doc2", "doc3"]  # IDs únicos para cada documento
)

# Paso 4: Consultar los documentos insertados
# Realizamos una consulta simple usando uno de los textos para buscar los documentos más similares
# El método query retorna los documentos más cercanos semánticamente al texto de consulta
results = collection.query(
    query_texts=["¿Cómo aprender ChromaDB?"],  # Texto de consulta para buscar similitud
    n_results=2  # Número de resultados más similares a retornar
)

# Imprime los resultados de la consulta para ver los documentos recuperados
print("Resultados de la búsqueda:")
print(results)

# Imprime los resultados de la búsqueda con formato JSON indentado para mejor legibilidad
# Esto hace que la salida sea más fácil de leer y analizar
print("Resultados de la búsqueda:")
print(json.dumps(results, indent=2, ensure_ascii=False))  # Formatea los resultados como JSON con indentación de 2 espacios
