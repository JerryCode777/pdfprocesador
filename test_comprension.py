#!/usr/bin/env python3
"""
Test de Comprensión Lectora - Verifica la calidad de las preguntas generadas
"""

import os
import json
import sys
from pathlib import Path

def test_json_file(filepath: str, expected_questions: int):
    """Test a single JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        errors = []

        # Check required fields
        required_fields = ['materia', 'numero_tema', 'total_temas', 'titulo_tema', 'texto', 'preguntas']
        for field in required_fields:
            if field not in data:
                errors.append(f"Campo faltante: {field}")

        # Check text
        if 'texto' in data:
            texto = data['texto']
            words = len(texto.split())
            if words < 50:
                errors.append(f"Texto muy corto: {words} palabras")

        # Check questions
        if 'preguntas' in data:
            preguntas = data['preguntas']
            if len(preguntas) != expected_questions:
                errors.append(f"Preguntas incorrectas: {len(preguntas)} (esperado: {expected_questions})")

            for i, p in enumerate(preguntas, 1):
                # Check question fields
                required_q = ['id_temporal', 'pregunta', 'dificultad', 'opciones', 'respuesta_correcta', 'explicacion', 'imagen']
                for field in required_q:
                    if field not in p:
                        errors.append(f"Pregunta {i}: falta campo '{field}'")

                # Check options
                if 'opciones' in p:
                    if set(p['opciones'].keys()) != {'A', 'B', 'C', 'D', 'E'}:
                        errors.append(f"Pregunta {i}: opciones incorrectas")

                # Check difficulty
                if 'dificultad' in p and p['dificultad'] not in [1, 2, 3]:
                    errors.append(f"Pregunta {i}: dificultad inválida: {p['dificultad']}")

        return errors

    except Exception as e:
        return [f"Error cargando archivo: {e}"]

def test_directory(directory: str, nivel: str, expected_questions: int):
    """Test all files in a directory"""
    print(f"\n📁 Probando: {directory}")
    print(f"   Nivel: {nivel} ({expected_questions} preguntas por texto)")
    print("─" * 60)

    if not os.path.exists(directory):
        print(f"❌ Directorio no existe")
        return

    files = sorted(Path(directory).glob("tema_*.json"))
    if not files:
        print(f"❌ No hay archivos JSON")
        return

    print(f"📄 Archivos: {len(files)}")

    total_errors = 0
    valid_files = 0

    for filepath in files:
        errors = test_json_file(str(filepath), expected_questions)

        if errors:
            print(f"   ❌ {filepath.name}: {len(errors)} error(es)")
            for err in errors[:2]:
                print(f"      • {err}")
            total_errors += len(errors)
        else:
            valid_files += 1

    print(f"\n📊 Resultado:")
    print(f"   ✅ Válidos: {valid_files}/{len(files)}")
    print(f"   ❌ Errores: {total_errors}")

def main():
    print("\n🧪 TEST DE COMPRENSIÓN LECTORA")
    print("═" * 60)

    base_dir = "output/questions"

    # Test Nivel I
    test_directory(
        os.path.join(base_dir, "comprension_lectoraI"),
        "Comprensión Lectora I",
        expected_questions=2
    )

    # Test Nivel II
    test_directory(
        os.path.join(base_dir, "comprension_lectoraII"),
        "Comprensión Lectora II",
        expected_questions=3
    )

    print("\n✅ Test completado\n")

if __name__ == "__main__":
    main()
