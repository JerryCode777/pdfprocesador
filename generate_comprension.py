#!/usr/bin/env python3
"""
Generador de Preguntas de Comprensión Lectora
- Comprensión Lectora I: 1 texto + 2 preguntas
- Comprensión Lectora II: 1 texto + 3 preguntas
"""

import sys
import os
import time
from datetime import datetime
sys.path.append('scripts')

from comprension_generator import ComprensionGenerator

def print_header():
    print("📖 GENERADOR DE PREGUNTAS DE COMPRENSIÓN LECTORA")
    print("Genera textos con preguntas basadas en contenido de Razonamiento Verbal")
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

    # Check if content file exists
    content_file = "output/content/razonamiento_verbal_content.json"
    if not os.path.exists(content_file):
        print(f"❌ ERROR: No existe el archivo {content_file}")
        print("Primero debes ejecutar extract_content.py para generar el contenido")
        return

    try:
        # Initialize comprension generator
        print("🔧 Inicializando generador de comprensión lectora...")
        generator = ComprensionGenerator()

        # Create output directories
        output_dir_i = "output/questions/comprension_lectoraI"
        output_dir_ii = "output/questions/comprension_lectoraII"
        os.makedirs(output_dir_i, exist_ok=True)
        os.makedirs(output_dir_ii, exist_ok=True)

        print(f"\n📚 Procesando contenido de comprensión lectora...")
        print(f"📁 Salida Nivel I: {output_dir_i}")
        print(f"📁 Salida Nivel II: {output_dir_ii}")

        # Generate reading comprehension questions
        generator.generate_comprension_questions(
            content_file,
            output_dir_i,
            output_dir_ii
        )

        # Final summary
        total_time = time.time() - start_time

        print("\n" + "🎉" * 50)
        print("🎉 ¡GENERACIÓN DE COMPRENSIÓN LECTORA COMPLETADA!")
        print("🎉" * 50)

        print(f"\n📊 RESUMEN:")
        print(f"  ⏱️ Tiempo total: {total_time/60:.1f} minutos")

        # Count generated files
        from pathlib import Path
        files_i = list(Path(output_dir_i).glob("texto_*.json"))
        files_ii = list(Path(output_dir_ii).glob("texto_*.json"))

        print(f"\n📁 ESTRUCTURA GENERADA:")
        print(f"  📚 Comprensión Lectora I:")
        print(f"      📄 {len(files_i)} textos con 2 preguntas cada uno")
        print(f"  📚 Comprensión Lectora II:")
        print(f"      📄 {len(files_ii)} textos con 3 preguntas cada uno")

        print(f"\n🎯 CARACTERÍSTICAS:")
        print(f"  📖 Textos generados con IA de alta calidad")
        print(f"  📝 Nivel I: 2 preguntas por texto")
        print(f"  📝 Nivel II: 3 preguntas por texto")
        print(f"  🎚️ 3 niveles de dificultad (1, 2, 3)")
        print(f"  📝 5 opciones por pregunta (A, B, C, D, E)")
        print(f"  📖 Explicaciones detalladas")

        print(f"\n📁 UBICACIONES:")
        print(f"  {output_dir_i}/")
        print(f"  {output_dir_ii}/")
        print(f"🚀 ¡LISTO PARA USAR EN TU APLICACIÓN FLUTTER!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
