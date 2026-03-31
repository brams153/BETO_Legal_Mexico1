---
title: "Ejemplos de Uso"
description: "Cómo ejecutar el código base y scripts en terminal."
date: 2026-05-24
weight: 50
---

# Guía Práctica de Ejecución

## 1. Ejecutar el Scraper del Repositorio SCJN

Para probar la ingesta inicial desde la terminal y construir los registros desde la API de la SCJN:

```bash
# Ejecución interactiva desde el directorio raíz del proyecto
python src/Beto/pipeline/01_ingestion/scrapers/repositorio_scjn/scrapper_scjn.py
```

**Respuesta del CLI esperada:**
```text
Iniciando extracción masiva en: /.../data/bronze/scjn
IDs obtenidos: 1000
Página 1 terminada. Total: 1000
JSON guardado en: /.../data/bronze/scjn/datos_limpios.json
Excel guardado en: /.../data/bronze/scjn/scjn_api.xlsx
```

## 2. Ejecutar el Pipeline OCR (Bronze -> Silver)

Una vez poblada la carpeta `data/bronze/diccionarios` con los documentos de la UNAM, corre el pipeline de OCR:

```bash
python src/Beto/pipeline/pipelines/ocr_extraction.py
```

**Comportamiento:**
El script localizará automáticamente la ruta raíz (retrocediendo iterativamente usando la función de configuración interna `get_project_root()`). Desplegará la carga de trabajo en múltiples workers según `MAX_WORKERS` y creará el archivo unificado `diccionario_completo.txt` en la capa Silver.

> **Advertencia de hardware:** Si el sistema o ventana X11 presenta saturación de recursos por procesos Tesseract huérfanos, ajusta a `MAX_WORKERS = 1` o `2` en el script antes de lanzar jobs superiores a los 3 GB de PDFs.
