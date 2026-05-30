---
title: "Esquema de Datos (Bronze)"
description: "Estructura de metadatos y esquemas JSON/Excel de la capa de ingesta."
date: 2026-05-24
weight: 45
---

# Referencia del Esquema de Datos (Capa Bronze)

Para asegurar la trazabilidad del pipeline de datos antes de las fases de limpieza profunda, los scrapers almacenan la información estructurada bajo contratos de datos específicos.

## 1. Mapeo de la API de Engroses de la SCJN

El archivo de salida intermedio generado por el scraper de la SCJN se localiza en `data/bronze/scjn/datos_limpios.json`. Este archivo mapea de forma unívoca el identificadores secuencial de la resolución con sus propiedades de localización remota e identificación interna de expediente.

### Estructura del JSON de Ingesta

Cada registro utiliza el ID único de la SCJN como clave principal (`string`) para agilizar las búsquedas en memoria indexada:

```json
{
    "ID_RESOLUCION": {
        "expediente": "NÚMERO_DE_EXPEDIENTE",
        "urlInternet": "URL_ABSOLUTA_AL_DOCX"
    }
}

```

### Diccionario de Campos

| Campo | Tipo | Capa | Descripción | Ejemplo |
| --- | --- | --- | --- | --- |
| `ID_RESOLUCION` | `String` (Index) | Bronze | Identificador numérico único asignado por la API de la SCJN. | `"230878"` |
| `expediente` | `String` | Bronze | Nomenclatura oficial del expediente jurídico en México. | `"5/2025-CA"` |
| `urlInternet` | `String` | Bronze | Dirección URL directa del servidor de la SCJN para la descarga del archivo binario (`.docx`). | `https://www2.scjn.gob.mx/.../2_344294_7087.docx` |

## 2. Archivos de Inspección Rápida (`.xlsx`)

De manera paralela al archivo JSON, el script `scrapper_scjn.py` persiste una réplica estructurada en un formato tabular compatible con `pandas` (`scjn_api.xlsx`). Este archivo actúa como puente de validación y control de auditoría externa para los analistas que requieran revisar el volumen total de engroses capturados por cada batch de ejecución de Airflow.
