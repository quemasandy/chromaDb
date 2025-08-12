# Importamos utilidades auxiliares para formateo de texto y carga de ChromaDB
from helper_utils import word_wrap, load_chroma
# Importamos PdfReader para leer archivos PDF
from pypdf import PdfReader
# Importamos os para operaciones del sistema operativo
import os
# Importamos OpenAI para usar modelos de lenguaje
from openai import OpenAI
# Importamos dotenv para cargar variables de entorno
from dotenv import load_dotenv

# Importamos PdfReader nuevamente (redundante, se puede eliminar)
from pypdf import PdfReader
# Importamos numpy para operaciones matemáticas
import numpy as np

# Importamos PyPDFLoader de langchain para cargar PDFs
from langchain_community.document_loaders import PyPDFLoader

# Cargamos las variables de entorno desde el archivo .env
load_dotenv()

# Obtenemos la clave API de OpenAI desde las variables de entorno
openai_key = os.getenv("OPENAI_API_KEY")
# Creamos un cliente de OpenAI con la clave API
client = OpenAI(api_key=openai_key)

# Importamos chromadb para la base de datos vectorial
import chromadb
# Importamos SentenceTransformerEmbeddingFunction para generar embeddings
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# Creamos una función de embedding usando SentenceTransformers
embedding_function = SentenceTransformerEmbeddingFunction()

# Obtenemos la ruta absoluta del archivo actual
absolute_path = os.path.abspath(__file__)
# Obtenemos el directorio padre del archivo actual
parent_dir = os.path.dirname(absolute_path)
# Creamos un lector PDF para el archivo del reporte anual de Microsoft
reader = PdfReader(os.path.join(parent_dir, "data", "microsoft-annual-report.pdf"))
# Extraemos el texto de cada página del PDF y eliminamos espacios en blanco
pdf_texts = [p.extract_text().strip() for p in reader.pages]

# Filtramos las cadenas vacías del texto extraído
pdf_texts = [text for text in pdf_texts if text]

# Importamos los splitters de texto de langchain
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)

# Creamos un splitter de caracteres recursivo que divide el texto en chunks de 1000 caracteres
character_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", ". ", " ", ""], chunk_size=1000, chunk_overlap=0
)
# Dividimos el texto del PDF en chunks usando el splitter de caracteres
character_split_texts = character_splitter.split_text("\n\n".join(pdf_texts))

# Creamos un splitter de tokens que divide el texto en chunks de 256 tokens
token_splitter = SentenceTransformersTokenTextSplitter(
    chunk_overlap=0, tokens_per_chunk=256
)

# Lista para almacenar los textos divididos por tokens
token_split_texts = []
# Iteramos sobre cada chunk de caracteres y los dividimos en tokens
for text in character_split_texts:
    token_split_texts += token_splitter.split_text(text)

# Creamos un cliente de ChromaDB
chroma_client = chromadb.Client()
# Creamos o obtenemos una colección llamada "microsoft-collect" con la función de embedding
chroma_collection = chroma_client.get_or_create_collection(
    "microsoft-collect", embedding_function=embedding_function
)

# Creamos IDs únicos para cada documento basados en su índice
ids = [str(i) for i in range(len(token_split_texts))]

# Agregamos los documentos a la colección de ChromaDB con sus IDs
chroma_collection.add(ids=ids, documents=token_split_texts)

# Obtenemos el número total de documentos en la colección
count = chroma_collection.count()

# Definimos una consulta de ejemplo sobre inversión en investigación y desarrollo
query = "What has been the investment in research and development?"

# Realizamos una búsqueda en la colección con la consulta
results = chroma_collection.query(
    query_texts=query, n_results=10, include=["documents", "embeddings"]
)

# Extraemos los documentos recuperados de los resultados
retrieved_documents = results["documents"][0]

# Imprimimos cada documento recuperado con formato de envoltura de palabras
for document in results["documents"][0]:
    print(word_wrap(document))
    print("")

# Importamos CrossEncoder para reranking de documentos
from sentence_transformers import CrossEncoder

# Creamos un modelo CrossEncoder para reranking usando el modelo ms-marco-MiniLM-L-6-v2
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# Creamos pares de consulta-documento para el reranking
pairs = [[query, doc] for doc in retrieved_documents]
# Calculamos las puntuaciones de relevancia para cada par usando el CrossEncoder
scores = cross_encoder.predict(pairs)

# Imprimimos las puntuaciones obtenidas
print("Scores:")
for score in scores:
    print(score)

# Imprimimos el nuevo ordenamiento basado en las puntuaciones (orden descendente)
print("New Ordering:")
for o in np.argsort(scores)[::-1]:
    print(o + 1)

# Definimos una consulta original sobre factores que contribuyeron al aumento de ingresos
original_query = (
    "What were the most important factors that contributed to increases in revenue?"
)

# Generamos consultas adicionales relacionadas con la consulta original (query expansion)
generated_queries = [
    "What were the major drivers of revenue growth?",
    "Were there any new product launches that contributed to the increase in revenue?",
    "Did any changes in pricing or promotions impact the revenue growth?",
    "What were the key market trends that facilitated the increase in revenue?",
    "Did any acquisitions or partnerships contribute to the revenue growth?",
]

# Concatenamos la consulta original con las consultas generadas
queries = [original_query] + generated_queries

# Realizamos búsquedas múltiples con todas las consultas
results = chroma_collection.query(
    query_texts=queries, n_results=10, include=["documents", "embeddings"]
)
# Extraemos todos los documentos recuperados
retrieved_documents = results["documents"]

# Eliminamos documentos duplicados usando un conjunto
unique_documents = set()
for documents in retrieved_documents:
    for document in documents:
        unique_documents.add(document)

# Convertimos el conjunto de documentos únicos de vuelta a una lista
unique_documents = list(unique_documents)

# Creamos pares de consulta-documento para el reranking con la consulta original
pairs = []
for doc in unique_documents:
    pairs.append([original_query, doc])

# Calculamos las puntuaciones de relevancia para cada par
scores = cross_encoder.predict(pairs)

# Imprimimos las puntuaciones obtenidas
print("Scores:")
for score in scores:
    print(score)

# Imprimimos el nuevo ordenamiento basado en las puntuaciones
print("New Ordering:")
for o in np.argsort(scores)[::-1]:
    print(o)

# ====
# Seleccionamos los 5 documentos con mayor puntuación
top_indices = np.argsort(scores)[::-1][:5]
# Extraemos los documentos top basados en los índices
top_documents = [unique_documents[i] for i in top_indices]

# Concatenamos los documentos top en un solo contexto separado por dobles saltos de línea
context = "\n\n".join(top_documents)

# Función para generar respuestas usando múltiples consultas
def generate_multi_query(query, context, model="gpt-3.5-turbo"):
    # Definimos el prompt del sistema para el asistente
    prompt = f"""
    You are a knowledgeable financial research assistant. 
    Your users are inquiring about an annual report. 
    """

    # Creamos los mensajes para la API de OpenAI
    messages = [
        {
            "role": "system",
            "content": prompt,
        },
        {
            "role": "user",
            "content": f"based on the following context:\n\n{context}\n\nAnswer the query: '{query}'",
        },
    ]

    # Realizamos la llamada a la API de OpenAI para generar la respuesta
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    # Extraemos el contenido de la respuesta
    content = response.choices[0].message.content
    # Dividimos el contenido en líneas
    content = content.split("\n")
    return content

# Generamos la respuesta final usando la consulta original y el contexto
res = generate_multi_query(query=original_query, context=context)
# Imprimimos la respuesta final
print("Final Answer:")
print(res)
