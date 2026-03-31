---
title: "Configuración"
description: "Explicación de archivos de metadata, dependencias y rutas."
date: 2026-05-24
weight: 60
---

# Archivos de Configuración del Proyecto

BETO Legal México centraliza sus rutas y dependencias para garantizar consistencia estructural sin *hardcoding*.

## 1. Metadatos y Dependencias (`pyproject.toml`)

A diferencia de sistemas antiguos basados puramente en `setup.py`, el proyecto utiliza el estándar PEP 518/621.

**Qué hace y cómo funciona:**
- Declara `setuptools` como backend de construcción.
- Fija las dependencias nucleares con versiones hardcodeadas para garantizar determinismo en despliegues a Kubernetes / Docker (ej. `beautifulsoup4==4.14.3`, `pandas==3.0.3`, `pytesseract==0.3.13`).
- Habilita el paquete en modo instalable bajo el esquema de módulo global `Beto`.

*Fragmento Relevante (`pyproject.toml`):*
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "Beto"
version = "0.1.0"
dependencies = [
    "beautifulsoup4==4.14.3",
    "pandas==3.0.3",
    # ... dependencias core
]
```

## 2. Gestor Dinámico de Rutas (`src/Beto/utils/config.py`)

**Qué hace y cómo funciona:**
Al invocar módulos desde carpetas anidadas diferentes, los caminos relativos (ej. `../../data`) fallan sistemáticamente en Python. Este script provee constantes universales inmutables derivadas en tiempo de ejecución.

- Implementa `get_project_root()`, una iteración inteligente utilizando la clase nativa `Path` (`pathlib`) que asciende en el árbol de directorios hasta encontrar el archivo ancla `pyproject.toml`.
- Exporta objetos `Path` estandarizados (`PROJECT_ROOT`, `BETO_ROOT`, `BRONZE_DIR`, `SILVER_DIR`, `GOLD_DIR`), los cuales pueden ser concatenados de forma segura mediante el operador `/`.
