#!/usr/bin/env python3
"""
Comprension Ingles Generator - Genera preguntas de comprensión lectora en inglés
- Nivel básico: 1 texto en inglés + 2 preguntas
"""

import os
import json
import re
from typing import Dict, List, Any
import google.generativeai as genai
from dotenv import load_dotenv
import time

class ComprensionInglesGenerator:
    def __init__(self, api_key: str = None):
        """Initialize comprension ingles generator with Gemini 2.5 Pro"""
        load_dotenv()
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY in .env file")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def generate_texto_ingles(self, numero_tema: int, total_temas: int) -> Dict[str, Any]:
        """Generate one English reading text with 2 questions"""

        print(f"📝 Generando texto {numero_tema} en inglés (2 preguntas)...")

        prompt = f"""
        Generate an original English reading comprehension text with 2 questions. This is for basic level English learners (A2-B1).

        INSTRUCTIONS:

        1. **GENERATE ORIGINAL ENGLISH TEXT**:
           - Create an original text of 120-180 words
           - Topic: Daily life, technology, health, environment, culture, education, etc.
           - Basic to intermediate level vocabulary (A2-B1 CEFR)
           - Clear, simple sentences with some compound sentences
           - Present simple, present continuous, past simple tenses primarily
           - Include vocabulary that allows for comprehension questions
           - Well-structured with 2-3 paragraphs

        2. **GENERATE 2 COMPREHENSION QUESTIONS IN ENGLISH**:
           - Questions must be in ENGLISH
           - Answer options must be in ENGLISH
           - Question types:
             * Main idea (What is the main idea of the text?)
             * Specific information (According to the text:, The text mentions that:)
             * Inference (From the text we can infer that:, It can be deduced that:)
             * Vocabulary in context (The word «X» in the text means:)
             * Purpose (The purpose of the text is:)
             * True/False about the text (According to the text, it is true that:)

           - Distribution:
             * 1 question: main idea, specific info, or vocabulary (difficulty 1-2)
             * 1 question: inference, purpose, or interpretation (difficulty 2-3)

        3. **ID FORMAT**:
           - IDs: comp_ing_{numero_tema:03d}_001, comp_ing_{numero_tema:03d}_002

        4. **OPTIONS**:
           - Always 5 options in ENGLISH (A, B, C, D, E)
           - Only ONE correct answer
           - Realistic distractors in English

        5. **EXPLANATIONS IN BILINGUAL FORMAT (SPANISH + ENGLISH)**:
           - Detailed explanations combining Spanish and English
           - Reference the English text with quotes
           - Explain in Spanish but include English phrases from the text
           - Format: "La respuesta correcta es B porque el texto dice 'phrase in English'... The other options are incorrect because..."
           - Help students understand both the answer and the English vocabulary

        RESPOND ONLY in JSON format:

        {{
            "materia": "comprension_ingles",
            "numero_tema": {numero_tema},
            "total_temas": {total_temas},
            "titulo_tema": "Texto {numero_tema}",
            "texto": "Here goes the original English text of 120-180 words about an interesting educational topic...",
            "preguntas": [
                {{
                    "id_temporal": "comp_ing_{numero_tema:03d}_001",
                    "pregunta": "What is the main idea of the text?",
                    "dificultad": 2,
                    "opciones": {{
                        "A": "First option in English",
                        "B": "Second option in English",
                        "C": "Third option in English",
                        "D": "Fourth option in English",
                        "E": "Fifth option in English"
                    }},
                    "respuesta_correcta": "B",
                    "explicacion": "La respuesta correcta es B porque el texto dice 'the main point in English'. The text clearly states that... Las otras opciones son incorrectas: A dice 'wrong idea' pero el texto no menciona esto, C confunde 'concept X' con 'concept Y', etc.",
                    "imagen": null
                }},
                {{
                    "id_temporal": "comp_ing_{numero_tema:03d}_002",
                    "pregunta": "According to the text, we can infer that:",
                    "dificultad": 3,
                    "opciones": {{
                        "A": "First option in English",
                        "B": "Second option in English",
                        "C": "Third option in English",
                        "D": "Fourth option in English",
                        "E": "Fifth option in English"
                    }},
                    "respuesta_correcta": "C",
                    "explicacion": "La inferencia correcta es C. Aunque el texto no lo dice explícitamente, podemos deducirlo cuando menciona 'key phrase from text'. This implies that... Las otras opciones no son correctas porque el texto no apoya esas conclusiones.",
                    "imagen": null
                }}
            ]
        }}

        IMPORTANT:
        - Text in ENGLISH (120-180 words, basic level A2-B1)
        - Questions in ENGLISH
        - Options in ENGLISH
        - Explanations BILINGUAL (Spanish + English combined)
        - Exactly 2 questions
        - Valid JSON without additional text
        - "imagen": null field in each question
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

                # Count words in English text
                texto = texto_data.get('texto', '')
                word_count = len(texto.split())
                print(f"   ✅ Generado texto {numero_tema} ({word_count} palabras) con {num_questions} preguntas")
                return texto_data
            else:
                raise Exception("No se encontró JSON válido en la respuesta")

        except Exception as e:
            print(f"   ❌ Error generando texto {numero_tema}: {e}")
            return None

    def generate_comprension_ingles(
        self,
        output_dir: str,
        num_textos: int = 20
    ):
        """Generate English reading comprehension questions"""

        print(f"\n📚 Generando {num_textos} textos en inglés...")
        print("=" * 60)

        successful = 0
        for i in range(1, num_textos + 1):
            texto_data = self.generate_texto_ingles(i, num_textos)

            if texto_data:
                # Save file
                filename = f"tema_{i:03d}_texto_{i}.json"
                filepath = os.path.join(output_dir, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(texto_data, f, ensure_ascii=False, indent=2)

                print(f"   💾 Guardado: {filename}")
                successful += 1

            # Pause between generations
            time.sleep(3)

        print(f"\n✅ Completado: {successful}/{num_textos} textos generados")
        print(f"📊 Total preguntas: {successful * 2}")
        print("=" * 60)
