import os
import sys
import pytesseract
from pathlib import Path
from pdf2image import convert_for_path

from concurrent.futures import ProcessPoolExecutor, as_completed

pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"
MAX_WORKERS = 1


def get_project_root():
    """
    Busca la raíz subiendo desde 'scripts_procesamiento' hasta la carpeta madre.
    """
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if (parent / "silver").exists() and (parent / "bronze").exists():
            return parent
    return current_path.parent.parent  # Fallback: subir dos niveles


PROJECT_ROOT = get_project_root()

INPUT_FOLDER = PROJECT_ROOT / "bronze" / "diccionarios"

OUTPUT_FOLDER = PROJECT_ROOT / "silver" / "diccionarios"


def procesar_un_pdf(nombre_archivo, ruta_input):
    path_completo_pdf = ruta_input / nombre_archivo
    texto_acumulado = []

    try:
        paginas = convert_for_path(
            path_completo_pdf, dpi=200, fmt="jpeg", poppler_path="/usr/bin"
        )
        total_pags = len(paginas)

        for i, pagina in enumerate(paginas, 1):
            print(f"📄 [{nombre_archivo}] -> OCR pág {i}/{total_pags}")
            texto = pytesseract.image_to_string(pagina, lang="spa", config="--psm 3")
            texto_acumulado.append(texto)

        print(f"✅ FINALIZADO: {nombre_archivo}")
        return texto_acumulado  # Devolvemos lista para manejar mejor el orden

    except Exception as e:
        print(f"❌ Error procesando {nombre_archivo}: {e}")
        return None


def ejecutar_paralelo():
    # Crear carpeta de salida si no existe
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    if not INPUT_FOLDER.exists():
        print(f"❌ Error: La carpeta de entrada {INPUT_FOLDER} no existe.")
        return

    # Obtener lista de PDFs
    lista_pdfs = [f for f in INPUT_FOLDER.glob("*.pdf")]

    if not lista_pdfs:
        print(f"⚠️ No se encontraron PDFs en {INPUT_FOLDER}")
        return

    print(f"🚀 Iniciando OCR paralelo (8 procesos)")
    print(f"📂 Origen: {INPUT_FOLDER}")
    print(f"📂 Destino: {OUTPUT_FOLDER}")
    print(f"📄 Archivos: {len(lista_pdfs)}")
    print("-" * 50)

    resultados_dict = {}

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Lanzamos procesos
        futuros = {
            executor.submit(procesar_un_pdf, f.name, INPUT_FOLDER): f.name
            for f in lista_pdfs
        }

        for futuro in as_completed(futuros):
            nombre = futuros[futuro]
            res = futuro.result()
            if res:
                resultados_dict[nombre] = res

    # Consolidar y guardar
    if resultados_dict:
        archivo_salida = OUTPUT_FOLDER / "diccionario_completo.txt"

        # Ordenamos alfabéticamente por nombre de archivo original
        archivos_ordenados = sorted(resultados_dict.keys())

        try:
            with open(archivo_salida, "w", encoding="utf-8") as f:
                for nombre in archivos_ordenados:
                    f.write(f"\n\n{'=' * 30}\n ARCHIVO: {nombre}\n{'=' * 30}\n\n")
                    f.write("\n\n".join(resultados_dict[nombre]))

            print("-" * 50)
            print(f"🎉 TODO LISTO. Archivo creado en: {archivo_salida}")
        except IOError as e:
            print(f"❌ Error al escribir el archivo final: {e}")
    else:
        print("\n⚠️ No se generó contenido.")


if __name__ == "__main__":
    ejecutar_paralelo()
