import os  # Import the os module to interact with the operating system
from dotenv import load_dotenv  # Import load_dotenv to load environment variables from a .env file
from pathlib import Path  # Import Path from pathlib to handle file system paths
import chromadb  # Import chromadb to interact with ChromaDB
from openai import OpenAI  # Import OpenAI to use the OpenAI API
from chromadb.utils import embedding_functions  # Import embedding_functions to use embedding utilities from ChromaDB

# Load environment variables from .env file
load_dotenv()  # Load environment variables from a .env file into the environment
openai_key = os.getenv("OPENAI_API_KEY")  # Get the OpenAI API key from environment variables

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai_key, model_name="text-embedding-3-small"
)  # Create an OpenAI embedding function using the API key and a specific model

current_file = Path(__file__).absolute()    # Get the absolute path of the current file
project_root = current_file.parent.parent  # Get the project root directory (two levels up)
chroma_db_path = project_root / "db" / "chroma_persist"  # Set the path for the ChromaDB persistent storage

if not chroma_db_path.exists():  # Check if the ChromaDB path exists
    print(f"ChromaDB path does not exist: {chroma_db_path}")  # Print an error message if the path does not exist
    raise FileNotFoundError(f"ChromaDB database not found at: {chroma_db_path}")  # Raise an error if the path does not exist

# Initialize the Chroma client with persistence
chroma_client = chromadb.PersistentClient(path=str(chroma_db_path))  # Create a persistent ChromaDB client using the specified path
collection_name = "document_qa_collection"  # Set the name for the collection
collection = chroma_client.get_or_create_collection(
    name=collection_name, embedding_function=openai_ef
)  # Get or create a collection in ChromaDB with the specified name and embedding function

client = OpenAI(api_key=openai_key)  # Create an OpenAI client using the API key


# =================================
# === For initial setup -- Uncomment (below) all for the first run, and then comment it all out ===
# =================================
# Function to load documents from a directory
def load_documents_from_directory(directory_path):
    print("==== Loading documents from directory ====")  # Print a message indicating documents are being loaded
    documents = []  # Initialize an empty list to store documents
    for filename in os.listdir(directory_path):  # Iterate over all files in the directory
        if filename.endswith(".txt"):  # Only process .txt files
            with open(
                os.path.join(directory_path, filename), "r", encoding="utf-8"
            ) as file:  # Open the file in read mode with UTF-8 encoding
                documents.append({"id": filename, "text": file.read()})  # Add the file content and filename as a document
    return documents  # Return the list of documents


# Function to split text into chunks
def split_text(text, chunk_size=1000, chunk_overlap=20):
    chunks = []  # Initialize an empty list to store text chunks
    start = 0  # Start index for chunking
    while start < len(text):  # Continue until the end of the text
        end = start + chunk_size  # Calculate the end index for the chunk
        chunks.append(text[start:end])  # Add the chunk to the list
        start = end - chunk_overlap  # Move the start index forward, with overlap
    return chunks  # Return the list of chunks


# Load documents from the directory
# Set the directory path for the documents
directory_path = current_file.parent / "data" / "new_articles"
documents = load_documents_from_directory(directory_path)  # Load documents from the specified directory

print(documents)
# # Split the documents into chunks
# chunked_documents = []  # Initialize an empty list to store chunked documents
# for doc in documents:  # Iterate over each document
#     chunks = split_text(doc["text"])  # Split the document text into chunks
#     print("==== Splitting docs into chunks ====")  # Print a message for splitting
#     for i, chunk in enumerate(chunks):  # Iterate over each chunk
#         chunked_documents.append({"id": f"{doc['id']}_chunk{i+1}", "text": chunk})  # Add the chunk with a unique id


# # Function to generate embeddings using OpenAI API
# def get_openai_embedding(text):
#     response = client.embeddings.create(input=text, model="text-embedding-3-small")  # Call the OpenAI API to get the embedding
#     embedding = response.data[0].embedding  # Extract the embedding from the response
#     print("==== Generating embeddings... ====")  # Print a message for generating embeddings
#     return embedding  # Return the embedding


# # Generate embeddings for the document chunks
# for doc in chunked_documents:  # Iterate over each chunked document
#     print("==== Generating embeddings... ====")  # Print a message for generating embeddings
#     doc["embedding"] = get_openai_embedding(doc["text"])  # Generate and store the embedding for the chunk


# # Upsert documents with embeddings into Chroma
# for doc in chunked_documents:  # Iterate over each chunked document
#     print("==== Inserting chunks into db;;; ====")  # Print a message for inserting into the database
#     collection.upsert(
#         ids=[doc["id"]], documents=[doc["text"]], embeddings=[doc["embedding"]]
#     )  # Upsert the chunk into the ChromaDB collection


# # === End of the initial setup -- Uncomment all for the first run, and then comment it all out ===
# # =================================


# # Function to query documents
# def query_documents(question, n_results=2):
#     # query_embedding = get_openai_embedding(question)
#     results = collection.query(query_texts=question, n_results=n_results)  # Query the collection for relevant documents using the question

#     # Extract the relevant chunks
#     relevant_chunks = [doc for sublist in results["documents"] for doc in sublist]  # Flatten the list of documents
#     print("==== Returning relevant chunks ====")  # Print a message for returning relevant chunks
#     return relevant_chunks  # Return the relevant chunks
#     # for idx, document in enumerate(results["documents"][0]):
#     #     doc_id = results["ids"][0][idx]
#     #     distance = results["distances"][0][idx]
#     #     print(f"Found document chunk: {document} (ID: {doc_id}, Distance: {distance})")


# # Function to generate a response from OpenAI
# def generate_response(question, relevant_chunks):
#     context = "\n\n".join(relevant_chunks)  # Join the relevant chunks to form the context
#     prompt = (
#         "You are an assistant for question-answering tasks. Use the following pieces of "
#         "retrieved context to answer the question. If you don't know the answer, say that you "
#         "don't know. Use three sentences maximum and keep the answer concise."
#         "\n\nContext:\n" + context + "\n\nQuestion:\n" + question
#     )  # Create the prompt for the OpenAI API

#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {
#                 "role": "system",
#                 "content": prompt,
#             },
#             {
#                 "role": "user",
#                 "content": question,
#             },
#         ],
#     )  # Call the OpenAI API to generate a response

#     answer = response.choices[0].message  # Extract the answer from the response
#     return answer  # Return the answer


# question = "give me a brief overview of the articles. Be concise, please."  # Set the question to ask
# relevant_chunks = query_documents(question)  # Query the collection for relevant chunks
# answer = generate_response(question, relevant_chunks)  # Generate a response using the relevant chunks

# print("==== Answer ====")  # Print a message indicating the answer is being printed
# print(answer.content)  # Print the answer content
