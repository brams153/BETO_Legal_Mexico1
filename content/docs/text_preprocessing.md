---
title: "Preprocesamiento y Normalización"
description: "Reglas de limpieza para el tratamiento de artefactos OCR y texto legal."
date: 2026-05-24
weight: 35
---

# Normalización de Texto Legal (Silver a Gold)

La extracción de texto mediante Tesseract genera cadenas con ruido tipográfico debido a la estructura física de los libros analizados (columnas, notas al pie, encabezados y folios). Este módulo documenta las heurísticas aplicadas en el pipeline para limpiar el archivo `diccionario_completo.txt`.

## 1. Desafíos Detectados en el Corpus OCR

Los documentos de la Biblioteca Jurídica Virtual de la UNAM presentan patrones de ruido que rompen la continuidad sintáctica requerida por las arquitecturas basadas en Transformers:

1. **Silabeo por Salto de Línea:** División incorrecta de tokens debido al formato a dos columnas (ej. `fami- liar`, `reem- bol- so`).
2. **Inyección de Metadatos de Repositorio:** Cadenas idénticas añadidas en cada página (ej. `DR © 1982. Universidad Nacional Autónoma de México - Instituto de Investigaciones Jurídicas`).
3. **Enlaces e Indicadores de Páginas:** URLs institucionales fijas que sesgan las distribuciones de embeddings de palabras (ej. `https://biblio.juridicas.unam.mx/bjv` o `Libro completo en: ...`).

## 2. Pipeline de Limpieza Algorítmica

Para mitigar estos problemas, el pipeline implementa un procesador basado en expresiones regulares (`re`) y segmentadores contextuales antes de almacenar las secuencias en la capa Gold.

### Matriz de Transformaciones Técnicas

| Tipo de Artefacto | Expresión Regular / Método | Acción Correctiva |
| :--- | :--- | :--- |
| Guiones de fragmentación | `r'(\\w+)-\\s*\\n\\s*(\\w+)'` | Une las sílabas eliminando el guion y el salto de línea para restaurar el token original (ej. `famili- ar` → `familiar`). |
| Encabezados de repositorio | `r'(?i)Esta obra forma parte del acervo.*'` | Remueve bloques de texto estáticos pertenecientes al metadato del PDF de la UNAM. |
| Números de página aislados | `r'^\\s*\\d+\\s*$'` | Identifica líneas que contienen únicamente folios numéricos para evitar que rompan el contexto conceptual entre párrafos continuos. |
| Normalización de espacios | `r'\\s+'` → `' '` | Colapsa múltiples saltos de línea y tabuladores en espacios simples para un flujo lineal uniforme de tokens. |

## 3. Preparación de Secuencias para BETO (Gold)

Una vez que el texto carece de ruido estructural, se ejecutan las últimas tareas de Feature Engineering descritas en la arquitectura:

- **Remoción Selectiva de Stopwords:** Preservación estricta de preposiciones que configuran fórmulas legales (ej. "ab intestato", "de jure", "de facto") para evitar la pérdida de sentido jurídico.
- **Mapeo de Entidades (NER):** Extracción e indexación automática de referencias a normatividades mexicanas (ej. `LFT`, `CC`, `DO`, `SHCP`, `SCJN`) y citas a leyes federales históricas presentes en los textos normalizados.
