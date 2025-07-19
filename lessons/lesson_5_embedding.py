import os  # Importa el módulo os para acceso a variables de entorno del sistema operativo
from dotenv import load_dotenv  # Importa la función load_dotenv para cargar variables desde archivo .env

from openai import OpenAI  # Importa la clase OpenAI del SDK oficial de OpenAI para interactuar con la API

load_dotenv()  # Carga las variables de entorno desde el archivo .env al entorno de ejecución

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY_QUEMASANDY"))  # Crea una instancia del cliente OpenAI usando la API key desde las variables de entorno

response = client.embeddings.create(  # Llama al endpoint de embeddings de OpenAI para generar vectores numéricos del texto
    input="Your text string goes here",  # El texto de entrada que será convertido a embedding (vector numérico)
    model="text-embedding-3-small"  # Especifica el modelo de embedding a utilizar (versión pequeña y eficiente)
)

print(response)  # Imprime la respuesta completa del API que contiene el vector embedding y metadatos
