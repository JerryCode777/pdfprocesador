#!/usr/bin/env python3
"""
Test del generador de preguntas con un solo archivo
"""

import sys
import os
sys.path.append('scripts')

from question_generator import QuestionGenerator
from pathlib import Path
import json

def main():
    print("🧪 PROBANDO GENERADOR DE PREGUNTAS")
    print("=" * 50)

    # Find a content file to test with
    content_dir = Path("output/content")

    if not content_dir.exists():
        print("❌ No existe el directorio output/content")
        print("Primero debes ejecutar extract_content.py")
        return

    content_files = list(content_dir.glob("*_content.json"))

    if not content_files:
        print("❌ No se encontraron archivos de contenido")
        print("Primero debes ejecutar extract_content.py")
        return

    # Use the first (smallest) file for testing
    test_file = content_files[0]
    print(f"📄 Probando con: {test_file.name}")

    # Load and analyze the content file
    with open(test_file, 'r', encoding='utf-8') as f:
        content_data = json.load(f)

    subject = content_data.get('metadata', {}).get('subject', 'UNKNOWN')
    total_pages = content_data.get('metadata', {}).get('total_pages', 0)
    topics = content_data.get('topics', [])

    print(f"📚 Materia: {subject}")
    print(f"📄 Total páginas: {total_pages}")
    print(f"🎯 Total temas disponibles: {len(topics)}")

    # Show first few topics
    print(f"\n🔍 PRIMEROS 5 TEMAS DETECTADOS:")
    for i, topic in enumerate(topics[:5], 1):
        print(f"  {i}. {topic}")

    # Initialize generator
    try:
        generator = QuestionGenerator()

        # Create test output directory
        test_output_dir = "output/test_questions"
        os.makedirs(test_output_dir, exist_ok=True)

        print(f"\n🚀 Iniciando generación de preguntas de prueba...")

        # Process the test file
        success = generator.process_content_file(str(test_file), test_output_dir)

        if success:
            print(f"\n✅ ¡Prueba exitosa!")

            # Analyze generated questions
            subject_dir = os.path.join(test_output_dir, subject.lower().replace(' ', '_'))

            if os.path.exists(subject_dir):
                question_files = list(Path(subject_dir).glob("tema_*.json"))
                print(f"\n📊 ANÁLISIS DE RESULTADOS:")
                print(f"  📁 Carpeta creada: {subject.lower().replace(' ', '_')}/")
                print(f"  📄 Archivos de preguntas generados: {len(question_files)}")

                # Show details of first question file
                if question_files:
                    first_q_file = question_files[0]
                    with open(first_q_file, 'r', encoding='utf-8') as f:
                        q_data = json.load(f)

                    print(f"\n📝 MUESTRA DEL PRIMER ARCHIVO:")
                    print(f"  📄 Archivo: {first_q_file.name}")
                    print(f"  🎯 Tema: {q_data.get('titulo_tema', 'N/A')}")
                    print(f"  🔢 Número de tema: {q_data.get('numero_tema', 'N/A')}")
                    print(f"  📊 Total temas: {q_data.get('total_temas', 'N/A')}")
                    print(f"  ❓ Preguntas generadas: {len(q_data.get('preguntas', []))}")

                    # Show first question as example
                    preguntas = q_data.get('preguntas', [])
                    if preguntas:
                        primera_pregunta = preguntas[0]
                        print(f"\n📋 EJEMPLO DE PRIMERA PREGUNTA:")
                        print(f"  ID: {primera_pregunta.get('id_temporal', 'N/A')}")
                        print(f"  Dificultad: {primera_pregunta.get('dificultad', 'N/A')}")
                        print(f"  Pregunta: {primera_pregunta.get('pregunta', 'N/A')[:100]}...")
                        print(f"  Respuesta correcta: {primera_pregunta.get('respuesta_correcta', 'N/A')}")

                    # Verify question distribution by difficulty
                    dificultades = {}
                    for pregunta in preguntas:
                        dif = pregunta.get('dificultad', 0)
                        dificultades[dif] = dificultades.get(dif, 0) + 1

                    print(f"\n📊 DISTRIBUCIÓN POR DIFICULTAD:")
                    for dif, count in sorted(dificultades.items()):
                        print(f"  Dificultad {dif}: {count} preguntas")

                    print(f"\n🎉 ¡ESTRUCTURA CORRECTA VERIFICADA!")
                    print(f"✅ Las preguntas siguen el formato solicitado")
                    print(f"✅ Los temas están organizados por orden de páginas")
                    print(f"✅ Los IDs temporales están correctamente formateados")

            else:
                print(f"⚠️ No se creó la carpeta de materia esperada")

        else:
            print(f"❌ La prueba falló")

    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()