#!/usr/bin/env python3
"""
NetflixFinder CLI - Command Line Interface for searching Netflix content.

This program provides an interactive interface to search for movies and series
using the NetflixFinder service with optional filters.
"""

import sys
import logging
from typing import Optional, List
from pathlib import Path

# Add the services directory to the path to import NetflixFinderService
sys.path.append(str(Path(__file__).parent / "services"))

from services.netflixFinder import NetflixFinderService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NetflixFinderCLI:
    """
    Command Line Interface for NetflixFinder service.
    
    Provides interactive prompts for search queries and filters.
    """
    
    def __init__(self):
        """Initialize the CLI with NetflixFinder service."""
        try:
            self.finder = NetflixFinderService()
            print("✅ NetflixFinder CLI initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing NetflixFinder service: {e}")
            sys.exit(1)
    
    def get_user_input(self, prompt: str, default: str = "") -> str:
        """
        Get user input with optional default value.
        
        Args:
            prompt: The prompt to show to the user
            default: Default value if user just presses Enter
            
        Returns:
            User input or default value
        """
        if default:
            user_input = input(f"{prompt} (default: {default}): ").strip()
            return user_input if user_input else default
        else:
            return input(f"{prompt}: ").strip()
    
    def get_optional_float(self, prompt: str) -> Optional[float]:
        """
        Get optional float input from user.
        
        Args:
            prompt: The prompt to show to the user
            
        Returns:
            Float value or None if user presses Enter
        """
        user_input = self.get_user_input(prompt)
        if not user_input:
            return None
        try:
            return float(user_input)
        except ValueError:
            print("❌ Invalid number format. Please enter a valid number.")
            return self.get_optional_float(prompt)
    
    def get_optional_int(self, prompt: str) -> Optional[int]:
        """
        Get optional integer input from user.
        
        Args:
            prompt: The prompt to show to the user
            
        Returns:
            Integer value or None if user presses Enter
        """
        user_input = self.get_user_input(prompt)
        if not user_input:
            return None
        try:
            return int(user_input)
        except ValueError:
            print("❌ Invalid number format. Please enter a valid integer.")
            return self.get_optional_int(prompt)
    
    def get_optional_list(self, prompt: str) -> Optional[List[str]]:
        """
        Get optional list input from user (comma-separated).
        
        Args:
            prompt: The prompt to show to the user
            
        Returns:
            List of strings or None if user presses Enter
        """
        user_input = self.get_user_input(prompt)
        if not user_input:
            return None
        # Split by comma and strip whitespace
        return [item.strip() for item in user_input.split(",") if item.strip()]
    
    def get_optional_date(self, prompt: str) -> Optional[str]:
        """
        Get optional date input from user (YYYY-MM-DD format).
        
        Args:
            prompt: The prompt to show to the user
            
        Returns:
            Date string or None if user presses Enter
        """
        user_input = self.get_user_input(prompt)
        if not user_input:
            return None
        # Basic date format validation
        if len(user_input) == 10 and user_input[4] == '-' and user_input[7] == '-':
            try:
                year, month, day = user_input.split('-')
                int(year), int(month), int(day)
                return user_input
            except ValueError:
                pass
        print("❌ Invalid date format. Please use YYYY-MM-DD format (e.g., 2020-01-15)")
        return self.get_optional_date(prompt)
    
    def collect_search_filters(self) -> dict:
        """
        Collect search filters from user through interactive prompts.
        
        Returns:
            Dictionary with search parameters
        """
        print("\n" + "="*60)
        print("🔍 SEARCH FILTERS")
        print("="*60)
        print("Press Enter to skip any filter (search all content)")
        print()
        
        filters = {}
        
        # Date range filters
        print("📅 DATE RANGE FILTERS:")
        filters['release_date_start'] = self.get_optional_date("Start date (YYYY-MM-DD)")
        filters['release_date_end'] = self.get_optional_date("End date (YYYY-MM-DD)")
        
        # Rating filters
        print("\n⭐ RATING FILTERS:")
        filters['vote_average_min'] = self.get_optional_float("Minimum vote average (0-10)")
        filters['vote_average_max'] = self.get_optional_float("Maximum vote average (0-10)")
        
        # Vote count filters
        print("\n📊 VOTE COUNT FILTERS:")
        filters['vote_count_min'] = self.get_optional_int("Minimum vote count")
        filters['vote_count_max'] = self.get_optional_int("Maximum vote count")
        
        # Popularity filters
        print("\n🔥 POPULARITY FILTERS:")
        filters['popularity_min'] = self.get_optional_float("Minimum popularity")
        filters['popularity_max'] = self.get_optional_float("Maximum popularity")
        
        # Genre filter
        print("\n🎭 GENRE FILTER:")
        print("Enter genres separated by commas (e.g., Action, Thriller, Drama)")
        filters['genres'] = self.get_optional_list("Genres")
        
        # Content type filter
        print("\n📺 CONTENT TYPE FILTER:")
        filters['content_type'] = self.get_user_input("Content type (movie/series)", "")
        if filters['content_type'] and filters['content_type'].lower() not in ['movie', 'series']:
            print("⚠️  Invalid content type. Using 'movie' as default.")
            filters['content_type'] = 'movie'
        
        # Number of results
        print("\n📋 RESULTS:")
        n_results_input = self.get_user_input("Number of results to show", "5")
        try:
            filters['n_results'] = int(n_results_input)
        except ValueError:
            print("⚠️  Invalid number. Using 5 as default.")
            filters['n_results'] = 5
        
        return filters
    
    def display_search_results(self, results: dict, query: str) -> None:
        """
        Display search results in a formatted way.
        
        Args:
            results: Search results from NetflixFinder service
            query: Original search query
        """
        print("\n" + "="*60)
        print(f"🎬 SEARCH RESULTS FOR: '{query}'")
        print("="*60)
        
        if not results['ids']:
            print("❌ No results found for your search criteria.")
            return
        
        print(f"✅ Found {len(results['ids'])} results\n")
        
        for i, (doc_id, doc, metadata, distance) in enumerate(zip(
            results['ids'], 
            results['documents'], 
            results['metadatas'], 
            results['distances']
        ), 1):
            print(f"🎯 RESULT {i} (Similarity: {(1-distance)*100:.1f}%)")
            print(f"   ID: {doc_id}")
            print(f"   Title: {metadata.get('title', 'N/A')}")
            print(f"   Original Title: {metadata.get('original_title', 'N/A')}")
            print(f"   Release Date: {metadata.get('release_date', 'N/A')}")
            print(f"   Rating: {metadata.get('vote_average', 'N/A')}/10 ({metadata.get('vote_count', 'N/A')} votes)")
            print(f"   Popularity: {metadata.get('popularity', 'N/A')}")
            print(f"   Genres: {metadata.get('genres', 'N/A')}")
            print(f"   Language: {metadata.get('original_language', 'N/A')}")
            print(f"   Overview: {metadata.get('overview', 'N/A')[:150]}...")
            if metadata.get('poster_url'):
                print(f"   Poster: {metadata.get('poster_url', 'N/A')}")
            print()
    
    def show_collection_stats(self) -> None:
        """Display collection statistics."""
        try:
            stats = self.finder.get_collection_stats()
            print("\n" + "="*60)
            print("📊 COLLECTION STATISTICS")
            print("="*60)
            print(f"Total documents: {stats['total_documents']}")
            print(f"Content types: {stats['content_types']}")
            print(f"Top genres: {stats['top_genres']}")
        except Exception as e:
            print(f"❌ Error getting collection stats: {e}")
    
    def run(self) -> None:
        """
        Main CLI loop.
        """
        print("🎬 NETFLIX FINDER CLI")
        print("="*60)
        print("Welcome to NetflixFinder! Search for movies and series with semantic search.")
        print("="*60)
        
        while True:
            try:
                # Get search query
                print("\n" + "="*60)
                query = self.get_user_input("What do you want to see?")
                
                if not query:
                    print("❌ Please enter a search query.")
                    continue
                
                # Collect filters
                filters = self.collect_search_filters()
                
                # Perform search
                print(f"\n🔍 Searching for: '{query}'")
                print("Please wait...")
                
                results = self.finder.search_content(
                    query=query,
                    n_results=filters['n_results'],
                    release_date_start=filters['release_date_start'],
                    release_date_end=filters['release_date_end'],
                    vote_average_min=filters['vote_average_min'],
                    vote_average_max=filters['vote_average_max'],
                    vote_count_min=filters['vote_count_min'],
                    vote_count_max=filters['vote_count_max'],
                    popularity_min=filters['popularity_min'],
                    popularity_max=filters['popularity_max'],
                    genres=filters['genres'],
                    content_type=filters['content_type']
                )
                
                # Display results
                self.display_search_results(results, query)
                
                # Ask if user wants to continue
                print("\n" + "="*60)
                continue_search = self.get_user_input("Search again? (y/n)", "y").lower()
                if continue_search not in ['y', 'yes', '']:
                    break
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error during search: {e}")
                continue_search = self.get_user_input("Try again? (y/n)", "y").lower()
                if continue_search not in ['y', 'yes', '']:
                    break
        
        # Show final statistics
        self.show_collection_stats()
        print("\n👋 Thanks for using NetflixFinder CLI!")

def main():
    """Main entry point for the CLI."""
    try:
        cli = NetflixFinderCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 