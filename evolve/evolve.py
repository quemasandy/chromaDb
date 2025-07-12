"""
EJERCICIO INTEGRAL: BÚSQUEDA DE PROGRAMADORES CON BASE DE DATOS VECTORIAL

Temática: Buscar programadores con diferentes lenguajes, tecnologías y experiencia usando ChromaDB y visualización de embeddings.

Incluye:
A. Extraer y mostrar los embeddings de algunos documentos y consultas, imprimiendo los vectores y sus distancias.
B. Calcular manualmente la distancia coseno entre dos textos y comparar con el resultado de ChromaDB.
C. Usar matplotlib y PCA/t-SNE para graficar los vectores en 2D/3D.
D. Comparar la búsqueda por palabras clave vs. búsqueda vectorial en un ejemplo concreto.

Cada sección tiene comentarios explicativos y sugerencias de experimentos.
"""

# =====================
# IMPORTS Y CONFIGURACIÓN
# =====================
import chromadb  # Base de datos vectorial
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import numpy as np  # Para cálculos vectoriales
import matplotlib.pyplot as plt  # Para visualización
from sklearn.decomposition import PCA  # Reducción de dimensionalidad
import json
from typing import Sequence

# =====================
# SECCIÓN 1: DATOS DE PROGRAMADORES
# =====================
# Creamos una lista de perfiles de programadores
programmers = [
    {
        "id": "p1",
        "name": "Ana",
        "languages": ["Python", "JavaScript"],
        "technologies": ["Django", "React"],
        "experience": 5,
        "description": "Desarrolladora fullstack con experiencia en Python y JavaScript, experta en Django y React."
    },
    {
        "id": "p2",
        "name": "Luis",
        "languages": ["Java", "Kotlin"],
        "technologies": ["Spring", "Android"],
        "experience": 7,
        "description": "Ingeniero backend especializado en Java y Kotlin, desarrollo de APIs con Spring y apps Android."
    },
    {
        "id": "p3",
        "name": "Sofía",
        "languages": ["C#", "TypeScript"],
        "technologies": [".NET", "Angular"],
        "experience": 4,
        "description": "Programadora con experiencia en C# y TypeScript, desarrollo web con .NET y Angular."
    },
    {
        "id": "p4",
        "name": "Carlos",
        "languages": ["Go", "Python"],
        "technologies": ["Docker", "Kubernetes"],
        "experience": 6,
        "description": "DevOps e ingeniero de software, experto en Go, Python, Docker y Kubernetes."
    },
    {
        "id": "p5",
        "name": "Elena",
        "languages": ["Ruby", "JavaScript"],
        "technologies": ["Rails", "Vue.js"],
        "experience": 3,
        "description": "Desarrolladora web con experiencia en Ruby on Rails y Vue.js, entusiasta de JavaScript."
    },
]

# Convertimos los perfiles a textos para embeddings
documents = [
    f"{p['name']}: {', '.join(p['languages'])}; {', '.join(p['technologies'])}; {p['experience']} años; {p['description']}"
    for p in programmers
]
ids = [p["id"] for p in programmers]
metadatas: Sequence[dict[str, str|int|float|bool|None]] = [
    {
        "name": str(p["name"]),
        "experience": int(p["experience"]),
        "languages": ", ".join(p["languages"]),
        "technologies": ", ".join(p["technologies"])
    }
    for p in programmers
]

# =====================
# SECCIÓN 2: CHROMADB Y EMBEDDINGS
# =====================
# Configuramos ChromaDB en modo persistente local
persist_directory = "./chroma_db"
client = chromadb.Client(Settings(persist_directory=persist_directory))
default_ef = embedding_functions.DefaultEmbeddingFunction()

# Creamos la colección
collection = client.get_or_create_collection(
    name="programmers",
    embedding_function=default_ef  # type: ignore
)

# Limpiamos la colección para evitar duplicados en pruebas
try:
    collection.delete(ids=ids)
except Exception:
    pass

# Insertamos los perfiles
collection.add(documents=documents, ids=ids, metadatas=metadatas)

# =====================
# SECCIÓN 3: EXTRAER Y MOSTRAR EMBEDDINGS Y DISTANCIAS (A)
# =====================
print("\n=== EMBEDDINGS DE PROGRAMADORES ===")
embeddings = default_ef(documents)  # Lista de vectores
for i, emb in enumerate(embeddings):
    print(f"{programmers[i]['name']}: {emb[:5]}... (dim={len(emb)})")  # Mostramos solo las primeras 5 dimensiones

# Calculamos la distancia coseno entre Ana y Carlos
from numpy.linalg import norm

def cosine_distance(a, b):
    """Calcula la distancia coseno entre dos vectores."""
    return 1 - np.dot(a, b) / (norm(a) * norm(b))

ana_emb = embeddings[0]
carlos_emb = embeddings[3]
dist_ana_carlos = cosine_distance(ana_emb, carlos_emb)
print(f"\nDistancia coseno (Ana, Carlos): {dist_ana_carlos:.4f}")

# =====================
# SECCIÓN 4: CONSULTA VECTORIAL Y DISTANCIA SEGÚN CHROMADB (B)
# =====================
query_text = "Busco programador Python con experiencia en Docker"
query_emb = default_ef([query_text])[0]

# Distancia manual entre consulta y cada programador
print("\n=== DISTANCIAS MANUALES ENTRE CONSULTA Y PROGRAMADORES ===")
for i, emb in enumerate(embeddings):
    dist = cosine_distance(query_emb, emb)
    print(f"{programmers[i]['name']}: {dist:.4f}")

# Consulta vectorial con ChromaDB
results = collection.query(query_texts=[query_text], n_results=3)
print("\n=== RESULTADOS DE BÚSQUEDA VECTORIAL (ChromaDB) ===")
if results["documents"] and results["distances"] and results["documents"][0] and results["distances"][0]:
    for i, doc in enumerate(results["documents"][0]):
        print(f"{i+1}. {doc} (distancia: {results['distances'][0][i]:.4f})")
else:
    print("No se encontraron resultados.")

# =====================
# SECCIÓN 5: VISUALIZACIÓN DE EMBEDDINGS EN 2D (C)
# =====================
print("\n=== VISUALIZACIÓN DE EMBEDDINGS EN 2D (PCA) ===")
pca = PCA(n_components=2)
embeddings_2d = pca.fit_transform(np.array(embeddings))

plt.figure(figsize=(8, 6))
for i, (x, y) in enumerate(embeddings_2d):
    plt.scatter(x, y, label=programmers[i]["name"])
    plt.text(x+0.01, y+0.01, programmers[i]["name"])
plt.title("Embeddings de programadores (PCA 2D)")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# =====================
# SECCIÓN 6: BÚSQUEDA POR PALABRAS CLAVE VS VECTORIAL (D)
# =====================
print("\n=== COMPARACIÓN: PALABRAS CLAVE VS VECTORIAL ===")
keyword = "Python Docker"

# Búsqueda por palabras clave (simulación simple)
print("\nBúsqueda por palabras clave:")
for p in programmers:
    if any(kw.lower() in p["description"].lower() for kw in keyword.split()):
        print(f"- {p['name']}: {p['description']}")

# Búsqueda vectorial (ya realizada arriba)
print("\nBúsqueda vectorial (ChromaDB):")
if results["documents"] and results["documents"][0]:
    for i, doc in enumerate(results["documents"][0]):
        print(f"- {doc}")
else:
    print("No se encontraron resultados.")

print("\n" + "="*60)
print("¡Ejercicio completo! Puedes modificar, experimentar y preguntarme sobre cada sección.")
print("="*60)
