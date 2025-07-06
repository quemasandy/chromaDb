from chromadb.utils import embedding_functions

# Instancia la función de embedding por defecto
default_ef = embedding_functions.DefaultEmbeddingFunction()

# Texto a embeddar (debe ser una lista)
name = ["Paulo"]

# Genera el embedding
emb = default_ef(name)

print(emb)
