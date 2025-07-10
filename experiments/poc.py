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

# Paso 11: Función para actualizar un documento existente en la colección

def update_document(collection, doc_id, new_text=None, new_metadata=None):
    """
    Actualiza el texto y/o los metadatos de un documento en la colección de ChromaDB.

    Parámetros:
        collection: Objeto de colección de ChromaDB donde se almacenan los documentos.
        doc_id (str): ID único del documento a actualizar.
        new_text (str, opcional): Nuevo texto para el documento. Si es None, no se actualiza el texto.
        new_metadata (dict, opcional): Nuevos metadatos para el documento. Si es None, no se actualizan los metadatos.

    Retorna:
        dict: Resultado de la actualización o mensaje de error.
    """
    try:
        # Paso 1: Consultar si el documento existe usando su ID
        existing = collection.get(ids=[doc_id])  # Busca el documento por ID
        if not existing["ids"] or len(existing["ids"]) == 0:
            # Si la lista de IDs está vacía, el documento no existe
            return {"error": f"Documento con ID '{doc_id}' no encontrado."}

        # Paso 2: Preparar los nuevos valores para actualizar
        updated_text = new_text if new_text is not None else existing["documents"][0]  # Usa el nuevo texto o el actual
        updated_metadata = new_metadata if new_metadata is not None else existing["metadatas"][0]  # Usa los nuevos metadatos o los actuales

        # Paso 3: Realizar la actualización usando el método update
        collection.update(
            ids=[doc_id],  # Lista con el ID a actualizar
            documents=[updated_text],  # Lista con el nuevo texto
            metadatas=[updated_metadata]  # Lista con los nuevos metadatos
        )

        # Paso 4: Consultar el documento actualizado para mostrar el resultado final
        updated = collection.get(ids=[doc_id])
        return {"success": True, "updated": updated}
    except Exception as e:
        # Manejo de errores: retorna el mensaje de la excepción
        return {"error": str(e)}

# Ejemplo de uso de la función update_document
print("\n=== ACTUALIZANDO DOCUMENTO 'doc2' ===")
# Mostrar el documento antes de la actualización
print("Antes:")
print(json.dumps(collection.get(ids=["doc2"]), indent=2, ensure_ascii=False))

# Actualizar el texto y los metadatos del documento 'doc2'
resultado_update = update_document(
    collection,
    doc_id="doc2",
    new_text="ChromaDB avanzado y práctico",  # Nuevo texto para el documento
    new_metadata={"categoria": "tutorial", "idioma": "español", "nivel": "avanzado"}  # Nuevos metadatos
)

# Mostrar el resultado de la actualización
print("Después:")
print(json.dumps(collection.get(ids=["doc2"]), indent=2, ensure_ascii=False))

# Mostrar si hubo error o éxito
if "error" in resultado_update:
    print("Error al actualizar:", resultado_update["error"])
else:
    print("Actualización exitosa.")


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
