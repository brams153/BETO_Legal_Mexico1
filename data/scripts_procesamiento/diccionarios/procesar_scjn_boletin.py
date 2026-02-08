from PIL import Image
from pathlib import Path
from pdf2image import convert_from_path
#import pytesseract
import requests
from bs4 import BeautifulSoup
import os
import time
import urllib3
import pymupdf
import pikepdf
# Desactivar advertencias de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
OUTPUT_DIR = "data/sin limpiar/scjn"
"""
Ejemplo basico para comprmir pdf
pdf=pikepdf.open('pdf_comprimido.pdf')
pdf.save("pdf_comprimido",optimize_version=True)
pdf.close() 
"""
class Extraer_scjn:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        })

    def get_siguiente_pagina_url(self):
        URL = "https://www.scjn.gob.mx/multimedia/boletin-mensual-resoluciones-del-pleno"
        #url principal y pagina 0 https://www.scjn.gob.mx/multimedia/boletin-mensual-resoluciones-del-pleno
        #url 1 y subsecuentes https://www.scjn.gob.mx/multimedia/boletin-mensual-resoluciones-del-pleno?page=1 //page=2...page=n
        """El objeto al que se quiere acceder e iterar tiene el siguiente formato:
        <a href="/multimedia/boletin-mensual-resoluciones-del-pleno?page=3" title="Ir a la página siguiente" rel="next">
            <span class="sr-only">Siguiente página</span>
            <span aria-hidden="true">››</span>
          </a>
        El link tiene la referencia href se pueden imprimir todos los href y filtar despues  
        """
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        for a_href in soup.find_all("a", href=True):
            print(a_href["href"])
        #En html href es el referenciador <a> contiene hipervinculos para el usuario por sintaxis y estandar debe estar aqui
if __name__ == "__main__":
    procesador = Extraer_scjn()
    url_sig_pag=procesador.get_siguiente_pagina_url()
       
    time.sleep(2)        
    '''def encontar_pdfs(self, url):
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
            
            return list(pdf_links)'''

      