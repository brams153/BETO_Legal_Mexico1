---
title: "Arquitectura y Flujo de Datos"
description: "Diseño del Lakehouse, Feature Engineering y MLOps."
date: 2026-05-24
weight: 30
---

# Arquitectura del Sistema

BETO Legal México implementa una arquitectura **Medallion (Lakehouse)** integrada con un stack completo de MLOps para la puesta en producción.

## 1. Data Pipeline (Ingesta a Gold)

La ingesta se compone de extractores automatizados que recolectan resoluciones de la SCJN y documentos de repositorios universitarios, volcándolos inicialmente en bruto.

```mermaid
graph TD
    subgraph Fuentes
        SCJN[API SCJN]
        PDFs[Archivos PDF Locales]
        Diccionarios[Biblio Jurídica UNAM]
    end
    subgraph Modulo Ingesta
        Scrapers[Módulo de Scrapers]
    end
    subgraph Lakehouse
        Bronze[(Capa Bronze)]
        Silver[(Capa Silver)]
        Gold[(Capa Gold)]
    end

    SCJN --> Scrapers
    PDFs --> Scrapers
    Diccionarios --> Scrapers

    Scrapers --> Bronze
    Bronze -->|OCR & Limpieza| Silver
    Silver -->|Tokenización & Features| Gold
```

## 2. Feature Engineering

En la capa Silver, se aplican transformaciones clave antes de la etapa de modelado. Esto incluye la fragmentación contextual de largos textos legales (Chunking) y la inyección de aumentación de datos (Augmentation).

```mermaid
graph LR
    S[(Capa Silver)] --> C[Transforms: Chunking]
    C --> T[Transforms: Tokenization]
    T --> N[NER Features]
    T --> CL[Classification Features]
    T --> R[Retrieval Features]
```

## 3. Serving y MLOps

La orquestación general está administrada por **Airflow**. En tiempo de ejecución, una API RESTful (**FastAPI**) provee inferencia síncrona, apoyada por una cola de tareas (**Celery workers**) para procesamiento asíncrono o inferencia en batch, mientras métricas críticas fluyen hacia **Prometheus** y **Grafana**.
