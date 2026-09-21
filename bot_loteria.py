import os
import re
import time
import unicodedata
import cloudscraper
from bs4 import BeautifulSoup

# TOKEN Y CANAL DE TELEGRAM
BOT_TOKEN = "8349151512:AAHH2W4ljSn5aOr66QMMQFTSEsNFNFAAdQU"
CHAT_ID = "@opdoradaresultados"
HISTORIAL_FILE = "enviados.txt"
URL_WEB = "https://loteriadehoy.com/"

MAPEO_LOTERIAS = {
    "LOTTO ACTIVO": "LOTTO ACTIVO",
    "LA GRANJITA": "LA GRANJITA",
    "SELVA PLUS": "SELVA PLUS",
    "GUACHARO ACTIVO": "GUACHARO ACTIVO",
    "GUACHARO": "GUACHARO ACTIVO",
    "EL GUACHARITO MILLONARIO": "EL GUACHARITO MILLONARIO",
    "LOTTO INTERNACIONAL": "LOTTO INTERNACIONAL",
    "LA RUCA": "LA RUCA",
    "TRIO ACTIVO": "TRIO ACTIVO"
}

EMOJIS_ANIMALES = {
    "DELFIN": "🐬", "BALLENA": "🐳", "CARNERO": "🐏", "TORO": "🐂", "CIEMPIES": "🐛",
    "ALACRAN": "🦂", "LEON": "🦁", "RANA": "🐸", "PERICO": "🦜", "TIGRE": "🐯",
    "GATO": "🐱", "CABALLO": "🐴", "MONO": "🐒", "PALOMA": "🕊️", "ZORRO": "🦊",
    "OSO": "🐻", "PAVOREAL": "🦚", "AGUILA": "🦅", "CHIVO": "🐐", "PERRO": "🐶",
    "ZAMURO": "🦅", "ELEFANTE": "🐘", "CAIMAN": "🐊", "GALLO": "🐓", "IGUANA": "🦎",
    "CAMELLO": "🐫", "CEBRA": "🦓", "PORCO": "🐖", "TURPIAL": "🐤", "CHIGUIRE": "🦙",
    "VENADO": "🦌", "CULEBRA": "🐍", "TUCAN": "🦜", "TIBURON": "🦈", "PUERCOESPIN": "🦔",
    "GALLINA": "🐔"
}

def normalizar_texto(texto):
    if not texto:
        return ""
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto.upper().strip()

def cargar_historial():
    if not os.path.exists(HISTORIAL_FILE):
        return set()
    with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def guardar_historial(clave):
    with open(HISTORIAL_FILE, "a", encoding="utf-8") as f:
        f.write(f"{clave}\n")

def enviar_telegram(scraper, mensaje):
    url_api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "HTML"
    }
    try:
        # Timeout agresivo de 5s para envío ultra rápido
        res = scraper.post(url_api, json=payload, timeout=5)
        return res.status_code == 200
    except Exception as e:
        print(f"Error de conexión con Telegram: {e}")
        return False

def extraer_resultados(scraper):
    try:
        # Petición directa con timeout reducido a 8s para acelerar respuesta
        response = scraper.get(URL_WEB, timeout=8)
        response.encoding = 'utf-8'
        if response.status_code != 200:
            print(f"📌 Web respondió status: {response.status_code}")
            return []
    except Exception as e:
        print(f"📌 Error de conexión con la web: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    resultados = []

    bloques = soup.find_all(["div", "article", "section", "tr"])

    for bloque in bloques:
        texto = bloque.get_text(separator=" ", strip=True)
        if not texto or len(texto) > 250:
            continue

        texto_norm = normalizar_texto(texto)

        for clave_loteria, nombre_oficial in MAPEO_LOTERIAS.items():
            if clave_loteria in texto_norm:
                hora_match = re.search(r'\b(0?[1-9]|1[0-2]):[0-5][0-9]\s*(AM|PM)\b', texto_norm)
                num_animal_match = re.search(r'\b(\d{1,3})\s*[-–—]?\s*([A-Z]{3,})\b', texto_norm)

                if hora_match and num_animal_match:
                    hora = hora_match.group(0)
                    num = num_animal_match.group(1)
                    animal = num_animal_match.group(2)

                    if animal in ["RESULTADOS", "LOTERIA", "HOY", "ANIMALITOS", "DATOS", "INICIO"]:
                        continue

                    clave_historial = f"{nombre_oficial}_{hora}_{num}_{animal}"
                    resultados.append({
                        "clave": clave_historial,
                        "loteria": nombre_oficial,
                        "hora": hora,
                        "num": num,
                        "animal": animal
                    })

    return resultados

if __name__ == "__main__":
    hora_ejecucion = time.strftime("%H:%M:%S")
    print(f"🤖 [{hora_ejecucion}] Escaneando loterías en tiempo real...")

    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
    historial = cargar_historial()
    resultados = extraer_resultados(scraper)

    resultados_unicos = {r["clave"]: r for r in resultados}.values()

    enviados_count = 0
    for r in resultados_unicos:
        if r["clave"] not in historial:
            emoji = EMOJIS_ANIMALES.get(r["animal"], "🎰")
            mensaje = (
                f"🎰 <b>{r['loteria']}</b>\n"
                f"⏰ Hora: <b>{r['hora']}</b>\n"
                f"💥 Resultado: <b>{r['num']} - {r['animal']}</b> {emoji}"
            )

            if enviar_telegram(scraper, mensaje):
                print(f"⚡ [PUBLICACIÓN INMEDIATA]: {r['loteria']} | {r['hora']} -> {r['num']} - {r['animal']}")
                guardar_historial(r["clave"])
                historial.add(r["clave"])
                enviados_count += 1
                time.sleep(0.5) # Pausa mínima para acelerar ráfagas de sorteos

    if enviados_count == 0:
        print(f"🟢 [{hora_ejecucion}] Bot operativo. Sin resultados nuevos publicados a esta hora.")
    
