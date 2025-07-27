# Import standard library modules first for environment and path management
import os  # Permite la gestión de variables de entorno y operaciones del sistema de archivos
from pathlib import Path  # Permite la manipulación de rutas de archivos de manera orientada a objetos

# Import third-party libraries for environment variable loading
from dotenv import load_dotenv  # Permite cargar variables de entorno desde un archivo .env

# Import Pinecone client and serverless specification for vector database operations
from pinecone import Pinecone, ServerlessSpec  # Permite la interacción con la base de datos vectorial Pinecone y la configuración serverless

# Import LangChain modules for LLM, embeddings, and prompt management
from langchain_openai import ChatOpenAI  # Permite la interacción con modelos de lenguaje de OpenAI
from langchain_openai import OpenAIEmbeddings  # Permite la generación de embeddings usando OpenAI

# Import LangChain modules for document loading and splitting
from langchain_community.document_loaders import DirectoryLoader  # Permite cargar documentos desde un directorio
from langchain_community.document_loaders import TextLoader  # Permite cargar archivos de texto individuales
from langchain_text_splitters import RecursiveCharacterTextSplitter  # Permite dividir documentos en fragmentos de texto

# Import LangChain modules for vector store and retrieval chains
from langchain_community.vectorstores import Chroma  # Permite el almacenamiento y recuperación de vectores usando Chroma
from langchain_core.prompts import ChatPromptTemplate  # Permite la creación de plantillas de prompts para chat
from langchain.chains.combine_documents import create_stuff_documents_chain  # Permite combinar documentos para cadenas de procesamiento
from langchain.chains import create_retrieval_chain  # Permite crear cadenas de recuperación de información
from langchain_pinecone import PineconeVectorStore  # Permite integrar Pinecone con LangChain para almacenamiento vectorial

# Load environment variables from .env file
load_dotenv()  # Carga las variables de entorno desde el archivo .env

# Get the absolute path of the current file and determine project root
current_file = Path(__file__).absolute()  # Obtiene la ruta absoluta del archivo actual
project_root = current_file.parent  # Define el directorio padre como la raíz del proyecto

# Extract API keys from environment variables
openai_key = os.getenv("OPENAI_API_KEY")  # Obtiene la clave de API de OpenAI desde las variables de entorno
pinecone_key = os.getenv("PINCONE_API_KEY")  # Obtiene la clave de API de Pinecone desde las variables de entorno

# Initialize OpenAI language model for text generation
llm = ChatOpenAI(api_key=openai_key, model="gpt-4")  # Crea una instancia del modelo GPT-4 para generar respuestas
# Initialize Pinecone client for vector database operations
pinecone = Pinecone(api_key=pinecone_key)  # Crea una instancia del cliente Pinecone para operaciones de base de datos vectorial

# Load documents from the specified directory
loader = DirectoryLoader(
    path=project_root / "data" / "new_articles",  # Define la ruta donde están los documentos de texto
    glob="*.txt",  # Especifica que solo cargue archivos con extensión .txt
    loader_cls=TextLoader  # Usa TextLoader para cargar archivos de texto
)
document = loader.load()  # Carga todos los documentos encontrados en el directorio especificado

# Split text documents into smaller chunks for better processing
text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n"],  # Define los separadores para dividir el texto (doble salto de línea y salto de línea)
    chunk_size=1000,  # Define el tamaño máximo de cada fragmento en caracteres
    chunk_overlap=20,  # Define el solapamiento entre fragmentos para mantener contexto
)
documents_chunks = text_splitter.split_documents(document)  # Divide los documentos en fragmentos más pequeños
print(f"Number of documents chunks: {len(documents_chunks)}")  # Imprime el número total de fragmentos creados

# Initialize OpenAI embeddings model for converting text to vectors
embedding = OpenAIEmbeddings(api_key=openai_key, model="text-embedding-3-small")  # Crea una instancia del modelo de embeddings de OpenAI

# Define the name for the Pinecone index
index_name = "developer-quickstart-py"  # Define el nombre del índice en Pinecone
# Get list of existing indexes from Pinecone
eixsting_indexes = [index_info["name"] for index_info in pinecone.list_indexes()]  # Obtiene la lista de índices existentes en Pinecone

# Create Pinecone index if it doesn't exist
if index_name not in eixsting_indexes:  # Verifica si el índice ya existe
    pinecone.create_index(
        name=index_name,  # Nombre del índice a crear
        dimension=1536,  # Dimensión de los vectores (debe coincidir con el modelo de embeddings)
        metric="cosine",  # Métrica de similitud a usar (coseno)
        spec=ServerlessSpec(
            cloud="aws",  # Proveedor de nube (AWS)
            region="us-east-1",  # Región de AWS donde se creará el índice
        ),
    )

# Get reference to the Pinecone index
index = pinecone.Index(index_name)  # Obtiene una referencia al índice de Pinecone

# Create Pinecone vector store and populate it with document embeddings
docsearch = PineconeVectorStore.from_documents(
    documents=documents_chunks,  # Fragmentos de documentos a procesar
    embedding=embedding,  # Modelo de embeddings para convertir texto a vectores
    index_name=index_name  # Nombre del índice donde se almacenarán los vectores
)

# Example query (commented out)
# query = "tell me about writers strike"  # Consulta de ejemplo
# docs = docsearch.similarity_search(query)  # Busca documentos similares a la consulta
# print(docs[0].page_content)  # Imprime el contenido del primer documento encontrado

# Create a retriever for document retrieval
retriever = docsearch.as_retriever()  # Convierte el vector store en un retriever para búsquedas

# Define the system prompt for the language model
system_prompt = (
    "You are an assistant for question-answering tasks. "  # Define el rol del asistente
    "Use the following pieces of retrieved context to answer "  # Instrucción para usar el contexto recuperado
    "the question. If you don't know the answer, say that you "  # Instrucción para admitir cuando no sabe la respuesta
    "don't know. Use three sentences maximum and keep the "  # Limitación de longitud de respuesta
    "answer concise."  # Instrucción para mantener la respuesta concisa
    "\n\n"  # Separador entre instrucciones y contexto
    "{context}"  # Placeholder para el contexto que se insertará
)

# Create a chat prompt template with system and human messages
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),  # Define el mensaje del sistema con las instrucciones
        ("human", "{input}"),  # Define el mensaje del usuario con placeholder para la pregunta
    ]
)

# Create a chain that combines documents with the language model
question_answer_chain = create_stuff_documents_chain(
    llm=llm,  # Modelo de lenguaje a usar
    prompt=prompt,  # Plantilla de prompt a usar
)

# Create a RAG (Retrieval-Augmented Generation) chain
rag_chain = create_retrieval_chain(retriever, question_answer_chain)  # Combina el retriever con la cadena de respuesta

# Invoke the RAG chain with a specific question
response = rag_chain.invoke({"input": "tell me more about AI and ML news"})  # Ejecuta la cadena RAG con una pregunta específica
res = response["answer"]  # Extrae la respuesta del resultado de la cadena

print(res)  # Imprime la respuesta generada por el modelo

# Commented line for deleting the index (uncomment to delete)
# pc.delete_index(index_name) ===> To delete the index  # Comando para eliminar el índice (comentado para evitar eliminación accidental)
