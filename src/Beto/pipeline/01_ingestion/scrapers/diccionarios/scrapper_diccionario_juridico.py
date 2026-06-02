import time
from Beto.utils.config import PROJECT_ROOT, BRONZE_DIR
from Beto.utils.client import obtener_cliente_http
from bs4 import BeautifulSoup


OUTPUT_DIR = BRONZE_DIR / "diccionarios"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"📂 Raíz del proyecto: {PROJECT_ROOT}")
print(f"📂 Guardando descargas en: {OUTPUT_DIR}")


class UNAMVacuum:
    def __init__(self):
        # Corregido: Consumimos la sesión web desde la utilidad global
        self.session = obtener_cliente_http(es_api=False)

    def get_tomos_urls(self):
        """Lista manual de los 8 tomos del Diccionario Jurídico"""
        return [
            "https://biblio.juridicas.unam.mx/bjv/detalle-libro/1168-diccionario-juridico-mexicano-t-i-a-b",
            "https://biblio.juridicas.unam.mx/bjv/detalle-libro/1169-diccionario-juridico-mexicano-t-ii-c-ch",
            "https://biblio.juridicas.unam.mx/bjv/detalle-libro/1170-diccionario-juridico-mexicano-t-iii-d",
            "https://biblio.juridicas.unam.mx/bjv/detalle-libro/1171-diccionario-juridico-mexicano-t-iv-e-h",
            "https://biblio.juridicas.unam.mx/bjv/detalle-libro/1172-diccionario-juridico-mexicano-t-v-i-j",
            "https://biblio.juridicas.unam.mx/bjv/detalle-libro/1173-diccionario-juridico-mexicano-t-vi-l-o",
            "https://biblio.juridicas.unam.mx/bjv/detalle-libro/1174-diccionario-juridico-mexicano-t-vii-p-reo",
            "https://biblio.juridicas.unam.mx/bjv/detalle-libro/1175-diccionario-juridico-mexicano-t-viii-rep-z",
        ]

    def find_pdfs_in_page(self, url):
        """Busca cualquier enlace que apunte a un archivo PDF"""
        print(f"🔎 Analizando: {url}")
        try:
            response = self.session.get(url, verify=False, timeout=15)
            soup = BeautifulSoup(response.content, "html.parser")
            pdf_links = set()

            for a in soup.find_all("a", href=True):
                href = a["href"]
                if ".pdf" in href.lower():
                    if href.startswith("/"):
                        full_url = f"https://biblio.juridicas.unam.mx{href}"
                    elif not href.startswith("http"):
                        full_url = f"https://biblio.juridicas.unam.mx/bjv/{href}"
                    else:
                        full_url = href
                    pdf_links.add(full_url)

            return list(pdf_links)
        except Exception as e:
            print(f"❌ Error conectando a {url}: {e}")
            return []

    def download_file(self, url, folder, prefix, index):
        """Descarga el PDF usando streaming para proteger la RAM"""
        try:
            filename = url.split("/")[-1].split("?")[0]
            if not filename.endswith(".pdf"):
                filename = f"documento_{index}.pdf"

            final_name = f"{prefix}_{index:02d}_{filename}"
            local_path = folder / final_name

            if local_path.exists():
                print(f"   Skip ⏭️ Ya existe: {final_name}")
                return

            print(f"   ⬇️ Descargando ({index}): {final_name}...")
            r = self.session.get(url, stream=True, verify=False, timeout=30)

            with open(local_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        except Exception as e:
            print(f"   ❌ Falló descarga de {url}: {e}")


if __name__ == "__main__":
    spider = UNAMVacuum()
    tomos = spider.get_tomos_urls()
    print(f"🚀 Iniciando extracción de {len(tomos)} tomos.\n")

    for link in tomos:
        book_id = link.split("detalle-libro/")[1].split("-")[0]
        pdfs = spider.find_pdfs_in_page(link)

        if not pdfs:
            print(f"⚠️ ALERTA: No se encontraron PDFs en el tomo {book_id}.\n")
        else:
            print(f"   ✅ Encontrados {len(pdfs)} archivos PDF en el tomo {book_id}.")
            for i, pdf_url in enumerate(pdfs, start=1):
                spider.download_file(pdf_url, OUTPUT_DIR, book_id, i)
                time.sleep(1)
            print()
