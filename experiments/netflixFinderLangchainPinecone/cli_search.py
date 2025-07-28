#!/usr/bin/env python3
"""
NetflixFinder CLI - Command Line Interface for searching Netflix content.

This program provides an interactive interface to search for movies and series
using the NetflixFinder service with semantic search.
"""

import sys  # Importa el módulo estándar para operaciones del sistema y argumentos de línea de comandos
import os  # Importa el módulo estándar para operaciones del sistema y variables de entorno
import logging  # Importa el módulo estándar para logging y seguimiento de eventos
from typing import Optional, List, Dict, Any  # Importa tipos para anotaciones de funciones y variables
from pathlib import Path  # Importa Path para manipulación de rutas de archivos

# Add the services directory to the path to import NetflixFinderService
sys.path.append(str(Path(__file__).parent / "services"))  # Agrega el directorio de servicios al path para importar NetflixFinderService

from services.netflixFinder import NetflixFinderService  # Importa el servicio de búsqueda de Netflix
from langchain_openai import ChatOpenAI  # Importa el modelo de chat de OpenAI para procesamiento de lenguaje natural
from dotenv import load_dotenv  # Importa la función para cargar variables de entorno desde un archivo .env

# Load environment variables from .env file
load_dotenv()  # Carga las variables de entorno desde el archivo .env

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Establece el nivel de logging en INFO para mostrar mensajes informativos
    format='%(asctime)s - %(levelname)s - %(message)s'  # Define el formato de los mensajes de log
)
logger = logging.getLogger(__name__)  # Crea un logger específico para este módulo

class NetflixFinderCLI:
    """
    Command Line Interface for NetflixFinder service.
    
    Provides interactive prompts for search queries with semantic search capabilities.
    """
    
    def __init__(self):
        """Initialize the CLI with NetflixFinder service."""
        try:
            # Get OpenAI API key from environment variables
            openai_api_key = os.getenv("OPENAI_API_KEY")  # Obtiene la clave de API de OpenAI desde las variables de entorno
            if not openai_api_key:  # Verifica si la clave de API existe
                raise ValueError("OPENAI_API_KEY not found in environment variables")  # Lanza un error si no se encuentra la clave
            
            # Initialize the language model for processing
            llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4")  # Inicializa el modelo de lenguaje GPT-4 para procesamiento
            
            # Define the Pinecone index name for the vector database
            index_name = "streaming-content"  # Define el nombre del índice en Pinecone donde están almacenados los datos de películas
            
            # Initialize the NetflixFinder service with required parameters
            self.finder = NetflixFinderService(llm=llm, index_name=index_name)  # Inicializa el servicio con el modelo de lenguaje y el nombre del índice
            print("✅ NetflixFinder CLI initialized successfully!")  # Imprime mensaje de éxito al inicializar
        except Exception as e:
            print(f"❌ Error initializing NetflixFinder service: {e}")  # Imprime mensaje de error si falla la inicialización
            sys.exit(1)  # Termina el programa con código de error
    
    def get_user_input(self, prompt: str, default: str = "") -> str:
        """
        Get user input with optional default value.
        
        Args:
            prompt: The prompt to show to the user
            default: Default value if user just presses Enter
            
        Returns:
            User input or default value
        """
        if default:  # Si hay un valor por defecto disponible
            user_input = input(f"{prompt} (default: {default}): ").strip()  # Solicita entrada del usuario mostrando el valor por defecto
            return user_input if user_input else default  # Retorna la entrada del usuario o el valor por defecto si está vacío
        else:
            return input(f"{prompt}: ").strip()  # Solicita entrada del usuario sin valor por defecto
    
    def get_optional_int(self, prompt: str, default: int = 5) -> int:
        """
        Get optional integer input from user with default value.
        
        Args:
            prompt: The prompt to show to the user
            default: Default integer value
            
        Returns:
            Integer value or default if user presses Enter
        """
        user_input = self.get_user_input(prompt, str(default))  # Solicita entrada del usuario con valor por defecto convertido a string
        try:
            return int(user_input)  # Intenta convertir la entrada a entero
        except ValueError:
            print(f"❌ Invalid number format. Using default value: {default}")  # Imprime mensaje de error si la conversión falla
            return default  # Retorna el valor por defecto en caso de error
    
    def display_search_results(self, results: Dict[str, Any], query: str) -> None:
        """
        Display search results in a formatted way showing context movies and LLM answer.
        
        Args:
            results: Search results from NetflixFinder service containing context and answer
            query: Original search query
        """
        print("\n" + "="*60)  # Imprime separador visual para los resultados
        print(f"🎬 SEARCH RESULTS FOR: '{query}'")  # Imprime el encabezado con la consulta original
        print("="*60)  # Imprime línea separadora
        
        # Display movies found in context
        context_movies = results.get('context', [])  # Obtiene la lista de películas del contexto de resultados
        if not context_movies:  # Verifica si no hay películas en el contexto
            print("❌ No movies found in context for your search criteria.")  # Imprime mensaje de no resultados
            return
        
        print(f"✅ Found {len(context_movies)} movies in context\n")  # Imprime el número de películas encontradas
        
        print("📽️  MOVIES IN CONTEXT:")  # Imprime encabezado para las películas en contexto
        print("-" * 40)  # Imprime línea separadora
        
        # Iterate through each movie in the context and display its information
        for i, doc in enumerate(context_movies, 1):  # Itera sobre cada documento de película en el contexto
            title = doc.metadata.get('title', 'Unknown Title')  # Obtiene el título de la película o un valor por defecto
            poster_url = doc.metadata.get('poster_url', 'No poster URL available')  # Obtiene la URL del póster o un valor por defecto
            overview = doc.metadata.get('overview', 'No overview available')  # Obtiene la sinopsis de la película o un valor por defecto
            release_date = doc.metadata.get('release_date', 'N/A')  # Obtiene la fecha de lanzamiento o un valor por defecto
            vote_average = doc.metadata.get('vote_average', 'N/A')  # Obtiene la calificación promedio o un valor por defecto
            genres = doc.metadata.get('genres', 'N/A')  # Obtiene los géneros de la película o un valor por defecto
            
            print(f"🎯 MOVIE {i}:")  # Imprime el número de la película
            print(f"   Title: {title}")  # Imprime el título de la película
            print(f"   Release Date: {release_date}")  # Imprime la fecha de lanzamiento
            print(f"   Rating: {vote_average}/10")  # Imprime la calificación
            print(f"   Genres: {genres}")  # Imprime los géneros
            print(f"   Overview: {overview[:150]}{'...' if len(overview) > 150 else ''}")  # Imprime una versión truncada de la sinopsis
            print(f"   Poster URL: {poster_url}")  # Imprime la URL del póster
            print("-" * 40)  # Imprime línea separadora entre películas
        
        # Display the LLM-generated recommendation answer
        print("\n🤖 AI RECOMMENDATION ANALYSIS:")  # Imprime encabezado para el análisis de IA
        print("="*60)  # Imprime línea separadora
        llm_answer = results.get('answer', 'No recommendation analysis available')  # Obtiene la respuesta del modelo de lenguaje
        print(llm_answer)  # Imprime la respuesta generada por el modelo de IA
        print("="*60)  # Imprime línea separadora final
    
    def run(self) -> None:
        """
        Main CLI loop for interactive movie search.
        """
        print("🎬 NETFLIX FINDER CLI")  # Imprime el título de la aplicación CLI
        print("="*60)  # Imprime línea separadora
        print("Welcome to NetflixFinder! Search for movies and series with AI-powered semantic search.")  # Imprime mensaje de bienvenida
        print("="*60)  # Imprime línea separadora
        
        while True:  # Inicia el bucle principal de la interfaz
            try:
                # Get search query from user
                print("\n" + "="*60)  # Imprime separador visual para nueva búsqueda
                query = self.get_user_input("What kind of movie or series do you want to watch?")  # Solicita la consulta de búsqueda al usuario
                
                if not query:  # Verifica si el usuario no ingresó una consulta
                    print("❌ Please enter a search query.")  # Imprime mensaje de error para consulta vacía
                    continue  # Continúa al siguiente ciclo del bucle
                
                # Perform search using the simplified API
                print(f"\n🔍 Searching for: '{query}'")  # Imprime mensaje indicando que se está realizando la búsqueda
                print("Please wait while our AI analyzes your request...")  # Imprime mensaje de espera mientras se procesa
                
                # Call the search service with only the query parameter
                results = self.finder.search_content(query=query)  # Ejecuta la búsqueda usando solo la consulta como parámetro
                
                # Display the search results
                self.display_search_results(results, query)  # Muestra los resultados de la búsqueda formateados
                
                # Ask if user wants to continue searching
                print("\n" + "="*60)  # Imprime separador para opciones de continuación
                continue_search = self.get_user_input("Would you like to search for something else? (y/n)", "y").lower()  # Pregunta si el usuario quiere continuar buscando
                if continue_search not in ['y', 'yes', '']:  # Verifica si el usuario no quiere continuar
                    break  # Sale del bucle principal
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for using NetflixFinder!")  # Maneja la interrupción del teclado con mensaje de despedida
                break  # Sale del bucle principal
            except Exception as e:
                print(f"\n❌ Error during search: {e}")  # Imprime mensaje de error si ocurre una excepción
                logger.error(f"Search error: {e}")  # Registra el error en el log
                continue_search = self.get_user_input("An error occurred. Try again? (y/n)", "y").lower()  # Pregunta si el usuario quiere intentar de nuevo
                if continue_search not in ['y', 'yes', '']:  # Verifica si el usuario no quiere continuar
                    break  # Sale del bucle principal
        
        print("\n👋 Thanks for using NetflixFinder CLI! Happy watching! 🍿")  # Imprime mensaje final de despedida

def main():
    """Main entry point for the CLI application."""
    try:
        cli = NetflixFinderCLI()  # Crea una instancia de la interfaz CLI
        cli.run()  # Ejecuta el bucle principal de la interfaz
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")  # Maneja la interrupción del teclado con mensaje de despedida
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")  # Imprime mensaje de error fatal
        logger.error(f"Fatal error: {e}")  # Registra el error fatal en el log
        sys.exit(1)  # Termina el programa con código de error

if __name__ == "__main__":
    main()  # Ejecuta la función principal si el script se ejecuta directamente 