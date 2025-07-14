"""
EJERCICIO DIDÁCTICO: ENTENDIENDO LA DISTANCIA COSENO EN 2 DIMENSIONES

Objetivo: Explicar paso a paso qué es la distancia coseno, cómo se calcula, y por qué es útil en embeddings.
Usamos vectores de 2D para simplicidad (fácil de visualizar), pero el concepto se extiende a 384D como en ChromaDB.

Estructura:
1. Teoría con comentarios.
2. Cálculos simples paso a paso.
3. De simple a complejo: Empezamos con basics y agregamos complejidad.
"""

import numpy as np  # Para operaciones matemáticas

from numpy.linalg import norm  # Para calcular la norma (longitud) de vectores

# =====================
# PARTE 1: EXPLICACIÓN TEÓRICA DE LA DISTANCIA COSENO
# =====================
# ¿Qué es la distancia coseno?
# - Mide el ÁNGULO entre dos vectores en un espacio multidimensional.
# - Útil para similitud: Vectores con ángulos pequeños (cerca de 0°) son similares.
# - Fórmula: distancia = 1 - cos(θ), donde cos(θ) = (A · B) / (|A| * |B|)
#   - A · B: Producto punto (mide alineación).
#   - |A| y |B|: Normas (longitudes) de los vectores.
# - Rango: 0 (idénticos) a 2 (opuestos). En embeddings, usamos 0-1 para similitud positiva.
# ¿Por qué usarla?
# - Ignora magnitud (longitud), enfoca en dirección (significado semántico).
# - Perfecta para embeddings: Dos textos con mismo significado tendrán vectores en direcciones similares.
#
# Analogía simple (2D):
# - Vector A: Flecha de (0,0) a (3,4) → Longitud 5, dirección noreste.
# - Vector B: Flecha de (0,0) a (6,8) → Mismo dirección, longitud 10.
# - Ángulo: 0° (idénticos en dirección) → Distancia coseno = 0.
#
# Extensión a ND: Igual, pero en más dimensiones (e.g., 384 en ChromaDB).

# =====================
# PARTE 2: CONCEPTOS BÁSICOS - VECTORES EN 2D
# =====================
# Definimos dos vectores simples en 2D (como 'embeddings' simplificados)
# Vector A: Representa 'Python developer' → [3, 4] (e.g., dim1: skill level, dim2: experience)
# Vector B: Representa 'JavaScript coder' → [2, 1] (diferente dirección)
A = np.array([3, 4])
B = np.array([2, 1])
print("Vector A:", A)
print("Vector B:", B)

# =====================
# PARTE 3: ¿QUÉ ES Y CÓMO SE CALCULA np.dot(a, b)? (PRODUCTO PUNTO)
# =====================
# ¿Qué es np.dot?
# - Calcula el PRODUCTO PUNTO (dot product) entre dos vectores.
# - Fórmula: Suma de productos elemento a elemento.
# - En 2D: (a1*b1) + (a2*b2)
# - Significado: Mide cuánto se 'alinean' los vectores (cuánto apuntan en la misma dirección).
#   - Alto positivo: Similar dirección.
#   - Cero: Perpendiculares (no relacionados).
#   - Negativo: Direcciones opuestas.
# ¿Para qué se usa?
# - Base de muchas métricas (e.g., coseno, similitud).
# - En embeddings: Alto dot product = textos semánticamente similares.
# ¿Cómo se calcula manualmente?
# - Para A=[3,4], B=[2,1]: (3*2) + (4*1) = 6 + 4 = 10
# - np.dot lo hace eficiente para ND.
print("\n=== CÁLCULO DEL PRODUCTO PUNTO (np.dot) ===")
dot_product = np.dot(A, B)
print("Producto punto manual: (3*2) + (4*1) = 6 + 4 = 10")
print("Producto punto con np.dot:", dot_product)  # Debería ser 10

# Ejemplo simple: Vectores idénticos
C = np.array([3, 4])  # Igual a A
print("Dot product de A con sí mismo:", np.dot(A, C))  # Alto: 3*3 + 4*4 = 9 + 16 = 25

# Ejemplo complejo: Vectores opuestos
D = np.array([-3, -4])  # Opuesto a A
print("Dot product de A con opuesto:", np.dot(A, D))  # Negativo: -9 + -16 = -25

# =====================
# PARTE 4: ¿QUÉ ES Y CÓMO SE CALCULA norm(a) * norm(b)? (NORMAS)
# =====================
# ¿Qué es norm?
# - Calcula la 'longitud' (magnitud) de un vector (norma Euclidiana L2 por defecto).
# - Fórmula en 2D: sqrt(a1² + a2²)
# - Significado: Tamaño del vector, independientemente de dirección.
# ¿Para qué se usa?
# - Normalizar: Evita que vectores 'largos' parezcan más similares solo por tamaño.
# - En coseno: Divide el dot product para enfocarse en ángulo.
# ¿Cómo se calcula manualmente?
# - Para A=[3,4]: sqrt(9 + 16) = sqrt(25) = 5
# - norm(a) * norm(b): Multiplica longitudes.
print("\n=== CÁLCULO DE NORMAS (norm) ===")
norm_A = norm(A)
norm_B = norm(B)
print("Norma de A manual: sqrt(3² + 4²) = sqrt(9+16) = sqrt(25) = 5")
print("Norma de A con norm:", norm_A)  # 5.0
print("Norma de B manual: sqrt(2² + 1²) = sqrt(4+1) = sqrt(5) ≈ 2.236")
print("Norma de B con norm:", norm_B)
print("Producto de normas (norm_A * norm_B):", norm_A * norm_B)  # ≈ 11.180

# Ejemplo simple: Vector unitario (longitud 1)
E = np.array([1, 0])
print("Norma de [1,0]:", norm(E))  # 1.0

# Ejemplo complejo: Vector cero
F = np.array([0, 0])
print("Norma de [0,0]:", norm(F))  # 0.0 (cuidado: divide por cero en coseno!)

# =====================
# PARTE 5: CÁLCULO COMPLETO DE DISTANCIA COSENO (SIMPLE A COMPLEJO)
# =====================
# Fórmula completa: 1 - (dot / (norm_a * norm_b))
print("\n=== DISTANCIA COSENO COMPLETA ===")
cos_theta = np.dot(A, B) / (norm(A) * norm(B))  # Cos del ángulo
print("Cos(θ) = dot / (norm_A * norm_B) = 10 / 11.180 ≈ 0.894")
print("Distancia coseno = 1 - cos(θ) ≈ 1 - 0.894 = 0.106")  # Baja: Similares

dist = 1 - np.dot(A, B) / (norm(A) * norm(B))
print("Distancia con fórmula:", dist)

# Ejemplo simple: Vectores idénticos
print("Distancia A con C (idénticos):", 1 - np.dot(A, C) / (norm(A) * norm(C)))  # 0.0

# Ejemplo complejo: Vectores perpendiculares
G = np.array([4, -3])  # Perpendicular a A (dot=0)
print("Dot de A y G:", np.dot(A, G))  # 12 - 12 = 0
print("Distancia A y G:", 1 - np.dot(A, G) / (norm(A) * norm(G)))  # 1.0 (90°)

# =====================
# PARTE 6: EXTENSIÓN A EMBEDDINGS REALES
# =====================
# En ChromaDB: Mismo cálculo, pero en 384D.
# Ej: Ana y Carlos en tu código usan esto para similitud semántica.
# print("\n¡Ejercicio completo! Experimenta cambiando vectores y observa cambios en distancias.")

A = np.array([1, 0])
B = np.array([1, 0])
C = np.array([1, 1])
D = np.array([0, 1])
E = np.array([-1, 1])
F = np.array([0, -1])

print('\n'*3)
print('-'*100)
print('A:', A)
print('B:', B)
print('C:', C)
print('D:', D)
print('E:', E)
print('F:', F)
print('-'*100)
print('np.dot(A, B):', np.dot(A, B))
print('np.dot(A, C):', np.dot(A, C))
print('np.dot(A, D):', np.dot(A, D))
print('np.dot(A, E):', np.dot(A, E))
print('np.dot(A, F):', np.dot(A, F))
print('-'*100)
print('norm(A):', norm(A))
print('norm(B):', norm(B))
print('norm(C):', norm(C))
print('norm(D):', norm(D))
print('norm(E):', norm(E))
print('norm(F):', norm(F))
print('-'*100)
print('norm(A) * norm(B):', norm(A) * norm(B))
print('norm(A) * norm(C):', norm(A) * norm(C))
print('norm(A) * norm(D):', norm(A) * norm(D))
print('norm(A) * norm(E):', norm(A) * norm(E))
print('norm(A) * norm(F):', norm(A) * norm(F))
print('-'*100)
print('np.dot(A, B) / (norm(A) * norm(B)) 0 grados:', np.dot(A, B) / (norm(A) * norm(B)))
print('np.dot(A, C) / (norm(A) * norm(C)) 45 grados:', np.dot(A, C) / (norm(A) * norm(C)))
print('np.dot(A, D) / (norm(A) * norm(D)) 90 grados:', np.dot(A, D) / (norm(A) * norm(D)))
print('np.dot(A, E) / (norm(A) * norm(E)) 135 grados:', np.dot(A, E) / (norm(A) * norm(E)))
print('np.dot(A, F) / (norm(A) * norm(F)) 180 grados:', np.dot(A, F) / (norm(A) * norm(F)))
print('-'*100)
print('cosine_distance A y B 0 grados:', 1 - np.dot(A, B) / (norm(A) * norm(B)))
print('cosine_distance A y C 45 grados:', 1 - np.dot(A, C) / (norm(A) * norm(C)))
print('cosine_distance A y D 90 grados:', 1 - np.dot(A, D) / (norm(A) * norm(D)))
print('cosine_distance A y E 135 grados:', 1 - np.dot(A, E) / (norm(A) * norm(E)))
print('cosine_distance A y F 180 grados:', 1 - np.dot(A, F) / (norm(A) * norm(F)))
print('-'*100)



