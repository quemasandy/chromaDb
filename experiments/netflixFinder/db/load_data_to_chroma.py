import csv
import logging
import os
from pathlib import Path
from typing import List, Dict, Any

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

# Create OpenAI embedding function
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai_api_key,  # Pass API key for authentication
    model_name="text-embedding-3-small"  # Specify embedding model to use
)

# Create persistent ChromaDB client that saves data to disk
chroma_client = chromadb.PersistentClient(path="./db/chroma_persist")

# Create or get existing collection called "content" with OpenAI embedding function
collection = chroma_client.get_or_create_collection(
    "content",  # Collection name for both movies and series
    embedding_function=openai_ef,  # Specify to use OpenAI embedding function
)

def load_content_from_csv(csv_file_path: str) -> List[Dict[str, Any]]:
    """
    Load content data from CSV file and prepare for ChromaDB insertion.
    
    Args:
        csv_file_path: Path to the CSV file containing content data
        
    Returns:
        List of dictionaries with content data prepared for ChromaDB
    """
    content_data = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            # Create CSV reader with dictionary format
            reader = csv.DictReader(file)
            
            for row in reader:
                # Create document text with relevant searchable information
                document_text = f"Title: {row['title']}\n"
                document_text += f"Original Title: {row['original_title']}\n"
                document_text += f"Overview: {row['overview']}\n"
                document_text += f"Genres: {row['genres']}\n"
                document_text += f"Language: {row['original_language']}\n"
                document_text += f"Release Date: {row['release_date']}"
                
                # Create metadata with all content information plus Netflix and type indicators
                metadata = {
                    "id": row['id'],
                    "title": row['title'],
                    "original_title": row['original_title'],
                    "overview": row['overview'],
                    "release_date": row['release_date'],
                    "vote_average": float(row['vote_average']),
                    "vote_count": int(row['vote_count']),
                    "popularity": float(row['popularity']),
                    "original_language": row['original_language'],
                    "genres": row['genres'],
                    "poster_url": row['poster_url'],
                    "source": "netflix",  # Indicate data comes from Netflix
                    "content_type": "movie"  # Default to movie, can be updated for series
                }
                
                content_data.append({
                    "id": row['id'],  # Simple ID - works for your case
                    "document": document_text,  # Searchable text content
                    "metadata": metadata  # All content information as metadata
                })
                
    except FileNotFoundError:
        logger.error(f"CSV file not found: {csv_file_path}")
        return []
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return []
    
    return content_data

def insert_content_to_chroma(content_data: List[Dict[str, Any]]) -> None:
    """
    Insert content data into ChromaDB collection.
    
    Args:
        content_data: List of content data dictionaries
    """
    if not content_data:
        logger.warning("No content to insert")
        return
    
    try:
        # Prepare data for batch insertion
        ids = [content["id"] for content in content_data]
        documents = [content["document"] for content in content_data]
        metadatas = [content["metadata"] for content in content_data]
        
        # Insert content into collection
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        logger.info(f"Successfully inserted {len(content_data)} content items into ChromaDB")
        
    except Exception as e:
        logger.error(f"Error inserting content to ChromaDB: {e}")
        raise

def main() -> None:
    """
    Main function to load content from CSV and insert into ChromaDB.
    """
    try:
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
        
        # Insert content into ChromaDB
        insert_content_to_chroma(content_data)
        
        # Verify insertion by checking collection count
        collection_count = collection.count()
        logger.info(f"Collection now contains {collection_count} documents")
        
        logger.info("Content data loading completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main() 