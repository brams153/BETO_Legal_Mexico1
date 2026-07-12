import time
from Beto.utils.config import PROJECT_ROOT, BRONZE_DIR
from Beto.utils.client import obtener_cliente_http
from bs4 import BeautifulSoup


class ExtraerBoletinSCJN:
    def __init__(self):
        # Se conecta la sesión con headers de navegador simulado
        self.session = obtener_cliente_http(es_api=False)

        self.output_dir = BRONZE_DIR / "scjn" / "boletines"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.url_base_dominio = "https://www.scjn.gob.mx"
        self.url_inicial = (
            f"{self.url_base_dominio}/multimedia/boletin-mensual-resoluciones-del-pleno"
        )

    def get_siguiente_pagina_url(self, url_actual):
        print(f"🔎 Buscando enlace de paginación en: {url_actual}")
        try:
            response = self.session.get(url_actual, verify=False, timeout=15)
            if response.status_code != 200:
                print(f"❌ Error al acceder a la página: {response.status_code}")
                return None

            soup = BeautifulSoup(response.content, "html.parser")
            boton_siguiente = soup.find("a", rel="next", href=True)

            if boton_siguiente:
                href = boton_siguiente["href"]
                url_siguiente = (
                    href
                    if href.startswith("http")
                    else f"{self.url_base_dominio}{href}"
                )
                return url_siguiente

            print("🏁 Última página del boletín alcanzada.")
            return None
        except Exception as e:
            print(f"❌ Error en get_siguiente_pagina_url: {e}")
            return None

    def encontrar_pdfs(self, url_pagina):
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


if __name__ == "__main__":
    procesador = ExtraerBoletinSCJN()
    url_a_procesar = procesador.url_inicial
    paginas_a_rastrear = 3

    print(f"🚀 Iniciando scraper de Boletines SCJN de forma modular.\n")

    for cuenta in range(1, paginas_a_rastrear + 1):
        print(f"--- PROCESANDO PÁGINA {cuenta} ---")
        lista_pdfs = procesador.encontrar_pdfs(url_a_procesar)
        print(f"📊 Enlaces PDF detectados: {len(lista_pdfs)}")

        url_siguiente = procesador.get_siguiente_pagina_url(url_a_procesar)
        if not url_siguiente:
            break

        url_a_procesar = url_siguiente
        print()
        time.sleep(2)
