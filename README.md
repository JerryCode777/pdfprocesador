# 📚 Extractor de Contenido Educativo

Sistema para extraer contenido educativo limpio de PDFs usando Gemini 2.5 Pro.

## 🎯 Qué hace

- Extrae **solo contenido educativo** de PDFs
- Organiza el contenido **página por página**
- Identifica **temas automáticamente**
- **NO incluye preguntas** ni ejercicios
- Procesa archivos grandes en **lotes de 100 páginas**
- Genera **JSON limpio** para usar en aplicaciones

## 🚀 Uso

### PASO 1: Extraer contenido de PDFs
```bash
source pdf_processor_env/bin/activate
python3 test_content.py        # Probar con un archivo
python3 extract_content.py     # Procesar todos los PDFs
```

### PASO 2: Generar preguntas por temas
```bash
source pdf_processor_env/bin/activate
python3 test_questions.py      # Probar generación de preguntas
python3 generate_questions.py  # Generar preguntas para todos
```

## 📁 Archivos del proyecto

### Extracción de contenido:
- `extract_content.py` - Procesar todos los PDFs
- `test_content.py` - Probar extracción con un archivo

### Generación de preguntas:
- `generate_questions.py` - Generar preguntas para todos los cursos
- `test_questions.py` - Probar generación con un archivo

### Módulos internos:
- `scripts/batch_content_extractor.py` - Extractor de contenido
- `scripts/question_generator.py` - Generador de preguntas
- `.env` - Configuración de API key
- `pdf_processor_env/` - Entorno virtual

## 📊 Salida

### Contenido extraído: `output/content/`
```json
{
  "metadata": {
    "subject": "BIOLOGIA",
    "total_pages": 373
  },
  "topics": ["Biología", "Genética", "Ecología"],
  "pages": [
    {
      "page_number": 1,
      "content": "Contenido educativo limpio...",
      "topics": ["Biología"]
    }
  ]
}
```

### Preguntas generadas: `output/questions/materia/`
```json
{
  "materia": "biologia",
  "numero_tema": 1,
  "total_temas": 25,
  "titulo_tema": "Introducción a la Biología",
  "preguntas": [
    {
      "id_temporal": "biologia_001_001",
      "pregunta": "¿Qué estudia la biología?",
      "dificultad": 1,
      "opciones": {
        "A": "Los seres vivos y sus procesos",
        "B": "Solo las plantas",
        "C": "Solo los animales",
        "D": "Los minerales",
        "E": "El clima"
      },
      "respuesta_correcta": "A",
      "explicacion": "La biología es la ciencia que estudia...",
      "imagen": null
    }
  ]
}
```

## ⚙️ Configuración

1. API key de Gemini configurada en `.env`
2. Entorno virtual con dependencias instaladas
3. PDFs en directorio `bancos/`