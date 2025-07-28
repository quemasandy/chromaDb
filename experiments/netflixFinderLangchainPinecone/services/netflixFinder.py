import os  # Importa el módulo estándar para operaciones del sistema y variables de entorno
import logging  # Importa el módulo estándar para logging y seguimiento de eventos
from typing import Dict, Any  # Importa tipos para anotaciones de funciones y variables

from dotenv import load_dotenv  # Importa la función para cargar variables de entorno desde un archivo .env

from pinecone import Pinecone  # Permite la interacción con la base de datos vectorial Pinecone

from langchain_openai import ChatOpenAI  # Permite la interacción con modelos de lenguaje de OpenAI
from langchain_openai import OpenAIEmbeddings  # Importa embeddings de OpenAI para vectorización de texto

from langchain_pinecone import PineconeVectorStore  # Permite integrar Pinecone con LangChain para almacenamiento vectorial

from langchain_core.prompts import ChatPromptTemplate  # Permite la creación de plantillas de prompts para chat
from langchain.chains.combine_documents import create_stuff_documents_chain  # Permite combinar documentos para cadenas de procesamiento
from langchain.chains import create_retrieval_chain  # Permite crear cadenas de recuperación de información

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINCONE_API_KEY")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NetflixFinderService:
    """
    Generic service for searching Netflix content using ChromaDB.
    
    This service provides semantic search capabilities with filtering options
    for release date, vote average, vote count, popularity, and genres.
    """
    
    def __init__(self, llm: ChatOpenAI, index_name: str):
        """Initialize the NetflixFinder service with Pinecone connection."""
        
        # Set the index name
        self.index_name = index_name
        
        # Set the LLM model
        self.llm = llm
        
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=pinecone_api_key)
        
        # Create OpenAI embeddings for the vector store
        self.embeddings = OpenAIEmbeddings(
            api_key=openai_api_key,  # Use OpenAI API key for authentication
            model="text-embedding-3-small"  # Specify the embedding model to use
        )
        
        # Create PineconeVectorStore for retrieval
        self.vector_store = PineconeVectorStore(
            index=self.pc.Index(self.index_name),  # Use Pinecone index
            embedding=self.embeddings,  # Use OpenAI embeddings
            text_key="text"  # Specify the key for text content
        )
        
        logger.info(f"NetflixFinder service initialized with index: {self.index_name}")

    def _get_index_as_retriever(self):
        return self.vector_store.as_retriever()  # Return the vector store as a retriever
    
    def search_content(self, query: str) -> Dict[str, Any]:
        try:
            logger.info(f"Searching for content with query: '{query}'")
                        
            # Define the system prompt for the language model
            # system_prompt = (
            #     "You are an expert movie recommendation analyst. Your primary goal is to find and articulate compelling connections between the user's query and the specific movies provided in the context. Your reasoning should be creative and insightful."
            #     "\n\n"
            #     "**Your instructions are absolute and you must follow them without exception:**"
            #     "\n\n"
            #     "1.  **Justify Every Single Movie:** For each movie in the `{context}`, you MUST explain its connection to the user's request. Identify which specific keywords or themes from the user's query (e.g., genre, mood, actors, plot elements) the movie satisfies. "
            #     "\n"
            #     "2.  **Embrace Imperfect Matches:** The provided movies might only match a part of the user's query. Your task is to highlight that partial match and present it as a valid reason for the recommendation. For example, if the user wants 'sci-fi comedy' and the context has a 'sci-fi action' movie, you will highlight the shared 'sci-fi' element."
            #     "\n"
            #     "3.  **No Excuses Rule:** You are strictly forbidden from stating that no movies match, that the context is irrelevant, or that you cannot find a suitable recommendation. Your entire purpose is to work with the provided information and convince the user of its relevance. Treat the context as the only truth."
            #     "\n"
            #     "4.  **Rank and Structure:** Present the movies in a ranked list, from the one with the strongest connection to the one with the most creative or tenuous connection. For each movie, you must provide:"
            #     "    - The **Title**."
            #     "    - The **poster_url**."
            #     "    - A clear, persuasive paragraph titled **'Connection to your query:'** that contains your justification."
            #     "\n\n"
            #     "context: {context}"
            # )

            # Define the system prompt for the language model
            system_prompt = (
            "Eres un analista experto en recomendación de películas. Tu objetivo principal es encontrar y articular conexiones convincentes entre la consulta del usuario y las películas específicas proporcionadas en el contexto. Tu razonamiento debe ser creativo y perspicaz."
            "\n\n"
            "**Tus instrucciones son absolutas y debes seguirlas sin excepción:**"
            "\n\n"
            "1.  **Justifica Cada Película:** Para cada película en el `{context}`, DEBES explicar su conexión con la solicitud del usuario. Identifica qué palabras clave o temas de la consulta del usuario satisface la película."
            "\n"
            "2.  **Acepta Coincidencias Imperfectas:** Es posible que las películas proporcionadas solo coincidan con una parte de la consulta. Tu tarea es resaltar esa coincidencia parcial y presentarla como una razón válida para la recomendación."
            "\n"
            "3.  **Regla de 'No Excusas':** Tienes estrictamente prohibido decir que ninguna película coincide o que el contexto es irrelevante. Tu único propósito es trabajar con la información proporcionada y convencer al usuario de su relevancia."
            "\n"
            "4.  **Clasifica y Estructura:** Presenta las películas en una lista ordenada, desde la conexión más fuerte hasta la más creativa. Para cada película, debes extraer la siguiente información directamente de sus metadatos en el contexto y presentarla de la siguiente manera:"
            "    - **Título:** [El título de la película]"
            "    - **URL del póster:** [La URL del póster. Encontrarás esta URL exacta dentro de los metadatos de cada película.]"
            "    - **Conexión con tu búsqueda:** [Tu párrafo de justificación claro y persuasivo aquí.]"
            "\n\n"
            "**IMPORTANTE: Toda tu respuesta final DEBE estar escrita en español.**"
            "\n\n"
            "context: {context}"
            )

            # Create a chat prompt template with system and human messages
            prompt = ChatPromptTemplate.from_messages(
                [
                    # Define el mensaje del sistema con las instrucciones
                    ("system", system_prompt),
                    # Define el mensaje del usuario con placeholder para la pregunta
                    ("human", "{input}"),
                ]
            )

            # Create a chain that combines documents with the language model
            question_answer_chain = create_stuff_documents_chain(
                llm=self.llm,  # Modelo de lenguaje a usar
                prompt=prompt,  # Plantilla de prompt a usar
            )

            # Create a RAG (Retrieval-Augmented Generation) chain
            # Combina el retriever con la cadena de respuesta
            rag_chain = create_retrieval_chain(self._get_index_as_retriever(), question_answer_chain)
            
            # Execute the RAG chain
            result = rag_chain.invoke({"input": query})
            
            logger.info(f"Found results for query: '{query}'")
            return result
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            raise


# Example usage and testing
if __name__ == "__main__":
    try:
        # Initialize service
        index_name = "streaming-content"
        llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4")
        finder = NetflixFinderService(llm=llm, index_name=index_name)
        
        # # Example 1: Search with filters
        print("\n=== EXAMPLE 1: Search with filters ===\n")
        query = "I want a movie with samurais and japanese culture and to be like fast and furious"
        
        results = finder.search_content(
            query=query,
        )

        print(f"\n\nquery: {query}")
        # Itera sobre los documentos en el contexto y muestra el título y la URL del póster de cada película
        print("\nMovies in context:")
        for doc in results.get('context', []):  # Itera sobre la lista de documentos en el contexto de resultados
            # Extrae el título y la URL del póster de los metadatos del documento
            title = doc.metadata.get('title', 'Unknown Title')  # Obtiene el título de la película o un valor por defecto
            poster_url = doc.metadata.get('poster_url', 'No poster URL available')  # Obtiene la URL del póster o un valor por defecto
            print(f"Title: {title}")  # Imprime el título de la película
            print(f"Poster URL: {poster_url}")  # Imprime la URL del póster de la película
            print("-" * 40)  # Imprime una línea divisoria para separar las películas

        # Muestra la respuesta generada por el modelo de lenguaje
        print("\nLLM Answer:")  # Imprime un encabezado para la respuesta del modelo
        print(results.get('answer', 'No answer available'))  # Imprime la respuesta o un valor por defecto si no existe
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise
