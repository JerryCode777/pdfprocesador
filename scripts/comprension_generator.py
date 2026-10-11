#!/usr/bin/env python3
"""
Comprension Generator - Genera preguntas de comprensión lectora
- Nivel I: 1 texto + 2 preguntas
- Nivel II: 1 texto + 3 preguntas
"""

import os
import json
import re
from typing import Dict, List, Any
import google.generativeai as genai
from dotenv import load_dotenv
import time

class ComprensionGenerator:
    def __init__(self, api_key: str = None):
        """Initialize comprension generator with Gemini 2.5 Pro"""
        load_dotenv()
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY in .env file")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def load_content_json(self, json_path: str) -> Dict[str, Any]:
        """Load content JSON file"""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_texto_nivel_i(self, numero_tema: int, total_temas: int, contenido_completo: str) -> Dict[str, Any]:
        """Generate one reading text with 2 questions (Nivel I)"""

        print(f"📝 Generando texto {numero_tema} para Comprensión Lectora I (2 preguntas)...")

        prompt = f"""
        Basándote en el siguiente contenido completo sobre comprensión lectora, genera un texto original de alta calidad educativa y 2 preguntas tipo examen de admisión.

        CONTENIDO COMPLETO SOBRE COMPRENSIÓN LECTORA:
        {contenido_completo}

        INSTRUCCIONES ESPECÍFICAS:

        1. **GENERAR TEXTO ORIGINAL**:
           - Crea un texto original de 150-200 palabras
           - Tema: Puede ser sobre ciencia, historia, literatura, sociedad, tecnología, etc.
           - Debe tener profundidad educativa apropiada para nivel secundario/universitario
           - Incluir información que permita hacer preguntas de diferentes niveles de comprensión
           - El texto debe ser claro, coherente y bien estructurado

        2. **GENERAR 2 PREGUNTAS TIPO ADMISIÓN**:
           - Usa los TIPOS DE PREGUNTAS descritos en el contenido:
             * Preguntas por el TEMA (El tema del texto es:, El asunto que trata el autor es:)
             * Preguntas por la IDEA PRINCIPAL (La idea principal es:, ¿Cuál es la afirmación principal?)
             * Preguntas por el TÍTULO (¿Qué título expresa mejor lo leído?)
             * Preguntas TEXTUALES (Según el texto:, Se afirma en el texto:)
             * Preguntas por INFERENCIAS (Del texto se infiere que:, Se deduce que:, Se colige que:)
             * Preguntas por TÉRMINOS (El significado de «x» es:, La palabra «x» significa:)
             * Preguntas por RELACIONES (La relación entre X y Y es de:)
             * Preguntas NEGATIVAS (Discrepa con lo leído:, Es falso:, No se plantea en la lectura:)

           - Distribución sugerida:
             * 1 pregunta de tipo: tema, idea principal, título, o textual (dificultad 1-2)
             * 1 pregunta de tipo: inferencia, relaciones, o término (dificultad 2-3)

           - Usa el formato y estilo de exámenes de admisión universitaria

        3. **FORMATO DE ID**:
           - IDs: comp_i_{numero_tema:03d}_001, comp_i_{numero_tema:03d}_002

        4. **OPCIONES**:
           - Siempre 5 opciones (A, B, C, D, E)
           - Solo UNA respuesta correcta
           - Distractores realistas pero incorrectos

        5. **EXPLICACIONES**:
           - Explicaciones detalladas que referencien el texto
           - Explicar por qué la respuesta es correcta
           - Mencionar por qué las otras opciones son incorrectas

        RESPONDE ÚNICAMENTE en formato JSON:

        {{
            "materia": "comprension_lectoraI",
            "numero_tema": {numero_tema},
            "total_temas": {total_temas},
            "titulo_tema": "Texto {numero_tema}",
            "texto": "Aquí va el texto original de 150-200 palabras...",
            "preguntas": [
                {{
                    "id_temporal": "comp_i_{numero_tema:03d}_001",
                    "pregunta": "¿Cuál es la idea principal del texto?",
                    "dificultad": 2,
                    "opciones": {{
                        "A": "Primera opción",
                        "B": "Segunda opción",
                        "C": "Tercera opción",
                        "D": "Cuarta opción",
                        "E": "Quinta opción"
                    }},
                    "respuesta_correcta": "B",
                    "explicacion": "La respuesta correcta es B porque...",
                    "imagen": null
                }},
                {{
                    "id_temporal": "comp_i_{numero_tema:03d}_002",
                    "pregunta": "Según el texto, se puede inferir que...",
                    "dificultad": 3,
                    "opciones": {{
                        "A": "Primera opción",
                        "B": "Segunda opción",
                        "C": "Tercera opción",
                        "D": "Cuarta opción",
                        "E": "Quinta opción"
                    }},
                    "respuesta_correcta": "C",
                    "explicacion": "La inferencia correcta es C porque...",
                    "imagen": null
                }}
            ]
        }}

        IMPORTANTE:
        - Texto original de 150-200 palabras
        - Exactamente 2 preguntas
        - JSON válido sin texto adicional
        - Campo "imagen": null en cada pregunta
        """

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Clean JSON response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            # Extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                texto_data = json.loads(json_str)

                # Verify we have 2 questions
                num_questions = len(texto_data.get('preguntas', []))
                if num_questions != 2:
                    print(f"   ⚠️ Se generaron {num_questions} preguntas en lugar de 2")

                print(f"   ✅ Generado texto {numero_tema} con {num_questions} preguntas")
                return texto_data
            else:
                raise Exception("No se encontró JSON válido en la respuesta")

        except Exception as e:
            print(f"   ❌ Error generando texto {numero_tema}: {e}")
            return None

    def generate_texto_nivel_ii(self, numero_tema: int, total_temas: int, contenido_completo: str) -> Dict[str, Any]:
        """Generate one reading text with 3 questions (Nivel II)"""

        print(f"📝 Generando texto {numero_tema} para Comprensión Lectora II (3 preguntas)...")

        prompt = f"""
        Basándote en el siguiente contenido completo sobre comprensión lectora, genera un texto original de alta calidad educativa y 3 preguntas tipo examen de admisión.

        CONTENIDO COMPLETO SOBRE COMPRENSIÓN LECTORA:
        {contenido_completo}

        INSTRUCCIONES ESPECÍFICAS:

        1. **GENERAR TEXTO ORIGINAL**:
           - Crea un texto original de 200-300 palabras
           - Tema: Puede ser sobre ciencia, historia, literatura, sociedad, tecnología, filosofía, etc.
           - Debe tener mayor profundidad educativa que Nivel I
           - Incluir argumentos, análisis, comparaciones, o exposición de ideas complejas
           - El texto debe ser claro, coherente y bien estructurado

        2. **GENERAR 3 PREGUNTAS TIPO ADMISIÓN**:
           - Usa los TIPOS DE PREGUNTAS descritos en el contenido:
             * Preguntas por el TEMA (El tema del texto es:, El asunto que trata el autor es:)
             * Preguntas por la IDEA PRINCIPAL (La idea principal es:, El autor pretende centralmente:)
             * Preguntas por el TÍTULO (¿Qué título expresa mejor lo leído?, El mejor título sería:)
             * Preguntas TEXTUALES (Según el texto:, Se afirma en el texto:, El autor afirma:)
             * Preguntas EQUIVALENTES (Según el texto, es verdadero:, Coincide con el texto:)
             * Preguntas por INFERENCIAS (Del texto se infiere que:, Se deduce que:, Se colige que:, Tácitamente se entiende que:)
             * Preguntas por TÉRMINOS CONNOTATIVOS (La frase «x» quiere decir:, El término «x» tiene el sentido de:)
             * Preguntas por RELACIONES (La relación entre X y Y es de: causalidad, secuencialidad, oposición, etc.)
             * Preguntas NEGATIVAS (Discrepa con lo leído:, Es falso:, No se plantea:, Es incompatible:)
             * Preguntas de EXTRAPOLACIÓN (Si se negara..., Si creamos el supuesto de...)

           - Distribución sugerida:
             * 1 pregunta de tipo: tema, idea principal, título, o textual (dificultad 1-2)
             * 1 pregunta de tipo: inferencia, equivalente, o término (dificultad 2)
             * 1 pregunta de tipo: relaciones, negativa, o extrapolación (dificultad 3)

           - Usa el formato y estilo de exámenes de admisión universitaria

        3. **FORMATO DE ID**:
           - IDs: comp_ii_{numero_tema:03d}_001, comp_ii_{numero_tema:03d}_002, comp_ii_{numero_tema:03d}_003

        4. **OPCIONES**:
           - Siempre 5 opciones (A, B, C, D, E)
           - Solo UNA respuesta correcta
           - Distractores realistas

        5. **EXPLICACIONES**:
           - Explicaciones detalladas que referencien el texto
           - Explicar por qué la respuesta es correcta con evidencia del texto
           - Mencionar por qué las otras opciones son incorrectas

        RESPONDE ÚNICAMENTE en formato JSON:

        {{
            "materia": "comprension_lectoraII",
            "numero_tema": {numero_tema},
            "total_temas": {total_temas},
            "titulo_tema": "Texto {numero_tema}",
            "texto": "Aquí va el texto original de 200-300 palabras...",
            "preguntas": [
                {{
                    "id_temporal": "comp_ii_{numero_tema:03d}_001",
                    "pregunta": "¿Qué afirmación del texto es correcta?",
                    "dificultad": 1,
                    "opciones": {{
                        "A": "Primera opción",
                        "B": "Segunda opción",
                        "C": "Tercera opción",
                        "D": "Cuarta opción",
                        "E": "Quinta opción"
                    }},
                    "respuesta_correcta": "C",
                    "explicacion": "La respuesta correcta es C porque...",
                    "imagen": null
                }},
                {{
                    "id_temporal": "comp_ii_{numero_tema:03d}_002",
                    "pregunta": "Del texto se puede inferir que...",
                    "dificultad": 2,
                    "opciones": {{
                        "A": "Primera opción",
                        "B": "Segunda opción",
                        "C": "Tercera opción",
                        "D": "Cuarta opción",
                        "E": "Quinta opción"
                    }},
                    "respuesta_correcta": "B",
                    "explicacion": "La inferencia correcta es B porque...",
                    "imagen": null
                }},
                {{
                    "id_temporal": "comp_ii_{numero_tema:03d}_003",
                    "pregunta": "El propósito principal del autor es:",
                    "dificultad": 3,
                    "opciones": {{
                        "A": "Primera opción",
                        "B": "Segunda opción",
                        "C": "Tercera opción",
                        "D": "Cuarta opción",
                        "E": "Quinta opción"
                    }},
                    "respuesta_correcta": "A",
                    "explicacion": "El propósito principal es A porque...",
                    "imagen": null
                }}
            ]
        }}

        IMPORTANTE:
        - Texto original de 200-300 palabras
        - Exactamente 3 preguntas
        - JSON válido sin texto adicional
        - Campo "imagen": null en cada pregunta
        """

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Clean JSON response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            # Extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                texto_data = json.loads(json_str)

                # Verify we have 3 questions
                num_questions = len(texto_data.get('preguntas', []))
                if num_questions != 3:
                    print(f"   ⚠️ Se generaron {num_questions} preguntas en lugar de 3")

                print(f"   ✅ Generado texto {numero_tema} con {num_questions} preguntas")
                return texto_data
            else:
                raise Exception("No se encontró JSON válido en la respuesta")

        except Exception as e:
            print(f"   ❌ Error generando texto {numero_tema}: {e}")
            return None

    def generate_comprension_questions(
        self,
        content_file: str,
        output_dir_i: str,
        output_dir_ii: str,
        num_textos_i: int = 20,
        num_textos_ii: int = 20
    ):
        """Generate reading comprehension questions for both levels"""

        # Load content
        print(f"📖 Cargando contenido desde {content_file}...")
        with open(content_file, 'r', encoding='utf-8') as f:
            contenido_completo = f.read()

        print(f"✅ Contenido cargado: {len(contenido_completo)} caracteres")

        # Generate Nivel I (2 preguntas por texto)
        print(f"\n📚 Generando {num_textos_i} textos para Comprensión Lectora I...")
        print("=" * 60)

        successful_i = 0
        for i in range(1, num_textos_i + 1):
            texto_data = self.generate_texto_nivel_i(i, num_textos_i, contenido_completo)

            if texto_data:
                # Save file
                filename = f"tema_{i:03d}_texto_{i}.json"
                filepath = os.path.join(output_dir_i, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(texto_data, f, ensure_ascii=False, indent=2)

                print(f"   💾 Guardado: {filename}")
                successful_i += 1

            # Pause between generations
            time.sleep(3)

        print(f"\n✅ Nivel I completado: {successful_i}/{num_textos_i} textos generados")

        # Generate Nivel II (3 preguntas por texto)
        print(f"\n📚 Generando {num_textos_ii} textos para Comprensión Lectora II...")
        print("=" * 60)

        successful_ii = 0
        for i in range(1, num_textos_ii + 1):
            texto_data = self.generate_texto_nivel_ii(i, num_textos_ii, contenido_completo)

            if texto_data:
                # Save file
                filename = f"tema_{i:03d}_texto_{i}.json"
                filepath = os.path.join(output_dir_ii, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(texto_data, f, ensure_ascii=False, indent=2)

                print(f"   💾 Guardado: {filename}")
                successful_ii += 1

            # Pause between generations
            time.sleep(3)

        print(f"\n✅ Nivel II completado: {successful_ii}/{num_textos_ii} textos generados")

        print("\n" + "=" * 60)
        print(f"📊 RESUMEN TOTAL:")
        print(f"   Nivel I: {successful_i}/{num_textos_i} textos ({successful_i * 2} preguntas)")
        print(f"   Nivel II: {successful_ii}/{num_textos_ii} textos ({successful_ii * 3} preguntas)")
        print(f"   Total preguntas generadas: {(successful_i * 2) + (successful_ii * 3)}")
        print("=" * 60)
