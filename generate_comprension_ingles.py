#!/usr/bin/env python3
"""
Generador de Comprensión Lectora en Inglés
- Textos en inglés nivel básico (A2-B1)
- Preguntas en español
- 1 texto + 2 preguntas
"""

import sys
import os
import time
from datetime import datetime
sys.path.append('scripts')

from comprension_ingles_generator import ComprensionInglesGenerator

def main():
    print("🌍 GENERADOR DE COMPRENSIÓN LECTORA EN INGLÉS")
    print("=" * 60)
    print(f"🕐 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Check API key
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key or api_key == 'your_gemini_api_key_here':
        print("❌ ERROR: API key no configurado!")
        return

    try:
        # Initialize generator
        print("🔧 Inicializando generador de comprensión en inglés...")
        generator = ComprensionInglesGenerator()

        # Create output directory
        output_dir = "output/questions/comprension_ingles"
        os.makedirs(output_dir, exist_ok=True)

        print(f"📁 Directorio de salida: {output_dir}")

        # Generate English comprehension questions
        generator.generate_comprension_ingles(
            output_dir,
            num_textos=20
        )

        print("\n" + "🎉" * 50)
        print("🎉 ¡GENERACIÓN COMPLETADA!")
        print("🎉" * 50)

        print(f"\n🎯 CARACTERÍSTICAS:")
        print(f"  📖 Textos en inglés nivel básico (A2-B1)")
        print(f"  ❓ Preguntas en inglés")
        print(f"  🅰️ Opciones en inglés")
        print(f"  💬 Explicaciones bilingües (Español + English)")
        print(f"  🔢 20 textos con 2 preguntas cada uno")
        print(f"  📊 Total: 40 preguntas")
        print(f"  🎚️ Niveles de dificultad: 1, 2, 3")

        print(f"\n📁 UBICACIÓN: {output_dir}/")
        print(f"🚀 ¡LISTO PARA USAR EN TU APLICACIÓN FLUTTER!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
