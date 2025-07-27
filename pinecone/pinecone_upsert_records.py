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

# Upsert records into a namespace
# `chunk_text` fields are converted to sparse vectors
# `category` and `quarter` fields are stored as metadata
index.upsert_records(
    "example-namespace",
    [
        {
            "_id": "vec1",
            "chunk_text": "AAPL reported a year-over-year revenue increase, expecting stronger Q3 demand for its flagship phones.",
            "category": "technology",
            "quarter": "Q3"
        },
        {
            "_id": "vec2",
            "chunk_text": "Analysts suggest that AAPL'\''s upcoming Q4 product launch event might solidify its position in the premium smartphone market.",
            "category": "technology",
            "quarter": "Q4"
        },
        {
            "_id": "vec3",
            "chunk_text": "AAPL'\''s strategic Q3 partnerships with semiconductor suppliers could mitigate component risks and stabilize iPhone production.",
            "category": "technology",
            "quarter": "Q3"
        },
        {
            "_id": "vec4",
            "chunk_text": "AAPL may consider healthcare integrations in Q4 to compete with tech rivals entering the consumer wellness space.",
            "category": "technology",
            "quarter": "Q4"
        }
    ]
)

time.sleep(10)  # Wait for the upserted vectors to be indexed
