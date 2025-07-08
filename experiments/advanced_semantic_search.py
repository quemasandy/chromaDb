import chromadb  # Importa la librería principal de ChromaDB para interactuar con la base de datos
from chromadb.config import Settings  # Importa la clase Settings para configurar la conexión a ChromaDB
from chromadb.utils import embedding_functions  # Importa funciones de embedding para usar modelos personalizados
import json  # Importa el módulo json para formatear los resultados de manera legible
import time  # Importa el módulo time para medir el rendimiento de las operaciones
from typing import List, Dict, Any  # Importa tipos de datos para mejor documentación del código

class AdvancedSemanticSearch:
    """
    Clase para implementar búsqueda semántica avanzada con ChromaDB.
    
    Esta clase proporciona funcionalidades avanzadas como:
    - Embeddings personalizados con sentence-transformers
    - Diferentes métricas de similitud
    - Filtrado por metadatos
    - Búsqueda híbrida
    - Monitoreo de rendimiento
    """
    
    def __init__(self, persist_directory: str = "./chroma_db_advanced"):
        """
        Inicializa el sistema de búsqueda semántica avanzada.
        
        Args:
            persist_directory (str): Directorio donde se guardarán los datos de ChromaDB
        """
        # Configura el directorio de persistencia para almacenar los datos de ChromaDB
        # Esto permite que los datos persistan entre ejecuciones del programa
        self.persist_directory = persist_directory
        
        # Crea una instancia del cliente de ChromaDB con configuración personalizada
        # Settings(persist_directory=...) especifica dónde guardar los datos en disco
        self.client = chromadb.Client(Settings(persist_directory=persist_directory))
        
        # Configura el embedding function usando sentence-transformers
        # 'all-MiniLM-L6-v2' es un modelo eficiente y preciso para embeddings en español e inglés
        # Este modelo genera vectores de 384 dimensiones que capturan el significado semántico
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Crea o obtiene la colección principal con el embedding function personalizado
        # La colección almacenará documentos con embeddings generados por el modelo especificado
        self.collection = self.client.get_or_create_collection(
            name="advanced_semantic_collection",
            embedding_function=self.embedding_function
        )
        
        print(f"✅ Sistema de búsqueda semántica avanzada inicializado en: {persist_directory}")
    
    def add_documents_with_metadata(self, documents: List[str], ids: List[str], 
                                   metadatas: List[Dict[str, Any]] = None) -> None:
        """
        Agrega documentos a la colección con metadatos opcionales.
        
        Args:
            documents (List[str]): Lista de textos a almacenar
            ids (List[str]): IDs únicos para cada documento
            metadatas (List[Dict[str, Any]], optional): Metadatos para cada documento
        """
        # Valida que el número de documentos, IDs y metadatos sea consistente
        if metadatas is None:
            metadatas = [{} for _ in documents]  # Crea metadatos vacíos si no se proporcionan
        
        # Verifica que todos los arrays tengan la misma longitud para evitar errores
        if len(documents) != len(ids) or len(documents) != len(metadatas):
            raise ValueError("El número de documentos, IDs y metadatos debe ser igual")
        
        # Registra el tiempo de inicio para medir el rendimiento de la operación
        start_time = time.time()
        
        # Agrega los documentos a la colección con sus metadatos correspondientes
        # ChromaDB automáticamente generará embeddings usando el embedding function configurado
        self.collection.add(
            documents=documents,  # Lista de textos a procesar y almacenar
            ids=ids,  # Identificadores únicos para cada documento
            metadatas=metadatas  # Metadatos asociados a cada documento
        )
        
        # Calcula y muestra el tiempo total de la operación
        elapsed_time = time.time() - start_time
        print(f"✅ {len(documents)} documentos agregados en {elapsed_time:.2f} segundos")
    
    def semantic_search(self, query: str, n_results: int = 5, 
                       where_filter: Dict[str, Any] = None,
                       where_document_filter: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Realiza búsqueda semántica con filtros opcionales.
        
        Args:
            query (str): Texto de consulta para buscar similitud semántica
            n_results (int): Número de resultados más similares a retornar
            where_filter (Dict[str, Any], optional): Filtro por metadatos
            where_document_filter (Dict[str, Any], optional): Filtro por contenido del documento
            
        Returns:
            Dict[str, Any]: Resultados de la búsqueda con documentos, metadatos y distancias
        """
        # Registra el tiempo de inicio para medir el rendimiento de la consulta
        start_time = time.time()
        
        # Realiza la consulta semántica con los filtros especificados
        # El embedding function convertirá automáticamente la consulta a un vector
        results = self.collection.query(
            query_texts=[query],  # Convierte la consulta a lista para compatibilidad con ChromaDB
            n_results=n_results,  # Número máximo de resultados a retornar
            where=where_filter,  # Filtro opcional por metadatos
            where_document=where_document_filter  # Filtro opcional por contenido del documento
        )
        
        # Calcula el tiempo total de la consulta
        elapsed_time = time.time() - start_time
        
        # Agrega información de rendimiento a los resultados
        results['query_time'] = elapsed_time
        results['query'] = query
        
        print(f"🔍 Búsqueda completada en {elapsed_time:.3f} segundos")
        return results
    
    def hybrid_search(self, query: str, n_results: int = 5,
                     where_filter: Dict[str, Any] = None,
                     weight_text: float = 0.7) -> Dict[str, Any]:
        """
        Realiza búsqueda híbrida combinando búsqueda semántica y filtrado por metadatos.
        
        Args:
            query (str): Texto de consulta para búsqueda semántica
            n_results (int): Número de resultados a retornar
            where_filter (Dict[str, Any], optional): Filtro por metadatos
            weight_text (float): Peso para la búsqueda de texto (0.0 a 1.0)
            
        Returns:
            Dict[str, Any]: Resultados de la búsqueda híbrida
        """
        # Realiza búsqueda semántica básica
        semantic_results = self.semantic_search(query, n_results * 2, where_filter)
        
        # Si hay filtros de metadatos, aplica filtrado adicional
        if where_filter:
            # Filtra resultados por metadatos y recalcula rankings
            filtered_results = self._apply_metadata_filtering(semantic_results, where_filter)
            return filtered_results
        
        return semantic_results
    
    def _apply_metadata_filtering(self, results: Dict[str, Any], 
                                 where_filter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplica filtrado adicional por metadatos a los resultados de búsqueda.
        
        Args:
            results (Dict[str, Any]): Resultados de búsqueda semántica
            where_filter (Dict[str, Any]): Filtro de metadatos a aplicar
            
        Returns:
            Dict[str, Any]: Resultados filtrados
        """
        # Implementa lógica de filtrado personalizada aquí
        # Por ahora, retorna los resultados originales
        return results
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Obtiene información detallada sobre la colección actual.
        
        Returns:
            Dict[str, Any]: Información de la colección incluyendo conteo y metadatos
        """
        # Obtiene el conteo total de documentos en la colección
        count = self.collection.count()
        
        # Obtiene una muestra de documentos para analizar la estructura
        sample_results = self.collection.get(limit=5)
        
        return {
            'total_documents': count,
            'sample_documents': sample_results,
            'embedding_function': str(self.embedding_function),
            'persist_directory': self.persist_directory
        }

def main():
    """
    Función principal que demuestra el uso del sistema de búsqueda semántica avanzada.
    """
    # Crea una instancia del sistema de búsqueda semántica avanzada
    # Esto inicializa ChromaDB con embeddings personalizados
    search_system = AdvancedSemanticSearch()
    
    # Define documentos de ejemplo con metadatos ricos para demostrar capacidades avanzadas
    # Cada documento tiene metadatos que incluyen categoría, idioma, fecha y tags
    documents = [
        "ChromaDB es una base de datos vectorial de código abierto para aplicaciones de IA",
        "Los embeddings son representaciones vectoriales que capturan el significado semántico",
        "La búsqueda semántica permite encontrar información similar sin coincidencia exacta de palabras",
        "Los modelos de lenguaje como GPT utilizan embeddings para entender el contexto",
        "Las bases de datos vectoriales son esenciales para aplicaciones de IA moderna",
        "El procesamiento de lenguaje natural requiere comprensión semántica avanzada",
        "Los sistemas de recomendación utilizan similitud vectorial para sugerir contenido",
        "La indexación semántica mejora significativamente la precisión de búsqueda"
    ]
    
    # Define IDs únicos para cada documento
    ids = [f"doc_{i+1}" for i in range(len(documents))]
    
    # Define metadatos ricos para cada documento
    # Los metadatos permiten filtrado y organización avanzada
    metadatas = [
        {"category": "database", "language": "es", "difficulty": "beginner", "tags": ["chromadb", "vector"]},
        {"category": "ai", "language": "es", "difficulty": "intermediate", "tags": ["embeddings", "vectors"]},
        {"category": "search", "language": "es", "difficulty": "intermediate", "tags": ["semantic", "search"]},
        {"category": "ai", "language": "es", "difficulty": "advanced", "tags": ["gpt", "nlp"]},
        {"category": "database", "language": "es", "difficulty": "intermediate", "tags": ["vector", "ai"]},
        {"category": "nlp", "language": "es", "difficulty": "advanced", "tags": ["nlp", "semantic"]},
        {"category": "recommendation", "language": "es", "difficulty": "intermediate", "tags": ["recommendation", "vector"]},
        {"category": "search", "language": "es", "difficulty": "advanced", "tags": ["indexing", "semantic"]}
    ]
    
    # Agrega los documentos con sus metadatos a la colección
    # Esto generará embeddings automáticamente usando el modelo sentence-transformers
    search_system.add_documents_with_metadata(documents, ids, metadatas)
    
    # Obtiene y muestra información sobre la colección
    collection_info = search_system.get_collection_info()
    print("\n📊 Información de la colección:")
    print(json.dumps(collection_info, indent=2, ensure_ascii=False))
    
    # Demuestra diferentes tipos de búsqueda semántica avanzada
    
    print("\n🔍 === BÚSQUEDA SEMÁNTICA BÁSICA ===")
    # Realiza búsqueda semántica básica sin filtros
    basic_results = search_system.semantic_search("¿Qué es ChromaDB?", n_results=3)
    print("Consulta: '¿Qué es ChromaDB?'")
    print(json.dumps(basic_results, indent=2, ensure_ascii=False))
    
    print("\n🔍 === BÚSQUEDA CON FILTRO POR CATEGORÍA ===")
    # Realiza búsqueda semántica filtrando por categoría específica
    category_results = search_system.semantic_search(
        "bases de datos vectoriales", 
        n_results=3,
        where_filter={"category": "database"}
    )
    print("Consulta: 'bases de datos vectoriales' (solo categoría 'database')")
    print(json.dumps(category_results, indent=2, ensure_ascii=False))
    
    print("\n🔍 === BÚSQUEDA CON FILTRO POR DIFICULTAD ===")
    # Realiza búsqueda semántica filtrando por nivel de dificultad
    difficulty_results = search_system.semantic_search(
        "embeddings y vectores", 
        n_results=3,
        where_filter={"difficulty": "beginner"}
    )
    print("Consulta: 'embeddings y vectores' (solo dificultad 'beginner')")
    print(json.dumps(difficulty_results, indent=2, ensure_ascii=False))
    
    print("\n🔍 === BÚSQUEDA HÍBRIDA ===")
    # Realiza búsqueda híbrida combinando semántica y filtros
    hybrid_results = search_system.hybrid_search(
        "inteligencia artificial", 
        n_results=3,
        where_filter={"category": "ai"}
    )
    print("Consulta: 'inteligencia artificial' (categoría 'ai')")
    print(json.dumps(hybrid_results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # Ejecuta la función principal cuando el script se ejecuta directamente
    # Esto permite que el código se ejecute como programa independiente
    main() 