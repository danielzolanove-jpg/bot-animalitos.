import os
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = "8349151512:AAHH2W4ljSn5a0r66QMMQFTSEsNFNFAAdQU"
CHAT_ID = "@Opdorada"
ARCHIVO_ESTADO = "ultimo_estado.txt"

# Fuentes oficiales a monitorear
FUENTES = {
    "Lotto Activo": "https://www.lottoactivo.com/resultados/animalitos/",
    "La Granjita": "https://lagranjita.com/",
    "Guácharo Activo": "https://nitter.net/guacharoactivo"  # Espejo Nitter para Twitter/X
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
}

def consultar_sitio(url):
    try:
        session = requests.Session()
        res = session.get(url, headers=HEADERS, timeout=20)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            contenedor = soup.find('main') or soup.find('article') or soup.find('body')
            if contenedor:
                return contenedor.get_text(separator="\n", strip=True)[:3000]
        else:
            print(f"Error HTTP {res.status_code} en {url}")
    except Exception as e:
        print(f"Error consultando {url}: {e}")
    return ""

def enviar_telegram(mensaje):
    url_api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "HTML"
    }
    try:
        res = requests.post(url_api, data=payload)
        if res.status_code == 200:
            print("Notificación enviada a Telegram.")
        else:
            print(f"Error Telegram: {res.text}")
    except Exception as e:
        print(f"Error de conexión Telegram: {e}")

if __name__ == "__main__":
    estado_actual_partes = []
    
    # Consultar cada una de las 3 loterías
    for nombre, url in FUENTES.items():
        contenido = consultar_sitio(url)
        estado_actual_partes.append(f"--- {nombre} ---\n{contenido}")

    estado_actual_completo = "\n".join(estado_actual_partes)

    estado_anterior = ""
    if os.path.exists(ARCHIVO_ESTADO):
        with open(ARCHIVO_ESTADO, "r", encoding="utf-8") as f:
            estado_anterior = f.read()

    # Comparar si hubo cambios en alguna de las fuentes
    if estado_actual_completo and estado_actual_completo != estado_anterior:
        mensaje = (
            f"🎰 <b>¡NUEVOS RESULTADOS DETECTADOS!</b>\n\n"
            f"Se han registrado novedades en las páginas oficiales:\n\n"
            f"🔹 <b>Lotto Activo:</b> https://www.lottoactivo.com/resultados/animalitos/\n"
            f"🔹 <b>La Granjita:</b> https://lagranjita.com/\n"
            f"🔹 <b>Guácharo Activo:</b> https://x.com/guacharoactivo\n\n"
            f"📲 <i>Consulta el canal para ver el boletín de sorteos.</i>"
        )
        enviar_telegram(mensaje)
        
        with open(ARCHIVO_ESTADO, "w", encoding="utf-8") as f:
            f.write(estado_actual_completo)
    else:
        print("Sin cambios en las loterías oficiales.")
