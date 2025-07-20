#!/bin/bash

# NetflixFinder CLI Runner
# This script activates the virtual environment and runs the CLI

echo "🎬 NetflixFinder CLI"
echo "===================="

# Check if virtual environment exists
if [ ! -d "../../venv" ]; then
    echo "❌ Virtual environment not found. Please run:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ../../venv/bin/activate

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import chromadb, openai, dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Please install:"
    echo "   pip install chromadb openai python-dotenv"
    exit 1
fi

# Check if .env file exists
if [ ! -f "../../.env" ]; then
    echo "❌ .env file not found. Please create one with:"
    echo "   OPENAI_API_KEY=your_openai_api_key_here"
    exit 1
fi

# Run the CLI
echo "🚀 Starting NetflixFinder CLI..."
echo "================================"
python3 cli_search.py 