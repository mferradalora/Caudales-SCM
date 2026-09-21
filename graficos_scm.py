import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

# 1. Cargar el archivo CSV
df = pd.read_csv('caudales_scm.csv')

# 2. Convertir Fecha_Reportada y Hora_Reportada a un solo objeto datetime
df['Fecha_Hora'] = pd.to_datetime(
    df['Fecha_Reportada'] + ' ' + df['Hora_Reportada'],
    format='%d/%m/%Y %H:%M',
    errors='coerce',
)

# Limpiar valores nulos y eliminar registros duplicados de capturas anteriores
df = df.dropna(subset=['Fecha_Hora', 'Caudal_Flow'])
df = df.drop_duplicates(subset=['Nombre_Canal', 'Fecha_Hora']).sort_values(
    'Fecha_Hora'
)

# 3. Directorio para guardar las imágenes
output_dir = 'graficos'
os.makedirs(output_dir, exist_ok=True)

# 4. Generar encabezado del README.md
readme_content = "# 📊 Monitoreo de Caudales SCM\n\n"
readme_content += "Visualización de caudales reportados por la Sociedad de Canal del Maipo.\n\n"
readme_content += (
    "> *Los gráficos se actualizan cada 2 horas.*\n\n---\n\n"
)

# 5. Generar un gráfico por cada Nombre_Canal
canales = sorted(df['Nombre_Canal'].unique())

for canal in canales:
    df_canal = df[df['Nombre_Canal'] == canal]

    plt.figure(figsize=(10, 4.5))
    plt.plot(
        df_canal['Fecha_Hora'],
        df_canal['Caudal_Flow']/1000,
        marker='o',
        markersize=4,
        linestyle='-',
        color='#0366d6',
        linewidth=1.8,
    )

    # --- CAMBIOS EN TÍTULO Y EJES ---
    
    # 1. Título sin la palabra "Caudal:"
    plt.title(f'{canal}', fontsize=14, fontweight='bold', pad=12) 
    
    # 2. Eje Y con la nueva etiqueta
    plt.ylabel('Caudal (m³/s)', fontsize=10) 
    plt.xlabel('Fecha y Hora Reportada', fontsize=10)
    
    # 3. Formato del eje X (una etiqueta por día, en formato dd-mm-yyyy)
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.DayLocator()) # Fuerza una etiqueta diaria
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y')) # Formato dd-mm-yyyy
    
    # Se aumenta ligeramente la rotación y se reduce el tamaño de letra para que los días no se superpongan
    plt.xticks(rotation=45, ha='right', fontsize=9) 
    # ---------------------------------

    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    # Normalizar el nombre del archivo (quitar espacios o caracteres especiales)
    filename = (
        "".join(c if c.isalnum() else "_" for c in canal).strip("_") + ".png"
    )
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=120)
    plt.close()

    # Enlazar la imagen generada dentro del README.md
    readme_content += f"## {canal}\n\n"
    readme_content += f"![{canal}]({filepath})\n\n---\n\n"

# 6. Escribir o sobrescribir el README.md
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)

print("Gráficos y README.md actualizados correctamente.")
