import os
import sys
import requests
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# Mapeo histórico de nombres para mantener compatibilidad con graficos_scm.py y README.md
NOMBRES_CANALES = {
    1: "RÍO MAIPO",
    3: "REGADOR SCM",
    50: "BT CANAL SAN CARLOS REGANTES",
    20: "CANAL EYZAGUIRRE",
    29: "CANAL SAN FRANCISCO",
    41: "CANAL FLORIDA",
    35: "CANAL LAS PERDICES",
    37: "BT CANAL EL CARMEN",
    38: "BT CANAL LA PUNTA",
    39: "CANAL LA PÓLVORA",
    1028: "CANAL BATUCO",
    90: "PTAP CHAMISERO",
    1029: "CANAL COLINA",
    1032: "CANAL LO CASTRO",
    1033: "CANAL LO SOLAR"
}

# IDs que deseas monitorear activamente (puedes añadir los nuevos IDs si deseas graficarlos)
CANALES_A_EXTRAER = [1, 3, 50, 20, 29, 41, 35, 37, 38, 39, 1028, 90, 1029, 1032, 1033]

ARCHIVO_CSV = "caudales_scm.csv"
URL_API = "https://servicios.scmaipo.cl/caudales/api/"

TOKEN = os.getenv(
    "SCM_BEARER_TOKEN", 
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb21wYW55IjoiU0NNYWlwbyJ9.UYp6RbGqtuyGPaVTpZTmmQaOCHh6fnYvX9Ej8TFWN-o"
)

HEADERS = {
    "accept": "*/*",
    "accept-language": "es-ES,es;q=0.9",
    "authorization": f"Bearer {TOKEN}",
    "origin": "https://www.scmaipo.cl",
    "referer": "https://www.scmaipo.cl/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36"
}

def consultar_y_guardar():
    ahora_chile = datetime.now(ZoneInfo("America/Santiago"))
    fecha_captura = ahora_chile.strftime("%Y-%m-%d")
    hora_captura = ahora_chile.strftime("%H:%M:%S")

    print(f"\n--- Ejecución: {fecha_captura} {hora_captura} (Hora Chile) ---")

    try:
        response = requests.get(URL_API, headers=HEADERS, timeout=20)
        
        if response.status_code != 200:
            print(f"❌ Error HTTP {response.status_code} al consultar la API de SCM")
            sys.exit(1)

        datos = response.json()
        estaciones = datos.get("body", [])

    except Exception as e:
        print(f"❌ Error de conexión con servicios.scmaipo.cl: {e}")
        sys.exit(1)

    nuevos_registros = []

    for item in estaciones:
        cid = item.get("id_punto")
        
        # Filtramos solo los canales requeridos (o quita esta condición si deseas guardar todos)
        if CANALES_A_EXTRAER and cid not in CANALES_A_EXTRAER:
            continue

        punto_nombre = NOMBRES_CANALES.get(cid, item.get("punto", f"CANAL_{cid}"))
        valor = item.get("valor", 0.0)
        fecha_hora_str = item.get("fecha_hora", "")

        # Procesamiento del timestamp telemétrico ("2026-11-10T08:00:00.000Z")
        if "T" in fecha_hora_str:
            dt_reportada = datetime.fromisoformat(fecha_hora_str.replace("Z", ""))
            fecha_rep = dt_reportada.strftime("%d/%m/%Y")
            hora_rep = dt_reportada.strftime("%H:%M")
        else:
            fecha_rep = "N/A"
            hora_rep = "N/A"

        nuevos_registros.append({
            "Fecha_Captura": fecha_captura,
            "Hora_Captura": hora_captura,
            "ID_Canal": cid,
            "Nombre_Canal": punto_nombre,
            "Caudal_Flow": float(valor) if valor is not None else 0.0,
            "Fecha_Reportada": fecha_rep,
            "Hora_Reportada": hora_rep
        })

        print(f"  [ID {cid}] {punto_nombre} -> Caudal/Valor: {valor} | Reportado: {fecha_rep} {hora_rep}")

    if not nuevos_registros:
        print("⚠️ No se procesaron registros válidos en esta ejecución.")
        return

    df_nuevos = pd.DataFrame(nuevos_registros)

    # Cargar CSV previo y descartar duplicados exactos
    if os.path.exists(ARCHIVO_CSV):
        df_existente = pd.read_csv(ARCHIVO_CSV)
        df_final = pd.concat([df_existente, df_nuevos], ignore_index=True)
        df_final = df_final.drop_duplicates(
            subset=["ID_Canal", "Fecha_Reportada", "Hora_Reportada"], 
            keep="last"
        )
    else:
        df_final = df_nuevos

    df_final.to_csv(ARCHIVO_CSV, index=False, encoding="utf-8")
    print(f"\n✅ Proceso finalizado. Total acumulado en CSV: {len(df_final)} filas.")

if __name__ == "__main__":
    consultar_y_guardar()
