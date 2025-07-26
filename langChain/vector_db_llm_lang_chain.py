# Import required libraries for environment variables management
import os
# Import dotenv to load environment variables from .env file
from dotenv import load_dotenv

# Import OpenAI's chat model for generating responses
from langchain_openai import ChatOpenAI
# Import OpenAI's embeddings model for converting text to vectors
from langchain_openai import OpenAIEmbeddings

# Import prompt template for creating structured prompts
from langchain_core.prompts import ChatPromptTemplate
# Import function to create retrieval chain for RAG (Retrieval Augmented Generation)
from langchain.chains import create_retrieval_chain
# Import function to create document combination chain
from langchain.chains.combine_documents import create_stuff_documents_chain
# Import text splitter to break large documents into smaller chunks
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Import Chroma vector database for storing and retrieving embeddings
from langchain_community.vectorstores import Chroma
# Import text loader for loading individual text files
from langchain_community.document_loaders import TextLoader
# Import directory loader for loading multiple files from a directory
from langchain_community.document_loaders import DirectoryLoader

# Load environment variables from .env file into the environment
load_dotenv()

# Get OpenAI API key from environment variables for authentication
openai_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI's GPT-4 chat model with the API key
model = ChatOpenAI(api_key=openai_key, model="gpt-4")

# Load documents from the specified directory containing .txt files
loader = DirectoryLoader(
    path="./data/new_articles/", glob="*.txt", loader_cls=TextLoader
)

# Load all documents from the directory into a list of Document objects
document = loader.load()
# Print the loaded documents to verify they were loaded correctly
print(document)

# Create a text splitter to break large documents into smaller chunks for better processing
text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n"],  # Split on double newlines and single newlines
    chunk_size=1000,  # Maximum size of each chunk in characters
    chunk_overlap=20,  # Number of characters to overlap between chunks for context
)
# Split the loaded documents into smaller chunks for better embedding generation
documents = text_splitter.split_documents(document)
# Print the number of document chunks created for verification
print(f"Number of documents: {len(documents)}")

# Initialize OpenAI's embedding model to convert text into vector representations
embedding = OpenAIEmbeddings(
    api_key=openai_key, model="text-embedding-3-small")

# Define the directory where ChromaDB will persist the vector database
persits_directory = "./db/chroma_db_real_world"
# Create a Chroma vector database from the document chunks and embeddings
vectordb = Chroma.from_documents(
    documents=documents, embedding=embedding, persist_directory=persits_directory
)  # This will create the Chroma object and persist the embeddings to the directory

# Create a retriever object from the vector database for similarity search
retriever = vectordb.as_retriever()

# Example of how to query the retriever (commented out for demonstration)
# res_docs = retriever.invoke("how much did microsoft raise?", k=2)
# print(res_docs)

# Define the system prompt that instructs the AI how to respond to questions
system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"  # Placeholder for the retrieved context
)

# Create a chat prompt template with system and human messages
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),  # System message with instructions
        ("human", "{input}"),  # Human message placeholder for the question
    ]
)

# Create a chain that combines documents and generates answers using the LLM
question_answer_chain = create_stuff_documents_chain(
    llm=model,  # Use the initialized GPT-4 model
    prompt=prompt,  # Use the defined prompt template
)

# Create a RAG (Retrieval Augmented Generation) chain that combines retrieval and answer generation
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# Invoke the RAG chain with a specific question about Databricks news
response = rag_chain.invoke({"input": "talk about databricks news"})
# Extract the answer from the response dictionary
res = response["answer"]

# Print the generated answer to the console
print(res)  # This will print the answer to the question
