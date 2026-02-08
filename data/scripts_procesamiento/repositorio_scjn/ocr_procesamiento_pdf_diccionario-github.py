from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
import os
import sys


def get_project_root():
    """
    Busca la raíz del proyecto subiendo directorios desde la ubicación
    de este script hasta encontrar la carpeta 'data' o '.github'.
    """
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if (parent / 'data').exists() or (parent / '.github').exists():
            return parent
    return current_path.parent  # Fallback: directorio actual

# Definimos la Raíz del Proyecto
PROJECT_ROOT = get_project_root()

# Definimos las rutas relativas basadas en la raíz
# Según tu árbol: root -> data -> scripts procesamiento
DATA_DIR = PROJECT_ROOT / "data" / "sin limpiar" / "diccionarios"
INPUT_FOLDER = DATA_DIR 
OUTPUT_FOLDER = DATA_DIR # O si prefieres: PROJECT_ROOT / "data" / "processed"

print(f"📂 Raíz del proyecto detectada: {PROJECT_ROOT}")
print(f"📂 Carpeta de entrada: {INPUT_FOLDER}")

# Configuración de binarios (Tesseract / Poppler)
# Intenta leer de variables de entorno (útil para Docker), si no, usa defaults
TESSERACT_CMD = os.getenv('TESSERACT_CMD', None) 
POPPLER_PATH = os.getenv('POPPLER_PATH', None) # Útil si en Windows poppler no está en PATH

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
# Si estás en Windows local y no usas variables de entorno, descomenta:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ==========================================
# 2. LÓGICA DEL SCRIPT
# ==========================================

# Usamos pathlib para listar archivos (más robusto que os.listdir)
# Filtramos solo archivos para evitar errores con carpetas
lista_rutas_pdf = [item for item in INPUT_FOLDER.iterdir() if item.is_file() and item.suffix.lower() == '.pdf']
lista_nombres_pdf = [item.name for item in lista_rutas_pdf]

def obtener_dic_nombre_ruta(lista_rutas):
    """
    Retorna un diccionario {nombre_archivo: ruta_absoluta_string}
    """
    dic_nombre_ruta = {}
    for ruta_obj in lista_rutas:
        # Pathlib maneja automáticamente los separadores (\ para Win, / para Linux)
        nombre_archivo = ruta_obj.name
        dic_nombre_ruta[nombre_archivo] = str(ruta_obj.resolve())
    
    return dic_nombre_ruta

def ocr_columnar_pdf(image):
    """
    Función específica para PDFs de doble columna (UNAM/BJV)
    """
    # --psm 1: Segmentación automática de página (CRUCIAL para columnas)
    custom_config = r'--oem 3 --psm 1 -l spa'
    data = pytesseract.image_to_string(image, config=custom_config)
    return data

def convertir_paginas_a_txt(lista_nombre_archivos, ruta_input, ruta_output):
    # Aseguramos que sean objetos Path
    ruta_input = Path(ruta_input)
    ruta_output = Path(ruta_output)
    
    # Crea la carpeta de salida si no existe (parents=True crea subcarpetas si faltan)
    ruta_output.mkdir(parents=True, exist_ok=True)

    contenido_total = [] 

    if not lista_nombre_archivos:
        print("⚠️ No se encontraron archivos PDF en la carpeta especificada.")
        return

    for nombre_archivo in lista_nombre_archivos:
        path_completo_pdf = ruta_input / nombre_archivo
        
        print(f"📄 Procesando: {nombre_archivo}...")
        
        try:
            # 1. Convertir PDF a imágenes
            # En Docker/Linux, poppler suele estar en el PATH por defecto.
            # En Windows, si falla, agrega el argumento: poppler_path=POPPLER_PATH
            paginas = convert_from_path(path_completo_pdf, dpi=300, poppler_path=POPPLER_PATH)
            
            contenido_libro = []
            
            for j, pagina in enumerate(paginas):
                print(f"   OCR pág {j+1}/{len(paginas)}...", end="\r")
                texto = pytesseract.image_to_string(pagina, lang='spa', config='--psm 1')
                contenido_libro.append(texto)
            
            contenido_total.extend(contenido_libro)
            print(f"\n✅ Procesado: {nombre_archivo}")

        except Exception as e:
            print(f"\n❌ Error en {nombre_archivo}: {e}")
    
    # Escribir todo el contenido acumulado
    nombre_salida = "diccionario_completo.txt"
    archivo_final = ruta_output / nombre_salida
    
    with open(archivo_final, "w", encoding="utf-8") as f_salida:
        f_salida.write("\n\n".join(contenido_total))
    
    print(f"\n✅ Archivo completo generado en: {archivo_final}")

# ==========================================
# 3. EJECUCIÓN
# ==========================================

if __name__ == "__main__":
    # Generamos el diccionario (aunque tu función original no lo usaba para el OCR, lo mantengo)
    dic_rutas = obtener_dic_nombre_ruta(lista_rutas_pdf)
    
    # Ejecutamos el proceso principal
    convertir_paginas_a_txt(lista_nombres_pdf, INPUT_FOLDER, OUTPUT_FOLDER)