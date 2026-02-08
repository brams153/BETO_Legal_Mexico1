import json  
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
import traceback
import pandas as pd

class Extraer_scjn:
    
    def __init__(self):
        self.session = requests.Session()
         
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        })
        self.pagina_n=0
        """Aquí pagina_n sera un atributo de self para poder acceder facilmente a él en métodos subsecuentes,se inicializa en 0 y la idea es iterarlo para obtener muchos archivos"""
        self.params={"page": self.pagina_n,"offset": 0,"limit":1000}
        self.url_base="https://bicentenario.scjn.gob.mx/repositorio-scjn/api/v1/engroses/"
        self.diccionario_completo = {}
    
    def request_api_ids(self):
        """Esta funcion primero conecta la api para obtener los ids de la pagina con .json(),si el http no da error(valor 200),entonces genera un diccionario con el formato:
        diccionario={id:url_api_id}"""
        API_URL = "https://bicentenario.scjn.gob.mx/repositorio-scjn/api/v1/engroses/ids"
        params = self.params
        #payload = {"parametros": {}, "limit": 100,"offset": 0}
    
        try:
            page=requests.get(API_URL,headers=self.session.headers,params=params,verify=False)
            if page.status_code == 200:
                lista_ids = page.json()
                # iniciar diccionario vacio y crear mapeo id -> url
                def generar_dic_apiurl(lista_contiene_ids):
                    dict_ids_urls = {}
                    base = self.url_base 
                    #self.url_base="https://bicentenario.scjn.gob.mx/repositorio-scjn/api/v1/engroses/"
                    for id in lista_contiene_ids:
                        urli=base+id
                        dict_ids_urls[id]=urli
                    return dict_ids_urls
                self.diccionario_ids_urls = generar_dic_apiurl(lista_ids) 
                print(f"Datos guardados en la instancia. IDs: {len(self.diccionario_ids_urls)}", flush=True)
            else:
                print(f"Error: {page.status_code}")
        except Exception as e:
            print(f"Ocurrió un error: {e}")
    def obtener_urls_docx(self):
        """La idea es iterar el self.diccionario_ids_urls para obtener un diccionarios que use el id y el valor sea el url para el docx (no confundir con el API_URL)."""
        dic_apiurl = self.diccionario_ids_urls
        lista_parametros_a_filtrar = ["urlInternet", "expediente"]  # queremos solo tener expediente como identificador
        resultados = {}
        for clave, valor in dic_apiurl.items():
            try:
                request_urli = self.session.get(valor, headers=self.session.headers, verify=False, timeout=10)
                data = request_urli.json()
                dict_filtrado = {k: v for k, v in data.items() if k in lista_parametros_a_filtrar}
                #dict_filtrado["id"] = clave  # Añade id al diccionario
                resultados[clave] = dict_filtrado
            except Exception as e:
                print(f"Error al obtener {clave}: {e}")

        self.dic_url_docx = resultados
        return resultados
    def iterar_paginas(self):
        contador_bucle = 0
        print("Iniciando extracción masiva...", flush=True)
        
        while contador_bucle < 50:
        #while contador_bucle < 260:
            self.pagina_n = self.pagina_n + 1
            self.params["page"] = self.pagina_n 
            self.request_api_ids()
            datos_pagina_actual = self.obtener_urls_docx()

            if datos_pagina_actual:
                self.diccionario_completo.update(datos_pagina_actual)
                print(f"Acumulados hasta ahora: {len(self.diccionario_completo)} registros.")
            
            contador_bucle += 1
            time.sleep(1) 

    def guardar_resultados(self):
        """Guarda el diccionario completo en un archivo JSON"""
        ruta_del_script = os.path.dirname(os.path.abspath(__file__))
        os.chdir(ruta_del_script)
        ruta_carpeta = Path(r"C:\Users\DELL\Downloads\proyectos\Beto_Legal_Mexico\data\sin limpiar\scjn")
        nombre_archivo = "datos_limpios.json"
        ruta_final = ruta_carpeta / nombre_archivo
        try:
            with open(ruta_final, 'w', encoding='utf-8') as f:
                json.dump(self.diccionario_completo, f, ensure_ascii=False, indent=4)
            print(f"¡Éxito! Se guardaron {len(self.diccionario_completo)} registros en '{nombre_archivo}'")
        except Exception as e:
            print(f"Error al guardar: {e}")

if __name__ == "__main__":
    try:
        procesador = Extraer_scjn() 
        procesador.iterar_paginas()
        procesador.guardar_resultados()
        
        print("Creando Excel...", flush=True)
        df = pd.DataFrame.from_dict(procesador.diccionario_completo, orient='index')
        ruta_guardado = r'C:\Users\DELL\Downloads\proyectos\Beto_Legal_Mexico\data\sin limpiar\scjn\scjn_api.xlsx'
        df.to_excel(ruta_guardado, index=False)
        print("¡Archivo Excel guardado exitosamente!")
        
    except Exception as e:
        print("Excepción en __main__:", e, flush=True)
        traceback.print_exc()
    finally:
        time.sleep(2)