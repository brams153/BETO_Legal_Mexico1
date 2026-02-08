import requests
from bs4 import BeautifulSoup
import time
import urllib3
from pathlib import Path  # <--- Importación clave para portabilidad

# Desactivar advertencias de SSL (Mantenemos tu configuración original)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# 1. DETECCIÓN DINÁMICA DE RUTAS
# ==========================================
def get_project_root():
    """
    Busca la carpeta raíz del proyecto subiendo niveles hasta encontrar
    indicadores clave como '.github', 'data' o '.venv'.
    """
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if (parent / '.github').exists() or (parent / 'data').exists():
            return parent
    return current_path.parent

# Definimos la raíz y la ruta de salida
PROJECT_ROOT = get_project_root()
OUTPUT_DIR = PROJECT_ROOT / "data" / "sin limpiar" / "diccionarios"

# Creamos el directorio si no existe (parents=True crea las carpetas intermedias)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"📂 Raíz del proyecto: {PROJECT_ROOT}")
print(f"📂 Guardando descargas en: {OUTPUT_DIR}")

# ==========================================
# 2. LÓGICA DEL SCRAPER (UNAMVacuum)
# ==========================================

class UNAMVacuum:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        })

    def get_tomos_urls(self):
        """Lista manual de los 8 tomos"""
        return [
            "https://biblio.juridicas.unam.mx/bjv/detalle-libro/1168-diccionario-juridico-mexicano-t-i-a-b",
            "https://biblio.juridicas.unam.mx/bjv/detalle-libro/1169-diccionario-juridico-mexicano-t-ii-c-ch",
            "https://biblio.juridicas.unam.mx/bjv/detalle-libro/1170-diccionario-juridico-mexicano-t-iii-d",
            "https://biblio.juridicas.unam.mx/bjv/detalle-libro/1171-diccionario-juridico-mexicano-t-iv-e-h",
            "https://biblio.juridicas.unam.mx/bjv/detalle-libro/1172-diccionario-juridico-mexicano-t-v-i-j",
            "https://biblio.juridicas.unam.mx/bjv/detalle-libro/1173-diccionario-juridico-mexicano-t-vi-l-o",
            "https://biblio.juridicas.unam.mx/bjv/detalle-libro/1174-diccionario-juridico-mexicano-t-vii-p-reo",
            "https://biblio.juridicas.unam.mx/bjv/detalle-libro/1175-diccionario-juridico-mexicano-t-viii-rep-z"
        ]

    def find_pdfs_in_page(self, url):
        """Busca CUALQUIER enlace que parezca un PDF"""
        print(f"🔎 Analizando: {url}")
        try:
            response = self.session.get(url, verify=False, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            pdf_links = set() # Usamos set para evitar duplicados
            
            # Buscar en todas las etiquetas 'a'
            for a in soup.find_all('a', href=True):
                href = a['href']
                # Si contiene .pdf (sin importar mayúsculas/minúsculas o query params)
                if '.pdf' in href.lower():
                    # Construir URL absoluta
                    if href.startswith('/'):
                        full_url = f"https://biblio.juridicas.unam.mx{href}"
                    elif not href.startswith('http'):
                        full_url = f"https://biblio.juridicas.unam.mx/bjv/{href}"
                    else:
                        full_url = href
                    
                    pdf_links.add(full_url)
            
            return list(pdf_links)

        except Exception as e:
            print(f"❌ Error conectando a {url}: {e}")
            return []

    def download_file(self, url, folder, prefix, index):
        """Descarga genérica. Recibe 'folder' como objeto Path."""
        try:
            # Intentar sacar nombre original, si falla usar genérico
            filename = url.split('/')[-1].split('?')[0]
            if not filename.endswith('.pdf'):
                filename = f"documento_{index}.pdf"
            
            # Nombre final: 1168_01_archivo.pdf
            final_name = f"{prefix}_{index:02d}_{filename}"
            
            # Construcción de ruta segura con pathlib
            local_path = folder / final_name 
            
            if local_path.exists():
                print(f"   ⏭️ Ya existe: {final_name}")
                return

            print(f"   ⬇️ Descargando ({index}): {final_name}...")
            r = self.session.get(url, stream=True, verify=False)
            
            # 'open' funciona perfectamente con objetos Path en Python 3.6+
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            
        except Exception as e:
            print(f"   ❌ Falló descarga de {url}: {e}")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    spider = UNAMVacuum()
    tomos = spider.get_tomos_urls()
    
    print(f"🚀 Iniciando extracción de {len(tomos)} tomos.\n")

    for link in tomos:
        # Extraer ID del libro (ej: 1168)
        book_id = link.split('detalle-libro/')[1].split('-')[0]
        
        # 1. Encontrar TODOS los PDFs de esa página
        pdfs = spider.find_pdfs_in_page(link)
        
        if not pdfs:
            print(f"⚠️ ALERTA: No se encontraron PDFs en el tomo {book_id}.")
        else:
            print(f"   ✅ Encontrados {len(pdfs)} archivos PDF en este tomo.")
            # 2. Descargarlos todos
            for i, pdf_url in enumerate(pdfs):
                # Pasamos OUTPUT_DIR (que ya es un Path object)
                spider.download_file(pdf_url, OUTPUT_DIR, book_id, i+1)
        
        print("-" * 50)
        time.sleep(2)