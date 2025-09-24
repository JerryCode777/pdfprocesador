#!/usr/bin/env python3
"""
Generador Principal de Preguntas - Procesa todos los archivos de contenido
"""

import sys
import os
import time
from datetime import datetime
sys.path.append('scripts')

from question_generator import QuestionGenerator

def print_header():
    print("❓ GENERADOR DE PREGUNTAS EDUCATIVAS")
    print("Genera 15 preguntas por tema basadas en contenido extraído")
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

    # Check if content directory exists
    content_dir = "output/content"
    if not os.path.exists(content_dir):
        print(f"❌ ERROR: No existe el directorio {content_dir}")
        print("Primero debes ejecutar extract_content.py para generar el contenido")
        return

    try:
        # Initialize question generator
        print("🔧 Inicializando generador de preguntas...")
        generator = QuestionGenerator()

        # Create output directory
        output_dir = "output/questions"
        os.makedirs(output_dir, exist_ok=True)

        # Process all content files
        generator.process_all_content_files(content_dir, output_dir)

        # Final summary
        total_time = time.time() - start_time

        print("\n" + "🎉" * 50)
        print("🎉 ¡GENERACIÓN DE PREGUNTAS COMPLETADA!")
        print("🎉" * 50)

        print(f"\n📊 RESUMEN:")
        print(f"  ⏱️ Tiempo total: {total_time/60:.1f} minutos")

        # Count generated files
        if os.path.exists(output_dir):
            from pathlib import Path
            total_question_files = 0
            subject_dirs = [d for d in Path(output_dir).iterdir() if d.is_dir()]

            print(f"\n📁 ESTRUCTURA GENERADA:")
            for subject_dir in subject_dirs:
                question_files = list(subject_dir.glob("tema_*.json"))
                total_question_files += len(question_files)
                print(f"  📚 {subject_dir.name}/")
                print(f"      📄 {len(question_files)} archivos de temas")

            print(f"\n📊 TOTALES:")
            print(f"  📚 Materias procesadas: {len(subject_dirs)}")
            print(f"  📄 Total archivos de preguntas: {total_question_files}")

        print(f"\n🎯 CARACTERÍSTICAS:")
        print(f"  📋 15 preguntas por tema")
        print(f"  🎚️ 3 niveles de dificultad (1, 2, 3)")
        print(f"  📝 5 opciones por pregunta (A, B, C, D, E)")
        print(f"  🆔 IDs temporales únicos por pregunta")
        print(f"  📖 Explicaciones detalladas")

        print(f"\n📁 UBICACIÓN: {output_dir}/")
        print(f"🚀 ¡LISTO PARA USAR EN TU APLICACIÓN FLUTTER!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()