import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

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

class NetflixFinderService:
    """
    Generic service for searching Netflix content using ChromaDB.
    
    This service provides semantic search capabilities with filtering options
    for release date, vote average, vote count, popularity, and genres.
    """
    
    def __init__(self):
        """Initialize the NetflixFinder service with ChromaDB connection."""
        # Get OpenAI API key from environment variables
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Create OpenAI embedding function
        self.openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_api_key,  # Pass API key for authentication
            model_name="text-embedding-3-small"  # Specify embedding model to use
        )
        
        # Create ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path="./db/chroma_persist")
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            "content",  # Collection name for both movies and series
            embedding_function=self.openai_ef  # Specify to use OpenAI embedding function
        )
        
        logger.info(f"NetflixFinder service initialized with collection: {self.collection.name}")
    
    def _convert_date_to_timestamp(self, date_str: str) -> int:
        """
        Convert date string to timestamp for ChromaDB filtering.
        
        Args:
            date_str: Date string in format 'YYYY-MM-DD'
            
        Returns:
            Timestamp as integer
        """
        try:
            # Parse date string to datetime object
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            # Convert to timestamp (seconds since epoch)
            return int(date_obj.timestamp())
        except ValueError as e:
            logger.error(f"Invalid date format: {date_str}. Expected format: YYYY-MM-DD")
            raise ValueError(f"Invalid date format: {date_str}. Expected format: YYYY-MM-DD") from e
    
    def _build_where_filter(self, 
                           release_date_start: Optional[str] = None,
                           release_date_end: Optional[str] = None,
                           vote_average_min: Optional[float] = None,
                           vote_average_max: Optional[float] = None,
                           vote_count_min: Optional[int] = None,
                           vote_count_max: Optional[int] = None,
                           popularity_min: Optional[float] = None,
                           popularity_max: Optional[float] = None,
                           genres: Optional[List[str]] = None,
                           content_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Build ChromaDB where filter based on provided parameters.
        
        Args:
            release_date_start: Start date for filtering (YYYY-MM-DD format)
            release_date_end: End date for filtering (YYYY-MM-DD format)
            vote_average_min: Minimum vote average
            vote_average_max: Maximum vote average
            vote_count_min: Minimum vote count
            vote_count_max: Maximum vote count
            popularity_min: Minimum popularity
            popularity_max: Maximum popularity
            genres: List of genres to filter by
            content_type: Content type to filter by (movie, series, etc.)
            
        Returns:
            ChromaDB where filter dictionary
        """
        where_conditions = []
        
        # Date range filtering (convert to timestamps)
        if release_date_start:
            start_timestamp = self._convert_date_to_timestamp(release_date_start)
            where_conditions.append({"release_date": {"$gte": start_timestamp}})
        
        if release_date_end:
            end_timestamp = self._convert_date_to_timestamp(release_date_end)
            where_conditions.append({"release_date": {"$lte": end_timestamp}})
        
        # Vote average filtering
        if vote_average_min is not None:
            where_conditions.append({"vote_average": {"$gte": vote_average_min}})
        
        if vote_average_max is not None:
            where_conditions.append({"vote_average": {"$lte": vote_average_max}})
        
        # Vote count filtering
        if vote_count_min is not None:
            where_conditions.append({"vote_count": {"$gte": vote_count_min}})
        
        if vote_count_max is not None:
            where_conditions.append({"vote_count": {"$lte": vote_count_max}})
        
        # Popularity filtering
        if popularity_min is not None:
            where_conditions.append({"popularity": {"$gte": popularity_min}})
        
        if popularity_max is not None:
            where_conditions.append({"popularity": {"$lte": popularity_max}})
        
        # Genre filtering (exact match)
        if genres:
            # For multiple genres, we need to use $in operator
            where_conditions.append({"genres": {"$in": genres}})
        
        # Content type filtering
        if content_type:
            where_conditions.append({"content_type": content_type})
        
        # Combine all conditions with AND logic
        if len(where_conditions) == 1:
            return where_conditions[0]
        elif len(where_conditions) > 1:
            return {"$and": where_conditions}
        else:
            return {}
    
    def search_content(self,
                      query: str,
                      n_results: int = 5,
                      release_date_start: Optional[str] = None,
                      release_date_end: Optional[str] = None,
                      vote_average_min: Optional[float] = None,
                      vote_average_max: Optional[float] = None,
                      vote_count_min: Optional[int] = None,
                      vote_count_max: Optional[int] = None,
                      popularity_min: Optional[float] = None,
                      popularity_max: Optional[float] = None,
                      genres: Optional[List[str]] = None,
                      content_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for content using semantic similarity with optional filters.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            release_date_start: Start date for filtering (YYYY-MM-DD format)
            release_date_end: End date for filtering (YYYY-MM-DD format)
            vote_average_min: Minimum vote average
            vote_average_max: Maximum vote average
            vote_count_min: Minimum vote count
            vote_count_max: Maximum vote count
            popularity_min: Minimum popularity
            popularity_max: Maximum popularity
            genres: List of genres to filter by
            content_type: Content type to filter by (movie, series, etc.)
            
        Returns:
            Dictionary containing search results with documents, metadatas, distances, and ids
        """
        try:
            logger.info(f"Searching for content with query: '{query}'")
            
            # Build where filter based on provided parameters
            where_filter = self._build_where_filter(
                release_date_start=release_date_start,
                release_date_end=release_date_end,
                vote_average_min=vote_average_min,
                vote_average_max=vote_average_max,
                vote_count_min=vote_count_min,
                vote_count_max=vote_count_max,
                popularity_min=popularity_min,
                popularity_max=popularity_max,
                genres=genres,
                content_type=content_type
            )
            
            # Log filter conditions for debugging
            if where_filter:
                logger.info(f"Applied filters: {where_filter}")
            
            # Perform semantic search with filters
            if where_filter:  # Only pass where parameter if there are actual filters
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where=where_filter,
                    include=["documents", "metadatas", "distances"]
                )
            else:  # No filters - search all content
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    include=["documents", "metadatas", "distances"]
                )
            
            # Extract results safely
            try:
                ids = results['ids'][0] if 'ids' in results and results['ids'] else []
                documents = results['documents'][0] if 'documents' in results and results['documents'] else []
                metadatas = results['metadatas'][0] if 'metadatas' in results and results['metadatas'] else []
                distances = results['distances'][0] if 'distances' in results and results['distances'] else []
            except (IndexError, TypeError):
                ids = []
                documents = []
                metadatas = []
                distances = []
            
            result_dict = {
                'ids': ids,
                'documents': documents,
                'metadatas': metadatas,
                'distances': distances
            }
            
            logger.info(f"Found {len(ids)} results for query: '{query}'")
            return result_dict
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            raise
    
    def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific content by ID.
        
        Args:
            content_id: ID of the content to retrieve
            
        Returns:
            Content metadata and document or None if not found
        """
        try:
            results = self.collection.get(
                ids=[content_id],
                include=["documents", "metadatas"]
            )
            
            if results and results.get('ids'):
                try:
                    document = results['documents'][0] if 'documents' in results and results['documents'] else None
                    metadata = results['metadatas'][0] if 'metadatas' in results and results['metadatas'] else None
                    
                    return {
                        'id': results['ids'][0],
                        'document': document,
                        'metadata': metadata
                    }
                except (IndexError, TypeError):
                    return None
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving content by ID {content_id}: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the content collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            
            # Get sample of documents to analyze metadata
            sample_results = self.collection.get(
                limit=min(100, count),
                include=["metadatas"]
            )
            
            # Analyze content types
            content_types = {}
            genres = {}
            
            if sample_results and sample_results.get('metadatas'):
                metadatas_list = sample_results.get('metadatas', [])
                if metadatas_list:
                    for metadata in metadatas_list:
                        # Count content types
                        content_type = metadata.get('content_type', 'unknown')
                        content_types[content_type] = content_types.get(content_type, 0) + 1
                        
                        # Count genres - handle different data types
                        genre_data = metadata.get('genres', '')
                        if isinstance(genre_data, str) and genre_data:
                            for genre in genre_data.split(', '):
                                genres[genre] = genres.get(genre, 0) + 1
                        elif isinstance(genre_data, list):
                            for genre in genre_data:
                                genres[genre] = genres.get(genre, 0) + 1
            
            return {
                'total_documents': count,
                'content_types': content_types,
                'top_genres': dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)[:10])
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            raise

# Example usage and testing
if __name__ == "__main__":
    try:
        # Initialize service
        finder = NetflixFinderService()
        
        # # Example 1: Search with filters
        print("\n=== EXAMPLE 1: Search with filters ===\n")
        query = "I want a movie with samurais and japanese culture and to be like fast and furious"
        
        results = finder.search_content(
            query=query,
            n_results=3,
            # release_date_start="2000-01-01",  # From year 2000
            # vote_average_min=6.0,  # Minimum rating 6.0
            # genres=["Action", "Thriller"],  # Specific genres
            # content_type="movie"  # Only movies
        )
        
        print(f"Search results for: '{query}' (WITH FILTERS)")
        print(f"Found {len(results['ids'])} results")
        
        for i, (doc_id, doc, metadata, distance) in enumerate(zip(
            results['ids'], 
            results['documents'], 
            results['metadatas'], 
            results['distances']
        )):
            print(f"\n--- Result {i+1} (Distance: {distance:.4f}) ---")
            print(f"ID: {doc_id}")
            print(f"Title: {metadata.get('title', 'N/A')}")
            print(f"Genres: {metadata.get('genres', 'N/A')}")
            print(f"Release Date: {metadata.get('release_date', 'N/A')}")
            print(f"Vote Average: {metadata.get('vote_average', 'N/A')}")
        
        print("\n" + "="*60)
        
        # Get collection statistics
        stats = finder.get_collection_stats()
        print(f"\n=== COLLECTION STATISTICS ===")
        print(f"Total documents: {stats['total_documents']}")
        print(f"Content types: {stats['content_types']}")
        print(f"Top genres: {stats['top_genres']}")
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise
