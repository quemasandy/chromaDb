"""
EJERCICIO DIDÁCTICO: ENTENDIENDO EL PRODUCTO PUNTO (DOT PRODUCT) EN 2 DIMENSIONES

Objetivo: Explicar paso a paso qué es el producto punto, cómo se calcula, y por qué mide alineación entre vectores.
Usamos vectores de 2D para simplicidad, pero el concepto se extiende a ND como en embeddings de ChromaDB.

Estructura:
1. Teoría con comentarios.
2. Cálculos simples paso a paso.
3. De simple a complejo: Empezamos con basics y agregamos complejidad.
4. Ejercicio de rotación: Vector base en eje X, y dot con vectores rotados de 0° a 360° en pasos de 10°.
"""

import numpy as np  # Para operaciones matemáticas y arrays

# =====================
# PARTE 1: EXPLICACIÓN TEÓRICA DEL PRODUCTO PUNTO
# =====================
# ¿Qué es el producto punto (np.dot)?
# - Es una operación que toma dos vectores y retorna un número escalar.
# - Fórmula en 2D: (A_x * B_x) + (A_y * B_y)
# - En general (ND): Suma de (A_i * B_i) para cada componente i.
# - Significado: Mide la 'alineación' o 'similitud direccional' entre vectores.
#   - Alto positivo: Vectores apuntan en direcciones similares.
#   - Cero: Vectores son perpendiculares (no alineados).
#   - Negativo: Vectores apuntan en direcciones opuestas.
# ¿Por qué usarlo?
# - Base para métricas como distancia coseno (en embeddings y ChromaDB).
# - En física: Trabajo = fuerza · desplazamiento (alineación de fuerzas).
# - En machine learning: Similitud entre características (e.g., embeddings de textos).
#
# Analogía simple (2D):
# - Vector A: [3, 0] (apunta derecha).
# - Vector B: [2, 0] (apunta misma dirección) → Dot alto (6).
# - Vector C: [0, 2] (apunta arriba, perpendicular) → Dot = 0.
# - Vector D: [-3, 0] (apunta izquierda, opuesto) → Dot negativo (-9).
#
# Nota: Dot depende de longitudes; para pura dirección, normaliza con norms (como en coseno).

# =====================
# PARTE 2: CONCEPTOS BÁSICOS - VECTORES EN 2D
# =====================
# Definimos vectores simples
A = np.array([3, 4])  # Ejemplo base
B = np.array([2, 1])  # Otro vector
print("Vector A:", A)
print("Vector B:", B)

# =====================
# PARTE 3: CÁLCULOS SIMPLES DE PRODUCTO PUNTO
# =====================
print("\n=== EJEMPLOS SIMPLES DE np.dot ===")

# Ejemplo 1: Cálculo manual y con np.dot
dot_manual = (3*2) + (4*1)  # 6 + 4 = 10
dot_numpy = np.dot(A, B)
print("Dot manual: (3*2) + (4*1) = 10")
print("Dot con np.dot:", dot_numpy)  # 10

# Ejemplo 2: Vectores idénticos
C = np.array([3, 4])  # Igual a A
dot_identical = np.dot(A, C)
print("Dot de A con sí mismo:", dot_identical)  # 9 + 16 = 25 (alto positivo)

# Ejemplo 3: Vectores perpendiculares
D = np.array([4, -3])  # Perpendicular: dot debería ser 0
dot_perp = np.dot(A, D)
print("Dot de A con perpendicular:", dot_perp)  # 12 - 12 = 0

# Ejemplo 4: Vectores opuestos
E = np.array([-3, -4])  # Opuesto a A
dot_opposite = np.dot(A, E)
print("Dot de A con opuesto:", dot_opposite)  # -9 -16 = -25 (negativo)

# =====================
# PARTE 4: DE SIMPLE A COMPLEJO - EFECTO DE LONGITUD Y DIRECCIÓN
# =====================
print("\n=== EFECTO DE LONGITUD Y DIRECCIÓN ===")

# Simple: Vectores unitarios (longitud 1) para ver pura dirección
A_unit = A / np.linalg.norm(A)  # Normalizado
B_unit = B / np.linalg.norm(B)
print("Dot de unitarios (solo dirección):", np.dot(A_unit, B_unit))  # ≈0.894 (cos del ángulo)

# Complejo: Escala un vector y ve cómo cambia dot
B_scaled = B * 2  # Doble longitud
dot_scaled = np.dot(A, B_scaled)
print("Dot con B escalado x2:", dot_scaled)  # 20 (doble del original 10, muestra efecto de longitud)

# =====================
# PARTE 5: EJERCICIO DE ROTACIÓN - PRODUCTO PUNTO CON ÁNGULOS DE 0° A 360°
# =====================
print("\n=== EJERCICIO: DOT PRODUCT CON ROTACIONES (0° a 360° en pasos de 10°) ===")

# Vector base en eje X (como pediste)
base_vector = np.array([1, 0])  # Longitud 1, apunta a 0° (derecha)
print("Vector base:", base_vector)

# Generamos vectores rotados (unitarios, para pura dirección)
angles_deg = np.arange(0, 370, 10)  # 0° a 360° en pasos de 10°
print("Ángulo (°) | Vector Rotado | Dot Product con Base")
print("-" * 50)
for deg in angles_deg:
    rad = np.deg2rad(deg)  # Convertir a radianes
    rotated = np.array([np.cos(rad), np.sin(rad)])  # Vector unitario en ángulo deg
    dot_val = np.dot(base_vector, rotated)
    print(f"{deg:3d}°     | {rotated} | {dot_val:.4f}")

# Análisis: Observa cómo dot es 1 en 0°, 0 en 90°/270°, -1 en 180°, y valores intermedios.
print("\n¡Ejercicio completo! Experimenta cambiando el vector base o pasos angulares para ver patrones.") 