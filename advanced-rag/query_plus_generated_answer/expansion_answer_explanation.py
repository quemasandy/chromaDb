# Importamos funciones auxiliares para proyección de embeddings y formateo de texto
from helper_utils import project_embeddings, word_wrap
# Importamos PdfReader para leer archivos PDF
from pypdf import PdfReader
# Importamos el módulo os para operaciones del sistema operativo
import os
# Importamos OpenAI para interactuar con la API de OpenAI
from openai import OpenAI
# Importamos load_dotenv para cargar variables de entorno desde archivo .env
from dotenv import load_dotenv

# Importación duplicada de PdfReader (línea redundante que se puede eliminar)
from pypdf import PdfReader
# Importamos específicamente la clase UMAP para reducción de dimensionalidad
# Fix the UMAP import - import the UMAP class specifically
from umap import UMAP


# Cargamos las variables de entorno desde el archivo .env
# Esto permite acceder a claves API y configuraciones sin hardcodearlas
load_dotenv()

# Obtenemos la clave API de OpenAI desde las variables de entorno
# Esta clave es necesaria para autenticarse con la API de OpenAI
openai_key = os.getenv("OPENAI_API_KEY")
# Creamos una instancia del cliente OpenAI usando la clave API
# Este cliente se usará para hacer llamadas a la API de OpenAI
client = OpenAI(api_key=openai_key)

# Obtenemos la ruta absoluta del archivo actual
# Esto nos da la ubicación completa del script que se está ejecutando
absolute_path = os.path.abspath(__file__)
# Obtenemos el directorio padre del archivo actual
# Esto nos permite navegar a carpetas relacionadas
parent_dir = os.path.dirname(absolute_path)
# Creamos un lector de PDF para el archivo del reporte anual de Microsoft
# Construimos la ruta completa al archivo PDF en la carpeta data
reader = PdfReader(os.path.join(parent_dir, "data", "microsoft-annual-report.pdf"))
# Extraemos el texto de todas las páginas del PDF y eliminamos espacios en blanco
# Creamos una lista donde cada elemento es el texto de una página
pdf_texts = [p.extract_text().strip() for p in reader.pages]

# Filtramos las cadenas vacías de la lista de textos
# Esto elimina páginas que no contienen texto útil
pdf_texts = [text for text in pdf_texts if text]
# Imprimimos la primera página del PDF con formato de envoltura de palabras
# Esto nos permite ver el contenido del PDF de manera legible
print(
    word_wrap(
        pdf_texts[0],
        width=100,
    )
)

# Dividimos el texto en fragmentos más pequeños para procesamiento


# Importamos las clases necesarias para dividir texto de LangChain
# RecursiveCharacterTextSplitter: divide texto basándose en caracteres específicos
# SentenceTransformersTokenTextSplitter: divide texto basándose en tokens del modelo
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)

# Creamos un divisor de texto que usa caracteres específicos como separadores
# separators: define los caracteres que se usan para dividir el texto
# chunk_size: tamaño máximo de cada fragmento (1000 caracteres)
# chunk_overlap: solapamiento entre fragmentos (0 = sin solapamiento)
character_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", ". ", " ", ""], chunk_size=1000, chunk_overlap=0
)
# Dividimos todo el texto del PDF en fragmentos usando el divisor de caracteres
# Primero unimos todos los textos con dobles saltos de línea, luego dividimos
character_split_texts = character_splitter.split_text("\n\n".join(pdf_texts))

# Imprimimos el fragmento número 10 para verificar la división
# Usamos word_wrap para formatear la salida de manera legible
print(word_wrap(character_split_texts[10]))
# Imprimimos el número total de fragmentos creados
print(f"\nTotal chunks: {len(character_split_texts)}")

# Creamos un divisor de texto basado en tokens usando SentenceTransformers
# chunk_overlap: sin solapamiento entre fragmentos
# tokens_per_chunk: máximo 256 tokens por fragmento
token_splitter = SentenceTransformersTokenTextSplitter(
    chunk_overlap=0, tokens_per_chunk=256
)
# Inicializamos una lista vacía para almacenar los fragmentos basados en tokens
token_split_texts = []
# Iteramos sobre cada fragmento de caracteres y los dividimos en tokens
# Esto crea fragmentos más pequeños y consistentes basados en el modelo de lenguaje
for text in character_split_texts:
    token_split_texts += token_splitter.split_text(text)

# Imprimimos el fragmento número 10 basado en tokens para verificar
print(word_wrap(token_split_texts[10]))
# Imprimimos el número total de fragmentos basados en tokens
print(f"\nTotal chunks: {len(token_split_texts)}")


# Importamos ChromaDB para crear y gestionar la base de datos vectorial
import chromadb
# Importamos la función de embedding de SentenceTransformer para ChromaDB
# Esta función convierte texto en vectores numéricos usando el modelo SentenceTransformer
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# Creamos una instancia de la función de embedding
# Esta función se usará para convertir texto en vectores de alta dimensionalidad
embedding_function = SentenceTransformerEmbeddingFunction()
# Probamos la función de embedding con el fragmento número 10
# Esto nos permite ver cómo se ve un embedding (vector numérico)
print(embedding_function([token_split_texts[10]]))

# Creamos un cliente de ChromaDB
# Este cliente nos permite interactuar con la base de datos vectorial
chroma_client = chromadb.Client()
# Creamos una colección en ChromaDB llamada "microsoft-collection"
# Una colección es como una tabla en una base de datos tradicional
# Le asignamos la función de embedding que creamos anteriormente
chroma_collection = chroma_client.create_collection(
    "microsoft-collection", embedding_function=embedding_function
)

# Creamos IDs únicos para cada fragmento de texto
# Los IDs son necesarios para identificar cada documento en la colección
ids = [str(i) for i in range(len(token_split_texts))]
# Agregamos todos los fragmentos de texto a la colección de ChromaDB
# Esto almacena los documentos junto con sus embeddings en la base de datos
chroma_collection.add(ids=ids, documents=token_split_texts)
# Imprimimos el número total de documentos almacenados en la colección
print(f"Total chunks: {chroma_collection.count()}")

# Definimos una consulta de ejemplo para buscar en los documentos
# Esta es la pregunta que queremos responder usando RAG
query = "What was the total revenue for the year?"


# Realizamos una búsqueda en la colección usando la consulta
# query_texts: lista de consultas a buscar
# n_results: número máximo de resultados a retornar (5 documentos más relevantes)
results = chroma_collection.query(query_texts=[query], n_results=5)
# Extraemos los documentos recuperados del resultado
# results["documents"][0] contiene la lista de documentos para la primera consulta
retrieved_documents = results["documents"][0]

# Iteramos sobre cada documento recuperado y lo imprimimos
# Esto nos permite ver qué documentos fueron encontrados como más relevantes
for document in retrieved_documents:
    print(word_wrap(document))
    print("\n")


# Definimos una función para generar respuestas hipotéticas usando OpenAI
# Esta función implementa la técnica de "query expansion" o expansión de consultas
def augment_query_generated(query, model="gpt-3.5-turbo"):
    # Definimos el prompt del sistema que le dice al modelo qué hacer
    # El modelo actuará como un asistente experto en investigación financiera
    prompt = """You are a helpful expert financial research assistant. 
   Provide an example answer to the given question, that might be found in a document like an annual report."""
    # Creamos la lista de mensajes para la API de OpenAI
    # Incluye el mensaje del sistema y la consulta del usuario
    messages = [
        {
            "role": "system",
            "content": prompt,
        },
        {"role": "user", "content": query},
    ]

    # Hacemos la llamada a la API de OpenAI para generar la respuesta
    # model: especifica qué modelo usar (gpt-3.5-turbo por defecto)
    # messages: la conversación que queremos que procese el modelo
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    # Extraemos el contenido de la respuesta generada
    # response.choices[0].message.content contiene el texto generado
    content = response.choices[0].message.content
    # Retornamos la respuesta generada
    return content


# Definimos la consulta original que queremos expandir
# Esta es la pregunta principal que queremos responder
original_query = "What was the total profit for the year, and how does it compare to the previous year?"
# Generamos una respuesta hipotética usando la función que definimos
# Esta respuesta simula lo que podríamos encontrar en los documentos
hypothetical_answer = augment_query_generated(original_query)

# Combinamos la consulta original con la respuesta hipotética
# Esto crea una consulta expandida que incluye tanto la pregunta como una posible respuesta
joint_query = f"{original_query} {hypothetical_answer}"
# Imprimimos la consulta combinada para verificar el resultado
print(word_wrap(joint_query))

# Realizamos una búsqueda usando la consulta expandida
# Esta búsqueda debería encontrar documentos más relevantes
# include: especifica qué información incluir en los resultados (documentos y embeddings)
# e results
results = chroma_collection.query(
    query_texts=joint_query, n_results=5, include=["documents", "embeddings"]
)
# Extraemos los documentos recuperados de la búsqueda expandida
retrieved_documents = results["documents"][0]

# Código comentado que realizaría la búsqueda con la consulta original
# Esto se puede usar para comparar resultados entre consulta original y expandida
# r results
# results = chroma_collection.query(
#     query_texts=original_query, n_results=5, include=["documents", "embeddings"]
# )

# Imprimimos cada documento recuperado con la consulta expandida
# Esto nos permite ver si la expansión mejoró la relevancia de los resultados
for doc in retrieved_documents:
    print(word_wrap(doc))
    print("")

# Obtenemos todos los embeddings de la colección
# Esto nos da los vectores numéricos de todos los documentos almacenados
embeddings = chroma_collection.get(include=["embeddings"])["embeddings"]
# Aplicamos UMAP para reducir la dimensionalidad de los embeddings
# UMAP convierte vectores de alta dimensión en 2D para visualización
# random_state y transform_seed: aseguran resultados reproducibles
# Fix the UMAP usage - use the imported UMAP class directly
umap_transform = UMAP(random_state=0, transform_seed=0).fit(embeddings)
# Proyectamos todos los embeddings del dataset usando la transformación UMAP
# Esto convierte los vectores de alta dimensión en coordenadas 2D
projected_dataset_embeddings = project_embeddings(embeddings, umap_transform)


# Extraemos los embeddings de los documentos recuperados
# Estos son los vectores de los documentos que fueron encontrados como más relevantes
retrieved_embeddings = results["embeddings"][0]
# Generamos el embedding de la consulta original
# Esto convierte la pregunta en un vector numérico
original_query_embedding = embedding_function([original_query])
# Generamos el embedding de la consulta expandida
# Esto convierte la pregunta + respuesta hipotética en un vector numérico
augmented_query_embedding = embedding_function([joint_query])

# Proyectamos el embedding de la consulta original a 2D usando UMAP
# Esto nos permite visualizar dónde se ubica la consulta en el espacio de embeddings
projected_original_query_embedding = project_embeddings(
    original_query_embedding, umap_transform
)
# Proyectamos el embedding de la consulta expandida a 2D
# Esto nos permite comparar la ubicación de ambas consultas
projected_augmented_query_embedding = project_embeddings(
    augmented_query_embedding, umap_transform
)
# Proyectamos los embeddings de los documentos recuperados a 2D
# Esto nos permite ver dónde se ubican los documentos relevantes
projected_retrieved_embeddings = project_embeddings(
    retrieved_embeddings, umap_transform
)

# Importamos matplotlib para crear visualizaciones
import matplotlib.pyplot as plt

# Creamos una nueva figura para la visualización
# Plot the projected query and retrieved documents in the embedding space
plt.figure()

# Graficamos todos los embeddings del dataset como puntos grises pequeños
# Estos representan todos los documentos en el espacio de embeddings 2D
plt.scatter(
    projected_dataset_embeddings[:, 0],  # Coordenada X de cada punto
    projected_dataset_embeddings[:, 1],  # Coordenada Y de cada punto
    s=10,  # Tamaño del punto (pequeño)
    color="gray",  # Color gris para todos los documentos
)
# Graficamos los embeddings de los documentos recuperados como círculos verdes vacíos
# Estos son los documentos que fueron encontrados como más relevantes
plt.scatter(
    projected_retrieved_embeddings[:, 0],  # Coordenada X
    projected_retrieved_embeddings[:, 1],  # Coordenada Y
    s=100,  # Tamaño del punto (más grande)
    facecolors="none",  # Sin relleno (círculo vacío)
    edgecolors="g",  # Borde verde
)
# Graficamos el embedding de la consulta original como una X roja
# Esto muestra dónde se ubica la pregunta original en el espacio
plt.scatter(
    projected_original_query_embedding[:, 0],  # Coordenada X
    projected_original_query_embedding[:, 1],  # Coordenada Y
    s=150,  # Tamaño del punto (más grande)
    marker="X",  # Forma de X
    color="r",  # Color rojo
)
# Graficamos el embedding de la consulta expandida como una X naranja
# Esto muestra dónde se ubica la pregunta expandida en el espacio
plt.scatter(
    projected_augmented_query_embedding[:, 0],  # Coordenada X
    projected_augmented_query_embedding[:, 1],  # Coordenada Y
    s=150,  # Tamaño del punto (más grande)
    marker="X",  # Forma de X
    color="orange",  # Color naranja
)

# Configuramos la relación de aspecto para que sea igual en ambos ejes
# Esto asegura que la visualización no se distorsione
plt.gca().set_aspect("equal", "datalim")
# Establecemos el título del gráfico usando la consulta original
plt.title(f"{original_query}")
# Ocultamos los ejes para una visualización más limpia
plt.axis("off")
# Mostramos el gráfico en pantalla
# display the plot
plt.show()
