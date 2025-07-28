import os  # Importa el módulo estándar para operaciones del sistema y variables de entorno
import csv  # Importa el módulo estándar para trabajar con archivos CSV
import logging  # Importa el módulo estándar para logging y seguimiento de eventos

from pathlib import Path  # Importa Path para manipulación de rutas de archivos de manera orientada a objetos
from typing import List, Dict, Any  # Importa tipos para anotaciones de funciones y variables
from dotenv import load_dotenv  # Importa la función para cargar variables de entorno desde un archivo .env

from langchain_community.document_loaders.csv_loader import CSVLoader  # Importa el cargador de documentos CSV de LangChain
from langchain_openai import OpenAIEmbeddings  # Importa la clase para generar embeddings usando OpenAI
from langchain_pinecone import PineconeVectorStore  # Importa la integración de Pinecone con LangChain para almacenamiento vectorial

from pinecone import Pinecone, ServerlessSpec  # Importa el cliente de Pinecone y la especificación serverless

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

pinecone_key = os.getenv("PINCONE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

pc = Pinecone(api_key=pinecone_key)

# Get OpenAI API key from environment variables

def load_content_from_csv(csv_file_path: str) -> List[Dict[str, Any]]:
    loader = CSVLoader(
        file_path=csv_file_path,
        source_column="id",        
        metadata_columns=[
            "id", 
            "title", 
            "original_title",
            "overview",
            "release_date",
            "vote_average",
            "vote_count",
            "popularity",
            "original_language",
            "genres",
            "poster_url"
        ],
        content_columns=[
            "title",           
            "original_title",  
            "overview",        
            "release_date"     
            "genres",          
        ],
    )
    data = loader.load()
    return data


def insert_content_to_pinecone(
        index_name: str, 
        content_data: List[Dict[str, Any]], 
        embedding: OpenAIEmbeddings
    ) -> None:
    """
    Insert content data into Pinecone collection.

    Args:
        content_data: List of content data dictionaries
    """
    if not pc.has_index(index_name):
        logger.error(f"Index {index_name} does not exist")
        return

    if not content_data:
        logger.warning("No content to insert")
        return

    try:
        PineconeVectorStore.from_documents(
            documents=content_data,
            embedding=embedding,
            index_name=index_name
        )
            
        logger.info(f"Successfully inserted {len(content_data)} content items into Pinecone")
        
    except Exception as e:
        logger.error(f"Error inserting content to Pinecone: {e}")
        raise

def main() -> None:
    """
    Main function to load content from CSV and insert into Pinecone.
    """
    try:
        # Create Pinecone index if it doesn't exist
        index_name = "streaming-content"

        if not pc.has_index(index_name):
            pc.create_index(
                name=index_name,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
        else:
            logger.info(f"Index {index_name} already exists")

        # Define CSV file path
        csv_file_path = Path(__file__).parent / "netflix_movies.csv"
        
        # Check if CSV file exists
        if not csv_file_path.exists():
            logger.error(f"CSV file not found: {csv_file_path}")
            return
        
        logger.info(f"Loading content from: {csv_file_path}")
        
        # Load content from CSV
        content_data = load_content_from_csv(str(csv_file_path))
        
        if not content_data:
            logger.error("No content loaded from CSV")
            return
        
        logger.info(f"Loaded {len(content_data)} content items from CSV")
        
        # Insert content into Pinecone
        embedding = OpenAIEmbeddings(api_key=openai_api_key, model="text-embedding-3-small")
        insert_content_to_pinecone(index_name, content_data, embedding)
        
        # Verify insertion by checking collection count
        index_stats = pc.Index(index_name).describe_index_stats()  # Get index statistics including total vector count
        index_count = index_stats.total_vector_count  # Extract total vector count from stats
        logger.info(f"Index now contains {index_count} documents")
        
        logger.info("Content data loading completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main() 