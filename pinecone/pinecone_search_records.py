from pinecone import Pinecone
import os
import time
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

pinecone_api_key = os.getenv("PINECONE_API_KEY")

pc = Pinecone(api_key=pinecone_api_key)

index_name = "developer-quickstart-py"

index = pc.Index(index_name)

results = index.search(
    namespace="example-namespace",
    query={
        "inputs": {"text": "Disease prevention"},
        "top_k": 2
    },
    fields=["category", "chunk_text", "quarter"]
)

print(results)
