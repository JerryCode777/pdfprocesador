#!/usr/bin/env python3
"""
Extractor Principal - Procesa PDFs en lotes de 100 páginas
Script único y definitivo para extraer contenido educativo
"""

import sys
import os
import time
from datetime import datetime
sys.path.append('scripts')

from batch_content_extractor import BatchContentExtractor

def print_header():
    print("📚 EXTRACTOR DE CONTENIDO EDUCATIVO")
    print("Procesamiento por lotes - Seguro para archivos grandes")
    print("=" * 60)
    print(f"🕐 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

def main():
    start_time = time.time()
    print_header()

    # Check API key
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key or api_key == 'your_gemini_api_key_here':
        print("❌ ERROR: API key no configurado!")
        return

    try:
        # Initialize batch extractor
        print("🔧 Inicializando extractor por lotes...")
        extractor = BatchContentExtractor(batch_size=100)

        # Create output directory
        output_dir = "output/content"
        os.makedirs(output_dir, exist_ok=True)

        # Process all PDFs
        output_files = extractor.process_all_pdfs("bancos", output_dir)

        if not output_files:
            print("❌ No se procesaron archivos exitosamente!")
            return

        # Final summary
        total_time = time.time() - start_time

        print("\n" + "🎉" * 50)
        print("🎉 ¡EXTRACCIÓN COMPLETADA!")
        print("🎉" * 50)

        print(f"\n📊 RESUMEN:")
        print(f"  ⏱️ Tiempo total: {total_time/60:.1f} minutos")
        print(f"  📄 Archivos procesados: {len(output_files)}")

        print(f"\n📁 ARCHIVOS GENERADOS:")
        for file in output_files:
            filename = os.path.basename(file)
            print(f"  📄 {filename}")

        print(f"\n✅ LISTO PARA USAR EN TU APLICACIÓN FLUTTER!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()