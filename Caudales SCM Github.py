#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
import csv
import json
from datetime import datetime
import time

# Listado de canales a monitorear con sus IDs
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

ARCHIVO_CSV = "registro_caudales_scm.csv"

# Cabeceras requeridas para la petición
HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'es-ES,es;q=0.9',
    'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb21wYW55IjoiU0NNYWlwbyJ9.UYp6RbGqtuyGPaVTpZTmmQaOCHh6fnYvX9Ej8TFWN-o',
    'priority': 'u=1, i',
    'referer': 'https://www.scmaipo.cl/canalistas/newCaudales/',
    'sec-ch-ua': '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36'
}

COOKIES = {
    '_ga': 'GA1.1.2067585923.1784048278',
    '_ga_KWKRVGB706': 'GS2.1.s1785785486$o7$g1$t1785787522$j59$l0$h0',
}

def inicializar_csv():
    """Crea la estructura del archivo CSV con los campos exactos del JSON."""
    try:
        with open(ARCHIVO_CSV, mode='x', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                "Fecha_Captura", 
                "Hora_Captura", 
                "ID_Canal", 
                "Nombre_Canal", 
                "Caudal_Flow", 
                "Fecha_Reportada", 
                "Hora_Reportada"
            ])
            print(f"✅ Archivo '{ARCHIVO_CSV}' creado con éxito.")
    except FileExistsError:
        pass

def consultar_y_guardar():
    """Realiza la consulta para cada canal y guarda los campos de 'body'."""
    ahora = datetime.now()
    fecha_captura = ahora.strftime("%Y-%m-%d")
    hora_captura = ahora.strftime("%H:%M:%S")

    print(f"\n--- Ejecución: {fecha_captura} {hora_captura} ---")

    for canal in CANALES:
        canal_id = canal["id"]
        canal_nombre_default = canal["nombre"]
        url_api = f"https://www.scmaipo.cl/api/caudales/{canal_id}/local"

        try:
            response = requests.get(url_api, headers=HEADERS, cookies=COOKIES, timeout=15)
            
            if response.status_code == 200:
                datos = response.json()
                
                # Extraemos el objeto interior 'body'
                body = datos.get("body", {})
                
                cid = body.get("id", canal_id)
                nombre = body.get("name", canal_nombre_default)
                flow = body.get("flow", "N/A")
                fecha_rep = body.get("date", "N/A")
                hora_rep = body.get("time", "N/A")

                # Escribimos los datos extraídos en el CSV
                with open(ARCHIVO_CSV, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        fecha_captura, 
                        hora_captura, 
                        cid, 
                        nombre, 
                        flow, 
                        fecha_rep, 
                        hora_rep
                    ])

                print(f"  [ID {cid}] {nombre} -> Flow: {flow} | Reportado: {fecha_rep} {hora_rep}")
            else:
                print(f"  ⚠️ Error HTTP {response.status_code} al consultar ID {canal_id}")

        except Exception as e:
            print(f"  ❌ Error de conexión en ID {canal_id}: {e}")
        
        # Pausa de 1 segundo entre peticiones de la misma ronda
        time.sleep(1)

if __name__ == "__main__":
    inicializar_csv()
    consultar_y_guardar()
    print("✅ Ejecución completada.")

