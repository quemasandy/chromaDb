# NetflixFinder CLI

A command-line interface for searching Netflix content using semantic search with ChromaDB.

## 🚀 Quick Start

### Option 1: Using the runner script (Recommended)
```bash
cd experiments/netflixFinder
./run_cli.sh
```

### Option 2: Manual execution
```bash
cd experiments/netflixFinder
source ../venv/bin/activate
python3 cli_search.py
```

## 📋 Prerequisites

1. **Virtual Environment**: Make sure you have the virtual environment activated
2. **Dependencies**: Install required packages
3. **Environment Variables**: Set up your `.env` file with OpenAI API key
4. **Data**: Ensure the ChromaDB collection is populated with movie data

## 🎯 How to Use

### 1. Start the CLI
The program will ask: **"What do you want to see?"**

Enter your search query in natural language, for example:
- "I want an action movie with samurais"
- "romantic comedy about love"
- "sci-fi movie with robots"

### 2. Configure Filters (Optional)
After entering your query, the CLI will ask for various filters. **Press Enter to skip any filter** and search all content:

#### 📅 Date Range Filters
- **Start date**: Enter in YYYY-MM-DD format (e.g., 2020-01-15)
- **End date**: Enter in YYYY-MM-DD format (e.g., 2023-12-31)

#### ⭐ Rating Filters
- **Minimum vote average**: Enter a number between 0-10
- **Maximum vote average**: Enter a number between 0-10

#### 📊 Vote Count Filters
- **Minimum vote count**: Enter minimum number of votes
- **Maximum vote count**: Enter maximum number of votes

#### 🔥 Popularity Filters
- **Minimum popularity**: Enter minimum popularity score
- **Maximum popularity**: Enter maximum popularity score

#### 🎭 Genre Filter
- **Genres**: Enter genres separated by commas (e.g., Action, Thriller, Drama)

#### 📺 Content Type Filter
- **Content type**: Enter "movie" or "series"

#### 📋 Results
- **Number of results**: Enter how many results to show (default: 5)

### 3. View Results
The CLI will display:
- Movie/Series title and original title
- Release date and rating
- Genres and language
- Overview (first 150 characters)
- Similarity percentage
- Poster URL (if available)

### 4. Continue or Exit
After viewing results, you can:
- Search again with new criteria
- Exit the program

## 🔧 Features

### ✅ Semantic Search
- Search using natural language
- Find content based on meaning, not just keywords

### ✅ Flexible Filtering
- Apply multiple filters or none at all
- Skip any filter by pressing Enter

### ✅ Rich Results
- Detailed movie information
- Similarity scores
- Multiple metadata fields

### ✅ User-Friendly Interface
- Clear prompts and instructions
- Error handling and validation
- Colorful emoji indicators

## 📁 File Structure

```
netflixFinder/
├── cli_search.py          # Main CLI application
├── run_cli.sh            # Runner script
├── README.md             # This file
├── services/
│   └── netflixFinder.py  # NetflixFinder service
└── db/
    ├── load_data_to_chroma.py  # Data loading script
    └── netflix_movies.csv      # Movie data
```

## 🛠️ Troubleshooting

### Error: "Virtual environment not found"
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "Missing dependencies"
```bash
pip install chromadb openai python-dotenv
```

### Error: ".env file not found"
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Error: "Collection expecting embedding with dimension..."
The collection was created with a different embedding model. You may need to:
1. Delete the existing collection
2. Reload data with the correct model
3. Or update the service to use the same model as the collection

## 🎬 Example Usage

```
🎬 NETFLIX FINDER CLI
============================================================
Welcome to NetflixFinder! Search for movies and series with semantic search.
============================================================

============================================================
What do you want to see?: I want an action movie with samurais

============================================================
🔍 SEARCH FILTERS
============================================================
Press Enter to skip any filter (search all content)

📅 DATE RANGE FILTERS:
Start date (YYYY-MM-DD): 
End date (YYYY-MM-DD): 

⭐ RATING FILTERS:
Minimum vote average (0-10): 6.0
Maximum vote average (0-10): 

📊 VOTE COUNT FILTERS:
Minimum vote count: 
Maximum vote count: 

🔥 POPULARITY FILTERS:
Minimum popularity: 
Maximum popularity: 

🎭 GENRE FILTER:
Enter genres separated by commas (e.g., Action, Thriller, Drama)
Genres: Action, Drama

📺 CONTENT TYPE FILTER:
Content type (movie/series): movie

📋 RESULTS:
Number of results to show (default: 5): 3

🔍 Searching for: 'I want an action movie with samurais'
Please wait...

============================================================
🎬 SEARCH RESULTS FOR: 'I want an action movie with samurais'
============================================================
✅ Found 3 results

🎯 RESULT 1 (Similarity: 85.2%)
   ID: 12345
   Title: The Last Samurai
   Original Title: The Last Samurai
   Release Date: 2003-12-05
   Rating: 7.7/10 (1234 votes)
   Popularity: 45.2
   Genres: Action, Drama, History
   Language: en
   Overview: An American military advisor embraces the Samurai culture he was hired to destroy...
```

## 🚀 Advanced Usage

### Batch Processing
You can modify the CLI to process multiple queries or integrate it with other scripts.

### Custom Filters
The service supports additional filters that can be added to the CLI interface.

### Export Results
Results can be exported to CSV or JSON format for further analysis.

## 📝 Notes

- The CLI uses the same NetflixFinder service as other applications
- All searches are performed against the ChromaDB collection
- Results are ranked by semantic similarity
- The service supports both movies and series (though current data is movies only) 