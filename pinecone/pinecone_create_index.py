import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

pinecone_api_key = os.getenv("PINECONE_API_KEY")

pc = Pinecone(api_key=pinecone_api_key)

index_name = "developer-quickstart-py"

if not pc.has_index(index_name):
    print(f"Index {index_name} does not exist. Creating...")
    try:
        pc.create_index_for_model(
            name=index_name,
            cloud="aws",
            region="us-east-1",
            embed={
                "model": "llama-text-embed-v2",
                "field_map": {"text": "chunk_text"}
            }
        )
        print(f"Index {index_name} created successfully.")
    except Exception as e:
        print(f"Error creating index: {e}")
else:
    print(f"Index {index_name} already exists.")
