import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ARCHIVO_CSV = "caudales_scm.csv"
CARPETA_GRAFICOS = "graficos"
ARCHIVO_README = "README.md"

os.makedirs(CARPETA_GRAFICOS, exist_ok=True)

def generar_graficos_y_readme():
    if not os.path.exists(ARCHIVO_CSV):
        print(f"❌ No se encontró el archivo {ARCHIVO_CSV}")
        return

    df = pd.read_csv(ARCHIVO_CSV)

    # 1. Unificar y parsear la serie temporal
    df['datetime'] = pd.to_datetime(
        df['Fecha_Reportada'] + ' ' + df['Hora_Reportada'], 
        format='%d/%m/%Y %H:%M', 
        errors='coerce'
    )
    df = df.dropna(subset=['datetime']).sort_values('datetime')

    canales = df['Nombre_Canal'].unique()
    canales_graficados = []

    for canal in sorted(canales):
        df_canal = df[df['Nombre_Canal'] == canal].copy()
        
        # Eliminar posibles duplicados temporales por seguridad
        df_canal = df_canal.drop_duplicates(subset=['datetime'])

        if df_canal.empty:
            continue

        # 2. Manejo de unidades: l/s a m3/s (salvo REGADOR SCM que se reporta en l/s/regador)
        if "REGADOR" in canal.upper():
            caudal_plot = df_canal['Caudal_Flow']
            label_y = "Caudal (l/s/regador)"
        else:
            caudal_plot = df_canal['Caudal_Flow'] / 1000.0
            label_y = "Caudal (m³/s)"

        # 3. Configuración de la figura
        fig, ax = plt.subplots(figsize=(12, 4.5), dpi=150)
        
        ax.plot(
            df_canal['datetime'], 
            caudal_plot, 
            marker='o', 
            markersize=3, 
            color='#0066cc', 
            linewidth=1.5
        )

        ax.set_title(canal, fontsize=13, fontweight='bold', pad=12)
        ax.set_ylabel(label_y, fontsize=10)
        ax.set_xlabel("Fecha", fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.5)

        # 4. Control del espaciado de fechas en el eje X
        rango_dias = (df_canal['datetime'].max() - df_canal['datetime'].min()).days

        # Ajuste de densidad: si la serie abarca muchos meses, separamos cada N días
        if rango_dias <= 14:
            intervalo = 1  # 1 etiqueta por día si la ventana es de 2 semanas
        elif rango_dias <= 45:
            intervalo = 3  # Cada 3 días para series mensuales
        elif rango_dias <= 90:
            intervalo = 5  # Cada 5 días (ideal para la serie de ~3 meses actual)
        else:
            intervalo = 10 # Cada 10 días para series mayores

        ax.xaxis.set_major_locator(mdates.DayLocator(interval=intervalo))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        
        # Rotación y ajuste automático para evitar solapamientos
        fig.autofmt_xdate(rotation=45, ha='right')

        # Nombre del archivo PNG (normalizado sin caracteres especiales)
        nombre_archivo = canal.replace(" ", "_").replace("Ó", "O").replace("Í", "I") + ".png"
        ruta_salida = os.path.join(CARPETA_GRAFICOS, nombre_archivo)
        
        plt.tight_layout()
        plt.savefig(ruta_salida)
        plt.close(fig)

        canales_graficados.append((canal, ruta_salida))
        print(f"  [OK] Gráfico generado: {nombre_archivo} (Etiquetas cada {intervalo} día/s)")

    # 5. Reconstruir README.md
    with open(ARCHIVO_README, "w", encoding="utf-8") as f:
        f.write("# 📊 Monitoreo de Caudales SCM\n\n")
        f.write("Visualización de caudales reportados por la Sociedad de Canal del Maipo.\n\n")
        f.write("> *Los gráficos se actualizan automáticamente cada 2 horas.*\n\n---\n\n")
        
        for canal, ruta in canales_graficados:
            f.write(f"## {canal}\n\n")
            f.write(f"![{canal}]({ruta})\n\n---\n\n")

    print("\n✅ Gráficos y README.md actualizados correctamente.")

if __name__ == "__main__":
    generar_graficos_y_readme()
