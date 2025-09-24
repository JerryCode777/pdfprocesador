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

### Probar con un archivo:
```bash
source pdf_processor_env/bin/activate
python3 test_content.py
```

### Procesar todos los PDFs:
```bash
source pdf_processor_env/bin/activate
python3 extract_content.py
```

## 📁 Archivos del proyecto

- `extract_content.py` - Procesar todos los PDFs
- `test_content.py` - Probar con un archivo grande
- `scripts/batch_content_extractor.py` - Módulo extractor
- `.env` - Configuración de API key
- `pdf_processor_env/` - Entorno virtual

## 📊 Salida

Los archivos JSON se guardan en `output/content/` con esta estructura:

```json
{
  "metadata": {
    "subject": "BIOLOGIA",
    "total_pages": 373,
    "processing_method": "gemini-2.5-pro-content-only"
  },
  "topics": ["Biología", "Genética", "Ecología"],
  "pages": [
    {
      "page_number": 1,
      "content": "Contenido educativo limpio...",
      "topics": ["Biología"],
      "has_content": true
    }
  ],
  "content_summary": {
    "pages_with_content": 350,
    "content_type": "educational_theory_only"
  }
}
```

## ⚙️ Configuración

1. API key de Gemini configurada en `.env`
2. Entorno virtual con dependencias instaladas
3. PDFs en directorio `bancos/`