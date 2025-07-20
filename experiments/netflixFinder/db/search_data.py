import csv
import logging
import os
from dataclasses import dataclass, fields, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

import requests
from requests.exceptions import RequestException

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_KEY = os.getenv("TMDB_KEY")
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
MAX_RESULTS = 100
OUTPUT_CSV_FILE = Path(__file__).parent / "netflix_movies.csv"
NETFLIX_PROVIDER_ID = "8"
WATCH_REGION = "EC"
LANGUAGES = "en|es"

@dataclass(frozen=True)
class Movie:
    """
    Immutable class to store movie information.
    
    Attributes:
        id: Unique movie identifier in TMDB
        title: Movie title
        original_title: Original movie title
        overview: Movie description/synopsis
        release_date: Release date in YYYY-MM-DD format
        vote_average: Average rating (0-10)
        vote_count: Total number of votes
        popularity: TMDB popularity index
        original_language: Original language ISO code
        genres: Genres separated by commas
        poster_url: Complete poster URL
    """
    id: int
    title: str
    original_title: str
    overview: str
    release_date: str
    vote_average: float
    vote_count: int
    popularity: float
    original_language: str
    genres: str
    poster_url: str


class TMDBAPIError(Exception):
    """Custom exception for TMDB API errors."""
    pass


class TMDBClient:
    """
    Client to interact with TMDB API.
    
    Encapsulates all API communication logic and error handling.
    """
    
    def __init__(self, api_key: str, base_url: str = BASE_URL):
        """
        Initialize TMDB client.
        
        Args:
            api_key: TMDB API key
            base_url: API base URL (defaults to global constant)
        
        Raises:
            ValueError: If API key is empty
        """
        # Validate that API key is not empty before continuing
        if not api_key:
            raise ValueError("API key cannot be empty")
        
        self.api_key = api_key
        self.base_url = base_url
        # Create reusable HTTP session for better performance
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NetflixFinder/1.0',
            'Accept': 'application/json'
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make HTTP request to TMDB API.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Query string parameters
        
        Returns:
            API JSON response
            
        Raises:
            TMDBAPIError: If there's an HTTP request error
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        # Basic parameters included in all requests
        request_params = {"api_key": self.api_key}
        
        # If additional parameters are provided, add them
        if params:
            request_params.update(params)
        
        try:
            response = self.session.get(url, params=request_params, timeout=30)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            # If there's an error, log it and raise our custom exception
            logger.error(f"Error in request to {url}: {e}")
            raise TMDBAPIError(f"API Error: {e}") from e
    
    def fetch_genre_map(self) -> Dict[int, str]:
        """
        Get genre map from TMDB.
        
        Returns:
            Dictionary mapping genre IDs to names
        """
        # Log that we're starting genre retrieval
        logger.info("Getting genre map...")
        
        try:
            data = self._make_request("genre/movie/list")
            genres = data.get("genres", [])
            
            genre_map = {genre["id"]: genre["name"] for genre in genres}
            logger.info(f"Genre map obtained successfully: {len(genre_map)} genres")
            
            return genre_map
        except TMDBAPIError as e:
            # If there's an error, log it and return empty dictionary
            logger.error(f"Error getting genres: {e}")
            return {}
    
    def fetch_movies(self, genre_map: Dict[int, str], max_results: int = MAX_RESULTS) -> List[Movie]:
        """
        Get movies from TMDB discovery API.
        
        Args:
            genre_map: Map of genre IDs to names
            max_results: Maximum number of results to obtain
            
        Returns:
            List of Movie objects
            
        Raises:
            ValueError: If no API key is configured
        """
        if not self.api_key:
            raise ValueError("TMDB_KEY environment variable not configured")
        
        today = datetime.now()
        twelve_months_ago = today - timedelta(days=365)
        
        search_params = {
            "with_watch_providers": NETFLIX_PROVIDER_ID,
            "watch_region": WATCH_REGION,
            "with_original_language": LANGUAGES,
            "sort_by": "popularity.desc",
            "release_date.gte": twelve_months_ago.strftime('%Y-%m-%d'),
            "release_date.lte": today.strftime('%Y-%m-%d'),
            "page": 1
        }
        
        movies_data: List[Movie] = []
        logger.info(f"Starting movie search, target: {max_results} results")
        
        while len(movies_data) < max_results:
            try:
                data = self._make_request("discover/movie", search_params)
                results = data.get("results", [])
                
                if not results:
                    logger.info("No more results found")
                    break
                
                for movie_json in results:
                    if len(movies_data) >= max_results:
                        break
                    
                    movie = self._create_movie_from_json(movie_json, genre_map)
                    if movie:
                        movies_data.append(movie)
                
                if data["page"] < data["total_pages"]:
                    search_params["page"] += 1
                else:
                    logger.info("Reached last page of results")
                    break
                    
            except TMDBAPIError as e:
                logger.error(f"Error on page {search_params['page']}: {e}")
                break
        
        logger.info(f"Search completed: {len(movies_data)} movies found")
        return movies_data[:max_results]
    
    def _create_movie_from_json(self, movie_json: Dict, genre_map: Dict[int, str]) -> Optional[Movie]:
        """
        Create Movie object from API JSON data.
        
        Args:
            movie_json: Movie JSON data
            genre_map: Map of genre IDs to names
            
        Returns:
            Movie object or None if critical data is missing
        """
        try:
            genre_ids = movie_json.get("genre_ids", [])
            # Convert each genre ID to its name using the map
            genre_names = [genre_map.get(gid, "Unknown") for gid in genre_ids]
            
            poster_path = movie_json.get("poster_path")
            poster_url = f"{IMAGE_BASE_URL}{poster_path}" if poster_path else "N/A"
            
            movie_id = movie_json.get("id")
            if movie_id is None:
                logger.warning("Movie without valid ID, skipping...")
                return None
                
            return Movie(
                id=movie_id,
                title=movie_json.get("title", "No title"), 
                original_title=movie_json.get("original_title", "No title"), 
                overview=movie_json.get("overview", "No description"), 
                release_date=movie_json.get("release_date", "N/A"), 
                vote_average=movie_json.get("vote_average", 0.0), 
                vote_count=movie_json.get("vote_count", 0), 
                popularity=movie_json.get("popularity", 0.0), 
                original_language=movie_json.get("original_language", "N/A"), 
                genres=", ".join(genre_names), 
                poster_url=poster_url 
            )
        except (KeyError, TypeError) as e:
            logger.warning(f"Error processing movie {movie_json.get('id', 'unknown')}: {e}")
            return None


class MovieDataExporter:
    """
    Class to export movie data to different formats.
    """
    
    @staticmethod
    def save_to_csv(movies: List[Movie], filename: str | Path) -> None:
        """
        Save a list of movies to a CSV file.
        
        Args:
            movies: List of Movie objects
            filename: Output filename (can be string or Path)
            
        Raises:
            IOError: If there's an error writing the file
        """

        if not movies:
            logger.warning("No movies to save")
            return
        
        fieldnames = [field.name for field in fields(Movie)]
        
        try:
            # Convert filename to Path if it's a string
            output_path = Path(filename) if isinstance(filename, str) else filename
            # Create directory if it doesn't exist (mkdir -p equivalent)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "w", newline="", encoding="utf-8") as file:
                # Create CSV writer with field names
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                # Write header (first row with column names)
                writer.writeheader()
                
                for movie in movies:
                    # Convert Movie object to dictionary and write it
                    writer.writerow(asdict(movie))
            
            logger.info(f"Successfully saved {len(movies)} movies to {output_path}")
            
        except IOError as e:
            logger.error(f"Error saving CSV file {filename}: {e}")
            raise


def main() -> None:
    """
    Main function that executes the complete search and export flow.
    
    Raises:
        SystemExit: If there are critical execution errors
    """
    try:
        if not API_KEY:
            logger.error("TMDB_KEY environment variable not configured")
            raise SystemExit(1)
        
        client = TMDBClient(API_KEY)
        
        genre_map = client.fetch_genre_map()
        if not genre_map:
            genre_map = {}
        
        movies = client.fetch_movies(genre_map)
        
        MovieDataExporter.save_to_csv(movies, OUTPUT_CSV_FILE)
        
        logger.info("Process completed successfully")
        
    except (TMDBAPIError, IOError) as e:
        logger.error(f"Error during execution: {e}")
        raise SystemExit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise SystemExit(1)


# Only execute main() if this file is run directly (not if imported)
if __name__ == "__main__":
    main()
