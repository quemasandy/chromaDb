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


def query_documents(question, n_results=2):
    results = collection.query(query_texts=question, n_results=n_results)

    relevant_chunks = [doc for sublist in results["documents"] for doc in sublist]
    print("==== Returning relevant chunks ====")
    return relevant_chunks


def generate_response(question, relevant_chunks):
    context = "\n\n".join(relevant_chunks)
    prompt = (
        "You are an assistant for question-answering tasks. Use the following pieces of "
        "retrieved context to answer the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the answer concise."
        "\n\nContext:\n" + context + "\n\nQuestion:\n" + question
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )  

    answer = response.choices[0].message  
    return answer  


question = "give me a brief overview of the articles. Be concise, please."
relevant_chunks = query_documents(question)
answer = generate_response(question, relevant_chunks)

print("==== Answer ====")
print(answer.content)
