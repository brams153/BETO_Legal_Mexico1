---
title: "Referencia de la API (Módulos)"
description: "Documentación técnica detallada de clases y scripts core."
date: 2026-05-24
weight: 40
---

# Referencia de Módulos Principales

Esta sección detalla la lógica interna de los módulos de ingesta y procesamiento, abstrayendo cómo interactúan las capas lógicas representadas en el código fuente.

## 1. Scraper de Diccionarios Jurídicos
**Archivo fuente:** `src/Beto/pipeline/01_ingestion/scrapers/diccionarios/scrapper_diccionario_juridico.py`

### Explicación Lógica
La clase `UNAMVacuum` gestiona la descarga paralela y segura de tomos desde servidores académicos. Dado que algunos servidores carecen de certificados estrictos o presentan bloqueos anti-bot, la clase configura una `requests.Session` predefinida con un *User-Agent* moderno e inhabilita las advertencias SSL mediante `urllib3.disable_warnings`.

- **`find_pdfs_in_page(url)`:** Parsea el DOM mediante `BeautifulSoup` para extraer toda etiqueta `<a>` que contenga un enlace a un PDF. Reconstruye las rutas relativas inyectando el host absoluto `https://biblio.juridicas.unam.mx/bjv/`. Se emplea un objeto de tipo `set()` para desduplicar rutas.
- **`download_file(url, folder, prefix, index)`:** Soporta un mecanismo de streaming (`iter_content`) con chunks de `8192 bytes` para evitar colapsar la memoria del servidor al descargar documentos masivos. Emplea nativamente `pathlib.Path` para una creación segura y cross-platform de las rutas de guardado.

## 2. Scraper del Repositorio SCJN
**Archivo fuente:** `src/Beto/pipeline/01_ingestion/scrapers/repositorio_scjn/scrapper_scjn.py`

### Explicación Lógica
La clase `Extraer_scjn` está diseñada para comunicarse con la API de "Engroses" del Bicentenario de la SCJN. No procesa DOM, sino que ataca endpoints REST con paginación paramétrica.

- **`request_api_ids()`:** Hace peticiones GET al endpoint de metadatos `.../api/v1/engroses/ids` pasando argumentos de límite (`offset`, `limit`, `page`). Construye un diccionario `id: url` en memoria.
- **`obtener_urls_docx()`:** Realiza un cruce de datos iterando sobre las URLs de los IDs recolectados. Ejecuta el filtro dinámico para quedarse únicamente con los atributos `urlInternet` y `expediente`.
- **Generación de Salida:** Por cada batch, el resultado final no sobreescribe un único formato, sino que se serializa tanto en `datos_limpios.json` (para interoperabilidad en Python) como en un dataframe indexado en `scjn_api.xlsx` usando `pandas`, para futuras inspecciones de los engroses.

## 3. Extracción OCR Asíncrona
**Archivo fuente:** `src/Beto/pipeline/pipelines/ocr_extraction.py`

### Explicación Lógica
Este módulo asume el esfuerzo de cálculo pesado del proyecto: trasladar los PDFs escaneados de la capa Bronze a la capa Silver (texto enriquecido y analizable).

- **Uso de multiprocesamiento:** Evita el GIL de Python y bloqueos I/O orquestando un pool con `concurrent.futures.ProcessPoolExecutor`. La constante `MAX_WORKERS` modula la intensidad sobre la CPU.
- **`procesar_un_pdf()`:** A través de `pdf2image.convert_for_path`, desglosa el PDF en imágenes JPG a 200 DPI. Acto seguido, inyecta la bandera `--psm 3` (Page Segmentation Mode: fully automatic page segmentation) sobre `pytesseract` utilizando `lang="spa"` para capturar con precisión la ortografía jurídica mexicana.
