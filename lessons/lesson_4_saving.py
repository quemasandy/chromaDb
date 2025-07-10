import chromadb  # Import the main ChromaDB library to interact with the vector database

from chromadb.utils import embedding_functions  # Import embedding utilities from ChromaDB

default_ef = embedding_functions.DefaultEmbeddingFunction()  # Create an instance of the default embedding function (not used explicitly here)
croma_client = chromadb.PersistentClient(path="./db/chroma_persist")  # Initialize a persistent ChromaDB client, storing data at the specified path

collection = croma_client.get_or_create_collection("my_story")  # Get or create a collection named 'my_story' to group related documents
# Define text documents
# List of dictionaries, each representing a document with an 'id' and 'text' field
# These documents will be stored in the collection
documents = [
    {"id": "doc1", "text": "Hello, world!"},  # Document 1: simple greeting
    {"id": "doc2", "text": "How are you today?"},  # Document 2: question
    {"id": "doc3", "text": "Goodbye, see you later!"},  # Document 3: farewell
    {
        "id": "doc4",
        "text": "Microsoft is a technology company that develops software. It was founded by Bill Gates and Paul Allen in 1975.",  # Document 4: factual information about Microsoft
    },
]

for doc in documents:  # Iterate over each document in the list
    collection.upsert(ids=doc["id"], documents=[doc["text"]])  # Insert or update the document in the collection using its id and text

# define a query text
# This is the text we will use to search for similar documents in the collection
query_text = "find document related to technology company"

results = collection.query(  # Perform a semantic search in the collection
    query_texts=[query_text],  # The query is provided as a list
    n_results=2,  # Retrieve the top 2 most similar documents
)

# Check if the query returned valid results (documents, ids, and distances)
if (
    results["documents"] and results["documents"][0]
    and results["ids"] and results["ids"][0]
    and results["distances"] and results["distances"][0]
):
    for idx, document in enumerate(results["documents"][0]):  # Iterate over each found document
        doc_id = results["ids"][0][idx]  # Get the document id
        distance = results["distances"][0][idx]  # Get the similarity distance
        print(
            f" For the query: {query_text}, \n Found similar document: {document} (ID: {doc_id}, Distance: {distance})"
        )  # Print the result: query, document text, id, and distance
else:
    print("No se encontraron documentos similares para la consulta.")  # Print a message if no similar documents were found
