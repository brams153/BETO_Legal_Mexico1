from PIL import Image
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
import requests
from bs4 import BeautifulSoup
import os
import time
import urllib3
import pymupdf
#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#referenciar tesseract si no lo reconoce
folder_str=r'C:\Users\DELL\Downloads\proyectos\Beto_Legal_Mexico\data\scripts procesamiento'
folder=Path(folder_str)
carpeta_salida=r'C:\Users\DELL\Downloads\proyectos\Beto_Legal_Mexico\data\scripts procesamiento'


lista_rutas_pdf=[item for item in folder.iterdir() if item.is_file()]

lista_nombres_pdf = os.listdir(folder)

def obtener_dic_nombre_ruta(ruta_pdf):
    """Retorna un diccionario con el sistema;
        diccionario={nombre_archivo:ruta}"""
    dic_nombre_ruta={}
    for ruta in lista_rutas_pdf:
        ruta_obj=Path(ruta)
        ruta_str=str(ruta)
        ruta_str=str(ruta_str).replace("WindowsPath", "")
        nombre_archivo=ruta_obj.name
        if nombre_archivo in lista_nombres_pdf:
            dic_nombre_ruta[nombre_archivo]=ruta_str
    #print(dic_nombre_ruta)
    return dic_nombre_ruta
dic_nombre_ruta=obtener_dic_nombre_ruta(folder)
def ocr_columnar_pdf(image):
    """
    Función específica para PDFs de doble columna (UNAM/BJV)
    """
    # --psm 1: Segmentación automática de página (CRUCIAL para columnas)
    # -l spa: Español
    custom_config = r'--oem 3 --psm 1 -l spa'

    data = pytesseract.image_to_string(image, config=custom_config)
    return data

def convertir_paginas_a_txt(lista_nombre_archivos, ruta_input, ruta_output):
    ruta_input = Path(ruta_input)#convierte el string de la ruta a una ruta real
    ruta_output = Path(ruta_output)#lo mismo aca
    ruta_output.mkdir(parents=True, exist_ok=True)#comprueba la existencia de las carpetas madre y si no los crea

    contenido_total = [] #lista vacía para almacenar el texto 

    for nombre_archivo in lista_nombre_archivos:
        #recorre el nombre de archivo en la lista con nombres de los archivos
        path_completo_pdf = ruta_input / nombre_archivo #divide ruta entrada entre nombre para encontar la ruta del pdf
        
        print(f"📄 Procesando: {nombre_archivo}...")
        
        try:
            # 1. Convertir PDF a imágenes
            # Si falla, añade: poppler_path=POPPLER_PATH
            paginas = convert_from_path(path_completo_pdf, dpi=300)
            
            contenido_libro = []
            
            for j, pagina in enumerate(paginas):
                print(f" OCR pág {j+1}...", end="\r")
                texto = pytesseract.image_to_string(pagina, lang='spa', config='--psm 1')
                contenido_libro.append(texto)
            
            # Acumular el contenido de este PDF al total
            contenido_total.extend(contenido_libro)
            
            # Código comentado para generar archivos separados (descomentar si se quiere uno por PDF)
            # nombre_txt = path_completo_pdf.stem + ".txt"
            # with open(ruta_output / nombre_txt, "w", encoding="utf-8") as f:
            #     f.write("\n\n--- NUEVA PÁGINA ---\n\n".join(contenido_libro))
            
            print(f"\n✅ Procesado: {nombre_archivo}")

        except Exception as e:
            print(f"\n❌ Error en {nombre_archivo}: {e}")
    
    # Escribir todo el contenido acumulado en un solo archivo
    nombre_salida = "diccionario_completo.txt"
    with open(ruta_output / nombre_salida, "w", encoding="utf-8") as f_salida:
        f_salida.write("\n\n".join(contenido_total))
    
    print(f"\n✅ Archivo completo generado: {nombre_salida}")
    
ocr=convertir_paginas_a_txt(lista_nombres_pdf,folder,carpeta_salida)