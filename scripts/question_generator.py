#!/usr/bin/env python3
"""
Question Generator - Genera preguntas basadas en los JSON de contenido extraído
Organiza por temas en el orden de las páginas y genera 15 preguntas por tema
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv
import time
from datetime import datetime
from collections import OrderedDict

class QuestionGenerator:
    def __init__(self, api_key: str = None):
        """Initialize question generator with Gemini 2.5 Pro"""
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

    def organize_topics_by_page_order(self, content_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Organize topics in page order and collect content for each topic"""
        print("📋 Organizando temas por orden de páginas...")

        pages = content_data.get('pages', [])
        topics_content = OrderedDict()
        topic_first_page = {}

        # Collect content for each topic in page order
        for page in sorted(pages, key=lambda x: x.get('page_number', 0)):
            page_topics = page.get('topics', [])
            page_content = page.get('content', '').strip()
            page_num = page.get('page_number', 0)

            for topic in page_topics:
                if topic not in topics_content:
                    topics_content[topic] = {
                        'content_parts': [],
                        'pages': []
                    }
                    topic_first_page[topic] = page_num

                if page_content:
                    topics_content[topic]['content_parts'].append(page_content)
                    topics_content[topic]['pages'].append(page_num)

        # Convert to organized list
        organized_topics = []
        for i, (topic, data) in enumerate(topics_content.items(), 1):
            combined_content = ' '.join(data['content_parts'])
            if combined_content.strip():  # Only include topics with content
                organized_topics.append({
                    'numero_tema': i,
                    'titulo_tema': topic,
                    'contenido': combined_content,
                    'paginas': data['pages'],
                    'primera_pagina': topic_first_page[topic]
                })

        # Sort by first page appearance
        organized_topics.sort(key=lambda x: x['primera_pagina'])

        # Update topic numbers after sorting
        for i, topic_data in enumerate(organized_topics, 1):
            topic_data['numero_tema'] = i

        print(f"   ✅ Organizados {len(organized_topics)} temas por orden de páginas")
        return organized_topics

    def generate_questions_for_topic(self, materia: str, topic_data: Dict[str, Any], total_temas: int) -> Dict[str, Any]:
        """Generate 15 questions for a specific topic using Gemini"""

        topic_title = topic_data['titulo_tema']
        topic_content = topic_data['contenido']
        topic_number = topic_data['numero_tema']

        print(f"🤖 Generando preguntas para tema {topic_number}: {topic_title}")

        # Create subject prefix for ID
        subject_prefix = materia.lower().replace(' ', '_')[:8]

        prompt = f"""
        Genera exactamente 15 preguntas de opción múltiple basadas en el siguiente contenido educativo del tema "{topic_title}" de {materia}.

        CONTENIDO DEL TEMA:
        {topic_content}

        INSTRUCCIONES ESPECÍFICAS:

        1. **PREGUNTAS BASADAS EN CONTENIDO**:
           - Genera preguntas ÚNICAMENTE basadas en el contenido proporcionado
           - NO inventes información que no esté en el contenido
           - Enfócate en conceptos, definiciones, explicaciones educativas
           - NUNCA hagas referencia al texto fuente (no uses "según el texto", "el texto menciona", etc.)
           - Formula las preguntas como conocimiento directo y natural

        2. **FORMATO DE ECUACIONES MATEMÁTICAS**:
           - TODAS las ecuaciones, fórmulas y expresiones matemáticas deben estar en formato LaTeX
           - Usa dobles signos de dólar para ecuaciones: $$ecuación$$
           - Ejemplos: $$x^2 + y^2 = z^2$$, $$\\frac{{a}}{{b}} = c$$, $$\\sqrt{{x + 1}}$$
           - Para variables en texto: $x$, $y$, $\\pi$, etc.
           - Esto aplica tanto a preguntas, opciones como explicaciones

        3. **ESTRUCTURA DE PREGUNTAS**:
           - 5 preguntas de dificultad 1 (básicas, definiciones)
           - 7 preguntas de dificultad 2 (comprensión, relaciones)
           - 3 preguntas de dificultad 3 (análisis, aplicación)

        3. **FORMATO DE ID**:
           - Usar prefijo: {subject_prefix}
           - Formato: {subject_prefix}_{topic_number:03d}_001, {subject_prefix}_{topic_number:03d}_002, etc.

        4. **OPCIONES**:
           - Siempre 5 opciones (A, B, C, D, E)
           - Solo UNA respuesta correcta
           - Distractores realistas pero claramente incorrectos
           - Si contienen matemáticas, usar LaTeX: "A": "$$x = \\frac{{-b \\pm \\sqrt{{b^2-4ac}}}}{{2a}}$$"

        5. **EXPLICACIONES**:
           - Explicaciones pedagógicas detalladas y naturales
           - Si incluyen matemáticas, usar LaTeX correctamente
           - Explicar por qué la respuesta es correcta y las otras incorrectas
           - NO hacer referencia al texto fuente en las explicaciones
           - Presentar la información como conocimiento establecido

        RESPONDE ÚNICAMENTE en formato JSON:

        {{
            "materia": "{materia.lower().replace(' ', '_')}",
            "numero_tema": {topic_number},
            "total_temas": {total_temas},
            "titulo_tema": "{topic_title}",
            "preguntas": [
                {{
                    "id_temporal": "{subject_prefix}_{topic_number:03d}_001",
                    "pregunta": "¿Cuál es la definición fundamental de materia?",
                    "dificultad": 1,
                    "opciones": {{
                        "A": "Todo lo que tiene peso y es visible",
                        "B": "Todo lo que ocupa espacio y tiene masa",
                        "C": "Cualquier sustancia que se puede tocar",
                        "D": "Únicamente los elementos químicos",
                        "E": "Todo aquello que posee energía"
                    }},
                    "respuesta_correcta": "B",
                    "explicacion": "La materia se define como todo lo que ocupa espacio y tiene masa. Esta definición incluye tanto sustancias visibles como invisibles (como el aire), sólidas, líquidas y gaseosas. Las otras opciones son incorrectas porque la materia no se limita a lo visible, tangible o a elementos específicos.",
                    "imagen": null
                }}
            ]
        }}

        IMPORTANTE:
        - Exactamente 15 preguntas
        - Solo información del contenido proporcionado
        - JSON válido sin texto adicional
        - NUNCA mencionar "el texto", "según el contenido", etc.
        - Preguntas y explicaciones como conocimiento natural y directo
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

            # Fix LaTeX escapes in response before parsing JSON
            # Replace single backslashes with double backslashes for proper JSON escaping
            response_text = re.sub(r'(?<!\\)\\(?![\\"/bfnrtux])', r'\\\\', response_text)

            # Extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                questions_data = json.loads(json_str)

                # Verify we have 15 questions
                num_questions = len(questions_data.get('preguntas', []))
                if num_questions != 15:
                    print(f"   ⚠️ Se generaron {num_questions} preguntas en lugar de 15")

                print(f"   ✅ Generadas {num_questions} preguntas para {topic_title}")
                return questions_data
            else:
                raise Exception("No se encontró JSON válido en la respuesta")

        except Exception as e:
            print(f"   ❌ Error generando preguntas para {topic_title}: {e}")
            # Return empty structure on error
            return {
                "materia": materia.lower().replace(' ', '_'),
                "numero_tema": topic_number,
                "total_temas": total_temas,
                "titulo_tema": topic_title,
                "preguntas": []
            }

    def process_content_file(self, content_file_path: str, output_base_dir: str) -> bool:
        """Process a single content file to generate questions"""
        print(f"\n📄 Procesando: {content_file_path}")

        try:
            # Load content data
            content_data = self.load_content_json(content_file_path)
            subject = content_data.get('metadata', {}).get('subject', 'UNKNOWN')

            print(f"📚 Materia: {subject}")

            # Organize topics by page order
            organized_topics = self.organize_topics_by_page_order(content_data)

            if not organized_topics:
                print("❌ No se encontraron temas con contenido")
                return False

            total_temas = len(organized_topics)
            print(f"📊 Total temas a procesar: {total_temas}")

            # Create output directory for this subject
            subject_dir = os.path.join(output_base_dir, subject.lower().replace(' ', '_'))
            os.makedirs(subject_dir, exist_ok=True)

            successful_topics = 0

            # Generate questions for each topic
            for topic_data in organized_topics:
                try:
                    questions_json = self.generate_questions_for_topic(subject, topic_data, total_temas)

                    # Save questions file
                    topic_filename = f"tema_{topic_data['numero_tema']:03d}_{topic_data['titulo_tema'].lower().replace(' ', '_').replace('/', '_')}.json"
                    topic_output_path = os.path.join(subject_dir, topic_filename)

                    with open(topic_output_path, 'w', encoding='utf-8') as f:
                        json.dump(questions_json, f, ensure_ascii=False, indent=2)

                    print(f"   💾 Guardado: {topic_filename}")
                    successful_topics += 1

                    # Brief pause between topics
                    time.sleep(2)

                except Exception as e:
                    print(f"   ❌ Error procesando tema {topic_data['titulo_tema']}: {e}")
                    continue

            print(f"✅ Completado: {successful_topics}/{total_temas} temas procesados")
            return successful_topics > 0

        except Exception as e:
            print(f"❌ Error procesando archivo {content_file_path}: {e}")
            return False

    def process_all_content_files(self, content_dir: str, output_dir: str) -> None:
        """Process all content files to generate questions"""
        content_files = list(Path(content_dir).glob("*_content.json"))

        if not content_files:
            print("❌ No se encontraron archivos de contenido")
            return

        print(f"🚀 INICIANDO GENERACIÓN DE PREGUNTAS")
        print(f"📁 Directorio de contenido: {content_dir}")
        print(f"📁 Directorio de salida: {output_dir}")
        print(f"📄 Archivos a procesar: {len(content_files)}")
        print("=" * 60)

        os.makedirs(output_dir, exist_ok=True)

        successful_files = 0
        total_files = len(content_files)

        for i, content_file in enumerate(content_files, 1):
            print(f"\n🎯 PROCESANDO ARCHIVO {i}/{total_files}")

            if self.process_content_file(str(content_file), output_dir):
                successful_files += 1

            # Pause between files
            if i < total_files:
                print("⏳ Pausa de 5 segundos entre archivos...")
                time.sleep(5)

        # Final summary
        print("\n" + "="*60)
        print("🎉 GENERACIÓN DE PREGUNTAS COMPLETADA")
        print("="*60)
        print(f"✅ Archivos procesados exitosamente: {successful_files}/{total_files}")
        print(f"📁 Preguntas guardadas en: {output_dir}")

def main():
    """Main function"""
    print("❓ Question Generator - Generador de Preguntas por Temas")
    print("=" * 60)

    # Check API key
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key or api_key == 'your_gemini_api_key_here':
        print("❌ ERROR: API key no configurado")
        return

    # Initialize generator
    generator = QuestionGenerator()

    # Process all content files
    content_dir = "output/content"
    output_dir = "output/questions"

    if not os.path.exists(content_dir):
        print(f"❌ No existe el directorio de contenido: {content_dir}")
        return

    generator.process_all_content_files(content_dir, output_dir)

if __name__ == "__main__":
    main()