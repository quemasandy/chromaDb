import os
from dotenv import load_dotenv
from pathlib import Path
import chromadb
from openai import OpenAI
from chromadb.utils import embedding_functions

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai_key, model_name="text-embedding-3-small"
)

current_file = Path(__file__).absolute()
project_root = current_file.parent.parent
chroma_db_path = project_root / "db" / "chroma_persist"

if not chroma_db_path.exists():
    print(f"ChromaDB path does not exist: {chroma_db_path}")
    raise FileNotFoundError(f"ChromaDB database not found at: {chroma_db_path}")

chroma_client = chromadb.PersistentClient(path=str(chroma_db_path))
collection_name = "document_qa_collection"
collection = chroma_client.get_or_create_collection(
    name=collection_name, embedding_function=openai_ef
)

client = OpenAI(api_key=openai_key)

def load_documents_from_directory(directory_path):
    print("==== Loading documents from directory ====")
    documents = []  
    for filename in os.listdir(directory_path):  
        if filename.endswith(".txt"):  
            with open(
                os.path.join(directory_path, filename), "r", encoding="utf-8"
            ) as file:  
                documents.append({"id": filename, "text": file.read()})  
    return documents  


def split_text(text, chunk_size=1000, chunk_overlap=20):
    chunks = []  
    start = 0  
    while start < len(text):  
        end = start + chunk_size  
        chunks.append(text[start:end])  
        start = end - chunk_overlap  
    return chunks  


directory_path = current_file.parent / "data" / "new_articles"
documents = load_documents_from_directory(directory_path)

print(documents)

chunked_documents = []
for doc in documents: 
    chunks = split_text(doc["text"])
    print("==== Splitting docs into chunks ====")
    for i, chunk in enumerate(chunks):
        chunked_documents.append({"id": f"{doc['id']}_chunk{i+1}", "text": chunk})

def get_openai_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    embedding = response.data[0].embedding
    print("==== Generating embeddings... ====")
    return embedding


for doc in chunked_documents:
    print("==== Generating embeddings... ====")
    doc["embedding"] = get_openai_embedding(doc["text"])


for doc in chunked_documents:
    print("==== Inserting chunks into db;;; ====")
    collection.upsert(
        ids=[doc["id"]], documents=[doc["text"]], embeddings=[doc["embedding"]]
    )
