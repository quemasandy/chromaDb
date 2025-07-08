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

# Paso 3: Insertar documentos con metadatos
# Los metadatos nos permiten categorizar y filtrar los documentos
# Cada documento ahora tiene información adicional que facilita la organización
collection.add(
    documents=["Hola mundo", "Aprendiendo ChromaDB", "Buscando información semántica"],  # Lista de textos a almacenar
    ids=["doc1", "doc2", "doc3"],  # IDs únicos para cada documento
    metadatas=[
        {"categoria": "saludo", "idioma": "español", "nivel": "básico"},  # Metadatos del primer documento
        {"categoria": "tutorial", "idioma": "español", "nivel": "intermedio"},  # Metadatos del segundo documento
        {"categoria": "búsqueda", "idioma": "español", "nivel": "avanzado"}  # Metadatos del tercer documento
    ]
)

# Paso 4: Consultar los documentos insertados (consulta básica sin filtros)
# Esta consulta busca documentos similares sin aplicar filtros específicos
results_basic = collection.query(
    query_texts=["¿Cómo aprender ChromaDB?"],  # Texto de consulta para buscar similitud
    n_results=2  # Número de resultados más similares a retornar
)

# Paso 5: Consultar con filtros por metadatos
# Esta consulta aplica filtros para obtener solo documentos de categoría "tutorial"
# El filtro where restringe los resultados a documentos que cumplan la condición
results_filtered = collection.query(
    query_texts=["¿Cómo aprender ChromaDB?"],  # Texto de consulta para buscar similitud
    n_results=2,  # Número de resultados más similares a retornar
    where={"categoria": "tutorial"}  # Filtro: solo documentos de categoría "tutorial"
)

# Paso 6: Consultar con múltiples filtros (CORREGIDO)
# Esta consulta combina varios filtros usando operadores lógicos correctos
# $and permite combinar múltiples condiciones con operador AND
results_multi_filter = collection.query(
    query_texts=["¿Cómo aprender ChromaDB?"],  # Texto de consulta para buscar similitud
    n_results=3,  # Número de resultados más similares a retornar
    where={
        "$and": [
            {"idioma": "español"},  # Primer filtro: idioma español
            {"nivel": "intermedio"}  # Segundo filtro: nivel intermedio
        ]
    },
    where_document={"$contains": "ChromaDB"}  # Filtro adicional: documento debe contener "ChromaDB"
)

# Paso 7: Agregar más ejemplos de filtros para demostrar diferentes operadores
# Consulta usando operador OR para mostrar documentos de nivel básico O intermedio
results_or_filter = collection.query(
    query_texts=["¿Cómo aprender ChromaDB?"],  # Texto de consulta para buscar similitud
    n_results=3,  # Número de resultados más similares a retornar
    where={
        "$or": [
            {"nivel": "básico"},  # Documentos de nivel básico
            {"nivel": "intermedio"}  # O documentos de nivel intermedio
        ]
    }
)

# Paso 8: Consulta con operador NOT para excluir ciertos documentos (CORREGIDO)
# Esta consulta excluye documentos de nivel avanzado usando $ne (not equal)
# $ne es el operador correcto para "no igual" en ChromaDB
results_not_filter = collection.query(
    query_texts=["¿Cómo aprender ChromaDB?"],  # Texto de consulta para buscar similitud
    n_results=3,  # Número de resultados más similares a retornar
    where={
        "$and": [
            {"idioma": "español"},  # Filtro: idioma español
            {"nivel": {"$ne": "avanzado"}}  # Excluir documentos de nivel avanzado usando $ne
        ]
    }
)

# Paso 9: Agregar más ejemplos de operadores de comparación
# Consulta usando operador $in para buscar múltiples valores
results_in_filter = collection.query(
    query_texts=["¿Cómo aprender ChromaDB?"],  # Texto de consulta para buscar similitud
    n_results=3,  # Número de resultados más similares a retornar
    where={
        "nivel": {"$in": ["básico", "intermedio"]}  # Buscar documentos de nivel básico O intermedio
    }
)

# Paso 10: Consulta usando operador $nin (not in) para excluir múltiples valores
# Esta consulta excluye documentos de nivel básico y avanzado
results_nin_filter = collection.query(
    query_texts=["¿Cómo aprender ChromaDB?"],  # Texto de consulta para buscar similitud
    n_results=3,  # Número de resultados más similares a retornar
    where={
        "nivel": {"$nin": ["básico", "avanzado"]}  # Excluir documentos de nivel básico Y avanzado
    }
)

# Imprime los resultados de las diferentes consultas para comparar
print("=== CONSULTA BÁSICA (sin filtros) ===")
print(json.dumps(results_basic, indent=2, ensure_ascii=False))

print("\n=== CONSULTA CON FILTRO (solo tutorial) ===")
print(json.dumps(results_filtered, indent=2, ensure_ascii=False))

print("\n=== CONSULTA CON MÚLTIPLES FILTROS (AND) ===")
print(json.dumps(results_multi_filter, indent=2, ensure_ascii=False))

print("\n=== CONSULTA CON FILTRO OR ===")
print(json.dumps(results_or_filter, indent=2, ensure_ascii=False))

print("\n=== CONSULTA CON FILTRO NOT EQUAL ($ne) ===")
print(json.dumps(results_not_filter, indent=2, ensure_ascii=False))

print("\n=== CONSULTA CON FILTRO IN ($in) ===")
print(json.dumps(results_in_filter, indent=2, ensure_ascii=False))

print("\n=== CONSULTA CON FILTRO NOT IN ($nin) ===")
print(json.dumps(results_nin_filter, indent=2, ensure_ascii=False))
