import requests
from bs4 import BeautifulSoup
import time
import urllib3
from pathlib import Path
from pdf2image import convert_for_path

# Importación de la configuración centralizada de tu entorno
from Beto.utils.config import PROJECT_ROOT, BRONZE_DIR

# Desactivar advertencias de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ExtraerBoletinSCJN:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            }
        )

        # --- LÓGICA DE RUTAS CENTRALIZADA ---
        self.output_dir = BRONZE_DIR / "scjn_boletines"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.url_base_dominio = "https://www.scjn.gob.mx"
        self.url_inicial = (
            f"{self.url_base_dominio}/multimedia/boletin-mensual-resoluciones-del-pleno"
        )

    def get_siguiente_pagina_url(self, url_actual):
        """
        Analiza la página actual y extrae el enlace hacia la página siguiente
        utilizando el atributo estándar de paginación rel='next'.
        """
        print(f"🔎 Buscando enlace de paginación en: {url_actual}")
        try:
            # Corregido: Usamos la sesión con cabeceras y omitimos la verificación SSL
            response = self.session.get(url_actual, verify=False, timeout=15)
            if response.status_code != 200:
                print(f"❌ Error al acceder a la página: {response.status_code}")
                return None

            soup = BeautifulSoup(response.content, "html.parser")

            # Buscamos específicamente el botón 'Siguiente' documentado
            boton_siguiente = soup.find("a", rel="next", href=True)

            if boton_siguiente:
                href = boton_siguiente["href"]
                # Si la ruta es relativa, le pegamos el dominio de la SCJN
                url_siguiente = (
                    href
                    if href.startswith("http")
                    else f"{self.url_base_dominio}{href}"
                )
                return url_siguiente

            print("🏁 Se ha alcanzado la última página del boletín.")
            return None

        except Exception as e:
            print(f"❌ Error en get_siguiente_pagina_url: {e}")
            return None

    def encontrar_pdfs(self, url_pagina):
        """Busca y extrae todos los enlaces a archivos PDF en la página proporcionada"""
        print(f"📂 Buscando archivos PDF en: {url_pagina}")
        try:
            response = self.session.get(url_pagina, verify=False, timeout=15)
            soup = BeautifulSoup(response.content, "html.parser")
            pdf_links = set()

            for a in soup.find_all("a", href=True):
                href = a["href"]
                if ".pdf" in href.lower():
                    full_url = (
                        href
                        if href.startswith("http")
                        else f"{self.url_base_dominio}{href}"
                    )
                    pdf_links.add(full_url)

            return list(pdf_links)
        except Exception as e:
            print(f"❌ Error al buscar PDFs: {e}")
            return []


# --- EJECUCIÓN CONTROLADA ---
if __name__ == "__main__":
    procesador = ExtraerBoletinSCJN()

    # Prueba de concepto: Vamos a rastrear el flujo a lo largo de 3 páginas
    url_a_procesar = procesador.url_inicial
    paginas_a_rastrear = 3

    print(f"🚀 Iniciando scraper de Boletines SCJN de forma modular.\n")

    for cuenta in range(1, paginas_a_rastrear + 1):
        print(f"--- PROCESANDO PÁGINA {cuenta} ---")

        # 1. Encontrar los PDFs de la página actual
        lista_pdfs = procesador.encontrar_pdfs(url_a_procesar)
        print(f"📊 Enlaces PDF detectados en esta página: {len(lista_pdfs)}")
        for pdf in lista_pdfs:
            print(f"   -> {pdf}")

        # 2. Obtener de forma dinámica el enlace para la siguiente iteración
        url_siguiente = procesador.get_siguiente_pagina_url(url_a_procesar)

        if not url_siguiente:
            break

        # Actualizamos la variable de control para el siguiente ciclo
        url_a_procesar = url_siguiente
        print()
        time.sleep(2)  # Pausa preventiva de cortesía al servidor judicial
