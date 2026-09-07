import os
import requests
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

CANALES = [
    {"id": 1, "nombre": "RÍO MAIPO"},
    {"id": 3, "nombre": "REGADOR SCM"},
    {"id": 50, "nombre": "BT CANAL SAN CARLOS REGANTES"},
    {"id": 20, "nombre": "CANAL EYZAGUIRRE"},
    {"id": 41, "nombre": "CANAL FLORIDA"},
    {"id": 35, "nombre": "CANAL LAS PERDICES"},
    {"id": 37, "nombre": "BT CANAL EL CARMEN"},
    {"id": 38, "nombre": "BT CANAL LA PUNTA"},
    {"id": 39, "nombre": "CANAL LA PÓLVORA"}
]

ARCHIVO_CSV = "caudales_scm.csv"

# Token con fallback. Si defines SCM_BEARER_TOKEN en GitHub Secrets, tomará ese valor.
TOKEN = os.getenv(
    "SCM_BEARER_TOKEN", 
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb21wYW55IjoiU0NNYWlwbyJ9.UYp6RbGqtuyGPaVTpZTmmQaOCHh6fnYvX9Ej8TFWN-o"
)

HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'es-ES,es;q=0.9',
    'authorization': f'Bearer {TOKEN}',
    'referer': 'https://www.scmaipo.cl/canalistas/newCaudales/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36'
}

COOKIES = {
    '_ga': 'GA1.1.2067585923.1784048278',
    '_ga_KWKRVGB706': 'GS2.1.s1785785486$o7$g1$t1785787522$j59$l0$h0',
}

def consultar_y_guardar():
    # Obtener hora oficial de Chile continental
    ahora_chile = datetime.now(ZoneInfo("America/Santiago"))
    fecha_captura = ahora_chile.strftime("%Y-%m-%d")
    hora_captura = ahora_chile.strftime("%H:%M:%S")

    print(f"\n--- Ejecución: {fecha_captura} {hora_captura} (Hora Chile) ---")

    nuevos_registros = []
    
    # Reutilización de conexión mediante Session
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(COOKIES)

    for canal in CANALES:
        canal_id = canal["id"]
        canal_nombre_default = canal["nombre"]
        url_api = f"https://www.scmaipo.cl/api/caudales/{canal_id}/local"

        try:
            response = session.get(url_api, timeout=15)
            
            if response.status_code == 200:
                datos = response.json()
                body = datos.get("body", {})
                
                cid = body.get("id", canal_id)
                nombre = body.get("name", canal_nombre_default)
                flow = body.get("flow", "N/A")
                fecha_rep = body.get("date", "N/A")
                hora_rep = body.get("time", "N/A")

                nuevos_registros.append({
                    "Fecha_Captura": fecha_captura,
                    "Hora_Captura": hora_captura,
                    "ID_Canal": cid,
                    "Nombre_Canal": nombre,
                    "Caudal_Flow": flow,
                    "Fecha_Reportada": fecha_rep,
                    "Hora_Reportada": hora_rep
                })

                print(f"  [ID {cid}] {nombre} -> Flow: {flow} | Reportado: {fecha_rep} {hora_rep}")
            else:
                print(f"  ⚠️ Error HTTP {response.status_code} al consultar ID {canal_id}")

        except Exception as e:
            print(f"  ❌ Error de conexión en ID {canal_id}: {e}")

    if not nuevos_registros:
        print("No se obtuvieron registros en esta ejecución.")
        return

    df_nuevos = pd.DataFrame(nuevos_registros)

    # Cargar CSV previo y descartar duplicados exactos
    if os.path.exists(ARCHIVO_CSV):
        df_existente = pd.read_csv(ARCHIVO_CSV)
        df_final = pd.concat([df_existente, df_nuevos], ignore_index=True)
        # Elimina filas donde el canal reportó exactamente la misma fecha y hora
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
