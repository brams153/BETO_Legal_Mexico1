---
title: "Guía de Instalación"
description: "Configuración del entorno de desarrollo local y dependencias del sistema."
date: 2026-05-24
weight: 20
---

# Configuración del Entorno

Este módulo detalla los pasos para desplegar el entorno de desarrollo y ejecución de los pipelines de ingesta e inferencia.

## Requisitos del Sistema (Linux)

Para la configuración del entorno en tu sistema local (ideal para una gestión orientada a terminal en entornos como Lubuntu con i3wm), necesitas instalar las herramientas base para la extracción de texto a partir de archivos PDF y soporte de reconocimiento óptico (OCR).

Desde tu emulador de terminal (ej. Alacritty), ejecuta el siguiente comando:

```bash
# Actualizar paquetería e instalar dependencias del sistema
sudo apt update
sudo apt install -y tesseract-ocr tesseract-ocr-spa poppler-utils python3.10-venv

```

* **`tesseract-ocr-spa`**: Paquete de idioma español, vital para procesar la terminología de los dictámenes jurídicos.
* **`poppler-utils`**: Proporciona herramientas subyacentes requeridas por la librería `pdf2image` para rasterizar los PDFs.

## Configuración del Entorno Virtual de Python

El ecosistema maneja dependencias complejas de Machine Learning y Scrapeo. Puedes preparar el entorno utilizando el gestor tradicional `pip` o el gestor de alta velocidad `uv` (recomendado para optimizar tiempos de compilación y resolución de candados).

### Opción A: Utilizando UV (Estrategia Rápida)

Si dispones de `uv` instalado en tu sistema, aprovecha el archivo `uv.lock` para garantizar un entorno determinista idéntico al de producción:

```bash
# Sincronizar el entorno virtual instantáneamente
uv sync

```

### Opción B: Utilizando el flujo tradicional de Pip

```bash
# Clonar y preparar el entorno virtual
mkdir -p ~/proyectos/beto_legal_mexico && cd ~/proyectos/beto_legal_mexico
python3 -m venv .venv
source .venv/bin/activate

# Instalar el paquete en modo editable junto con sus dependencias base
pip install -e .

```

## Inicialización de Estructuras Locales

El sistema asume la existencia de la estructura base del Lakehouse. Asegúrate de generar los directorios de almacenamiento en la raíz de tu proyecto:

```bash
mkdir -p data/{bronze,silver,gold}

```
