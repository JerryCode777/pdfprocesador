#!/usr/bin/env python3
"""
Test del extractor con archivo grande (Biología)
"""

import sys
import os
sys.path.append('scripts')

from batch_content_extractor import BatchContentExtractor, ProgressTracker
from pathlib import Path

def main():
    print("🧪 PROBANDO EXTRACTOR CON ARCHIVO GRANDE")
    print("=" * 50)

    # Find Biology PDF or largest file
    pdf_files = list(Path("bancos").glob("*BIOLOGIA*.pdf"))

    if not pdf_files:
        print("📄 No se encontró Biología, buscando archivo más grande...")
        all_pdfs = list(Path("bancos").glob("*.pdf"))
        if not all_pdfs:
            print("❌ No hay archivos PDF")
            return
        all_pdfs.sort(key=lambda x: x.stat().st_size, reverse=True)
        test_file = all_pdfs[0]
    else:
        test_file = pdf_files[0]

    print(f"📄 Probando con: {test_file.name}")
    file_size_mb = test_file.stat().st_size / (1024 * 1024)
    print(f"📏 Tamaño: {file_size_mb:.1f} MB")

    # Get page count
    import fitz
    doc = fitz.open(str(test_file))
    total_pages = len(doc)
    doc.close()
    print(f"📄 Total páginas: {total_pages}")
    print(f"📦 Se dividirá en {(total_pages + 99) // 100} lotes de 100 páginas")

    # Create output directory
    os.makedirs("output/content", exist_ok=True)

    try:
        extractor = BatchContentExtractor(batch_size=100)
        progress = ProgressTracker(1)

        print(f"\n🚀 Iniciando procesamiento...")
        output_file = extractor.process_single_pdf_in_batches(str(test_file), "output/content", progress)

        print(f"\n✅ Test exitoso! Generado: {output_file}")

        # Show results
        import json
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"\n📊 RESULTADOS:")
        print(f"  • Materia: {data.get('metadata', {}).get('subject', 'N/A')}")
        print(f"  • Total páginas: {data.get('metadata', {}).get('total_pages', 'N/A')}")
        print(f"  • Lotes procesados: {data.get('metadata', {}).get('batches_processed', 'N/A')}")
        print(f"  • Páginas con contenido: {data.get('content_summary', {}).get('pages_with_content', 'N/A')}")
        print(f"  • Temas encontrados: {len(data.get('topics', []))}")

        print(f"\n🎉 ¡PROCESAMIENTO EXITOSO!")

    except Exception as e:
        print(f"❌ Test fallido: {e}")

if __name__ == "__main__":
    main()