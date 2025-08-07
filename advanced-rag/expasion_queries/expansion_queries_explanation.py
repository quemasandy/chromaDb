# Importamos utilidades auxiliares para proyección de embeddings y formateo de texto
from helper_utils import project_embeddings, word_wrap
# Importamos PdfReader para leer archivos PDF
from pypdf import PdfReader
# Importamos os para operaciones del sistema de archivos
import os
# Importamos OpenAI para usar modelos de lenguaje
from openai import OpenAI
# Importamos dotenv para cargar variables de entorno desde archivo .env
from dotenv import load_dotenv

# Importamos librerías para procesamiento de datos y visualización
from pypdf import PdfReader
import numpy as np
import umap

# Cargamos las variables de entorno desde el archivo .env
load_dotenv()

# Obtenemos la clave API de OpenAI desde las variables de entorno
openai_key = os.getenv("OPENAI_API_KEY")
# Creamos una instancia del cliente de OpenAI usando la clave API
client = OpenAI(api_key=openai_key)

# Obtenemos la ruta del directorio actual donde está este script
root_dir = os.path.dirname(os.path.abspath(__file__))
# Construimos la ruta completa al archivo PDF del reporte anual de Microsoft
pdf_path = os.path.join(root_dir, "data", "microsoft-annual-report.pdf")
# Creamos un lector de PDF para el archivo especificado
reader = PdfReader(pdf_path)
# Extraemos el texto de cada página del PDF y eliminamos espacios en blanco
pdf_texts = [p.extract_text().strip() for p in reader.pages]

# Filtramos las cadenas vacías para eliminar páginas sin contenido
pdf_texts = [text for text in pdf_texts if text]

# Importamos los separadores de texto de LangChain
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)

# Creamos un separador de caracteres recursivo que divide el texto en chunks de 1000 caracteres
# Usa múltiples separadores en orden de preferencia: saltos de línea dobles, simples, puntos, espacios
character_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", ". ", " ", ""], chunk_size=1000, chunk_overlap=0
)
# Dividimos todo el texto del PDF en chunks usando el separador de caracteres
character_split_texts = character_splitter.split_text("\n\n".join(pdf_texts))

# Creamos un separador basado en tokens para dividir el texto en chunks de 256 tokens
token_splitter = SentenceTransformersTokenTextSplitter(
    chunk_overlap=0, tokens_per_chunk=256
)

# Inicializamos una lista vacía para almacenar los textos divididos por tokens
token_split_texts = []
# Iteramos sobre cada chunk de caracteres y los dividimos en chunks de tokens
for text in character_split_texts:
    token_split_texts += token_splitter.split_text(text)

# Importamos ChromaDB y la función de embedding de SentenceTransformer
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# Creamos una función de embedding usando el modelo SentenceTransformer
embedding_function = SentenceTransformerEmbeddingFunction()
# Comentario: línea para probar la función de embedding (comentada)
# print(embedding_function([token_split_texts[10]]))

# Creamos una instancia del cliente de ChromaDB
chroma_client = chromadb.Client()
# Creamos una colección llamada "microsoft-collection" con la función de embedding especificada
chroma_collection = chroma_client.create_collection(
    "microsoft-collection", embedding_function=embedding_function
)

# Generamos IDs únicos para cada documento basados en su índice
ids = [str(i) for i in range(len(token_split_texts))]

# Agregamos todos los documentos a la colección de ChromaDB con sus IDs correspondientes
chroma_collection.add(ids=ids, documents=token_split_texts)
# Contamos cuántos documentos hay en la colección
chroma_collection.count()

# Definimos una consulta de ejemplo para buscar información sobre ingresos
query = "What was the total revenue for the year?"

# Realizamos una búsqueda en la colección usando la consulta, obteniendo 5 resultados
results = chroma_collection.query(query_texts=[query], n_results=5)
# Extraemos los documentos recuperados del primer (y único) resultado de consulta
retrieved_documents = results["documents"][0]

# Comentario: código para mostrar los documentos recuperados (comentado)
# for document in retrieved_documents:
#     print(word_wrap(document))
#     print("\n")

# Definimos una función para generar múltiples consultas relacionadas usando GPT
def generate_multi_query(query, model="gpt-3.5-turbo"):
    # Definimos el prompt del sistema que le dice al modelo qué hacer
    prompt = """
    You are a knowledgeable financial research assistant. 
    Your users are inquiring about an annual report. 
    For the given question, propose up to five related questions to assist them in finding the information they need. 
    Provide concise, single-topic questions (withouth compounding sentences) that cover various aspects of the topic. 
    Ensure each question is complete and directly related to the original inquiry. 
    List each question on a separate line without numbering.
                """

    # Creamos la lista de mensajes para la conversación con el modelo
    messages = [
        {
            "role": "system",
            "content": prompt,
        },
        {"role": "user", "content": query},
    ]

    # Realizamos la llamada a la API de OpenAI para generar las consultas expandidas
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    # Extraemos el contenido de la respuesta
    content = response.choices[0].message.content
    # Dividimos el contenido por líneas para obtener las consultas individuales
    content = content.split("\n")
    return content

# Definimos la consulta original sobre factores de crecimiento de ingresos
original_query = (
    "What details can you provide about the factors that led to revenue growth?"
)
# Generamos consultas expandidas usando la función definida
aug_queries = generate_multi_query(original_query)

# Paso 1: Mostramos las consultas expandidas generadas
for query in aug_queries:
    print("\n", query)

# Paso 2: Combinamos la consulta original con las consultas expandidas en una lista
joint_query = [
    original_query
] + aug_queries  # La consulta original está en una lista porque ChromaDB puede manejar múltiples consultas

# Comentario: línea para mostrar las consultas combinadas (comentada)
# print("======> \n\n", joint_query)

# Realizamos una búsqueda con todas las consultas (original + expandidas) y obtenemos embeddings
results = chroma_collection.query(
    query_texts=joint_query, n_results=5, include=["documents", "embeddings"]
)
# Extraemos los documentos recuperados para todas las consultas
retrieved_documents = results["documents"]

# Eliminamos documentos duplicados usando un conjunto (set)
unique_documents = set()
for documents in retrieved_documents:
    for document in documents:
        unique_documents.add(document)

# Mostramos los resultados de documentos para cada consulta
for i, documents in enumerate(retrieved_documents):
    print(f"Query: {joint_query[i]}")
    print("")
    print("Results:")
    for doc in documents:
        print(word_wrap(doc))
        print("")
    print("-" * 100)

# Obtenemos todos los embeddings de la colección para visualización
embeddings = chroma_collection.get(include=["embeddings"])["embeddings"]
# Creamos una transformación UMAP para reducir la dimensionalidad de los embeddings
umap_transform = umap.UMAP(random_state=0, transform_seed=0).fit(embeddings)
# Proyectamos los embeddings del dataset completo en 2D usando UMAP
projected_dataset_embeddings = project_embeddings(embeddings, umap_transform)

# Paso 4: También podemos visualizar los resultados en el espacio de embeddings
# Generamos el embedding de la consulta original
original_query_embedding = embedding_function([original_query])
# Generamos embeddings para todas las consultas (original + expandidas)
augmented_query_embeddings = embedding_function(joint_query)

# Proyectamos la consulta original en el espacio 2D
project_original_query = project_embeddings(original_query_embedding, umap_transform)
# Proyectamos las consultas expandidas en el espacio 2D
project_augmented_queries = project_embeddings(
    augmented_query_embeddings, umap_transform
)

# Extraemos los embeddings de los documentos recuperados
retrieved_embeddings = results["embeddings"]
# Aplanamos la lista de embeddings (de lista de listas a lista simple)
result_embeddings = [item for sublist in retrieved_embeddings for item in sublist]

# Proyectamos los embeddings de los resultados en el espacio 2D
projected_result_embeddings = project_embeddings(result_embeddings, umap_transform)

# Importamos matplotlib para crear la visualización
import matplotlib.pyplot as plt

# Creamos una figura para la visualización
plt.figure()
# Graficamos todos los embeddings del dataset como puntos grises pequeños
plt.scatter(
    projected_dataset_embeddings[:, 0],
    projected_dataset_embeddings[:, 1],
    s=10,
    color="gray",
)
# Graficamos las consultas expandidas como X naranjas grandes
plt.scatter(
    project_augmented_queries[:, 0],
    project_augmented_queries[:, 1],
    s=150,
    marker="X",
    color="orange",
)
# Graficamos los documentos recuperados como círculos verdes vacíos
plt.scatter(
    projected_result_embeddings[:, 0],
    projected_result_embeddings[:, 1],
    s=100,
    facecolors="none",
    edgecolors="g",
)
# Graficamos la consulta original como X roja grande
plt.scatter(
    project_original_query[:, 0],
    project_original_query[:, 1],
    s=150,
    marker="X",
    color="r",
)

# Configuramos el gráfico para mantener la proporción de aspecto
plt.gca().set_aspect("equal", "datalim")
# Establecemos el título del gráfico con la consulta original
plt.title(f"{original_query}")
# Ocultamos los ejes para una visualización más limpia
plt.axis("off")
# Mostramos el gráfico
plt.show()  # display the plot
