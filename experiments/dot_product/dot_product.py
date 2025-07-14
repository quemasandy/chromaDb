import numpy as np  # Para operaciones vectoriales y matemáticas

print("\n=== EJERCICIO: DOT PRODUCT CON ROTACIONES (0° a 360° en pasos de 5°) ===")

# Definimos un vector base (por ejemplo, [1, 0])
base_vector = np.array([1, 0])

# Generamos vectores rotados (unitarios, para pura dirección)
angles_deg = np.arange(0, 365, 5)  # 0° a 360° en pasos de 5°
print(f"{'Ángulo (°)':<12} | {'Vector Rotado':<30} | {'Dot Product':<12}")
print("-" * 60)
for deg in angles_deg:
    rad = np.deg2rad(deg)  # Convertir a radianes
    rotated = np.array([np.cos(rad), np.sin(rad)])  # Vector unitario en ángulo deg
    dot_val = np.dot(base_vector, rotated)
    print(f"{deg:10d}° | {str(rotated):<30} | {dot_val:.4f}")

# =====================
# PARTE 6: GENERAR ARCHIVO EXCEL CON RESULTADOS
# =====================
import pandas as pd  # Para crear DataFrame y exportar a Excel

print("\n=== GENERANDO ARCHIVO EXCEL 'rotations_results.xlsx' ===")

# Crear lista de resultados
results = []
for deg in angles_deg:
    rad = np.deg2rad(deg)
    rotated = np.array([np.cos(rad), np.sin(rad)])
    dot_val = np.dot(base_vector, rotated)
    results.append({
        'Ángulo (°)': deg,
        'Rotated_X': rotated[0],
        'Rotated_Y': rotated[1],
        'Dot_Product': dot_val
    })

# Crear DataFrame y exportar a Excel
df = pd.DataFrame(results)
df.to_excel('rotations_results.xlsx', index=False)
print("Archivo Excel generado con éxito!")

# =====================
# PARTE 7: GRÁFICO DE VECTORES ROTADOS Y DOT PRODUCT
# =====================
import matplotlib.pyplot as plt  # Para gráficos

print("\n=== GENERANDO GRÁFICO INTERACTIVO DE VECTORES ROTADOS (con Plotly) ===")

import plotly.graph_objects as go  # Para gráficos interactivos

# Crear figura Plotly
fig = go.Figure()

# Añadir vectores rotados cada 5°, con colores y hover
for deg in angles_deg:
    rad = np.deg2rad(deg)
    rotated = np.array([np.cos(rad), np.sin(rad)])
    dot_val = np.dot(base_vector, rotated)
    is_highlight = (deg % 45 == 0)
    color = 'blue' if is_highlight else 'gray'
    opacity = 1.0 if is_highlight else 0.3
    width = 3 if is_highlight else 1
    # Dibujar línea como vector
    fig.add_trace(go.Scatter(
        x=[0, rotated[0]],
        y=[0, rotated[1]],
        mode='lines+markers',
        line=dict(color=color, width=width),
        opacity=opacity,
        hoverinfo='text',
        text=f"{deg}°<br>Dot: {dot_val:.4f}",
        showlegend=False
    ))
    # Añadir annotation para TODOS los vectores
    label = f"{deg}°<br>{dot_val:.3f}" if is_highlight else f"{dot_val:.3f}"  # Completo para highlights, solo dot para grises
    font_size = 10 if is_highlight else 9  # Pequeño para grises
    font_color = 'blue' if is_highlight else 'gray'
    x_offset = 0.125 if deg == 360 else 0  # Adds a slight horizontal offset to the 360° label position to prevent overlap with the 0° label, improving graph readability
    fig.add_annotation(
        x=rotated[0]*1.1 + x_offset, y=rotated[1]*1.1,
        text=label,
        showarrow=False,
        font=dict(size=font_size, color=font_color)
    )

# Configurar layout para interactividad
fig.update_layout(
    title='Vectores Rotados cada 5° y Producto Punto (Hover para detalles; Highlights en azul)',
    xaxis=dict(range=[-1.5, 1.5], title='X'),
    yaxis=dict(range=[-1.5, 1.5], title='Y'),
    width=1300, height=1300,
    showlegend=False
)

fig.show()  # Abre en browser para zoom/hover
print("Gráfico interactivo generado con Plotly! Abre en browser; haz hover sobre vectores para ver labels. Zoom para claridad.")

# Análisis: Observa cómo dot es 1 en 0°, 0 en 90°/270°, -1 en 180°, y valores intermedios.
print("\n¡Ejercicio completo! Experimenta cambiando el vector base o pasos angulares para ver patrones.") 