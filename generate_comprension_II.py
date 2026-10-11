#!/usr/bin/env python3
"""
Generador solo para Comprensión Lectora II
Para continuar la generación que se detuvo
"""

import sys
import os
import time
from datetime import datetime
sys.path.append('scripts')

from comprension_generator import ComprensionGenerator

def main():
    print("📖 GENERADOR DE COMPRENSIÓN LECTORA II")
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

    # Check if content file exists
    content_file = "output/content/razonamiento_verbal_content.json"
    if not os.path.exists(content_file):
        print(f"❌ ERROR: No existe el archivo {content_file}")
        return

    try:
        # Initialize generator
        print("🔧 Inicializando generador...")
        generator = ComprensionGenerator()

        # Create output directory
        output_dir_ii = "output/questions/comprension_lectoraII"
        os.makedirs(output_dir_ii, exist_ok=True)

        # Load content
        print(f"\n📖 Cargando contenido desde {content_file}...")
        with open(content_file, 'r', encoding='utf-8') as f:
            contenido_completo = f.read()

        print(f"✅ Contenido cargado: {len(contenido_completo)} caracteres")

        # Generate Nivel II (3 preguntas por texto)
        num_textos = 20
        print(f"\n📚 Generando {num_textos} textos para Comprensión Lectora II...")
        print("=" * 60)

        successful = 0
        for i in range(1, num_textos + 1):
            texto_data = generator.generate_texto_nivel_ii(i, num_textos, contenido_completo)

            if texto_data:
                # Save file
                filename = f"tema_{i:03d}_texto_{i}.json"
                filepath = os.path.join(output_dir_ii, filename)

                import json
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(texto_data, f, ensure_ascii=False, indent=2)

                print(f"   💾 Guardado: {filename}")
                successful += 1

            # Pause between generations
            time.sleep(3)

        print(f"\n✅ Nivel II completado: {successful}/{num_textos} textos generados")
        print(f"📊 Total preguntas: {successful * 3}")
        print(f"📁 Ubicación: {output_dir_ii}/")
        print("\n🎉 ¡GENERACIÓN COMPLETADA!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
