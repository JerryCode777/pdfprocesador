#!/usr/bin/env python3
"""
Batch Content Extractor - Procesa PDFs en lotes de 100 páginas
Mantiene la misma estructura de salida pero es más seguro para archivos grandes
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
import fitz  # PyMuPDF for page splitting

class ProgressTracker:
    def __init__(self, total_files: int):
        self.total_files = total_files
        self.current_file = 0
        self.start_time = time.time()

    def update_file(self, filename: str, step: str = ""):
        self.current_file += 1
        elapsed = time.time() - self.start_time

        print("\n" + "="*80)
        print(f"📊 PROGRESO: [{self.current_file}/{self.total_files}] ({self.current_file/self.total_files*100:.1f}%)")
        print(f"⏱️  Tiempo transcurrido: {elapsed/60:.1f} minutos")

        if self.current_file > 1:
            avg_time = elapsed / (self.current_file - 1)
            remaining = avg_time * (self.total_files - self.current_file)
            print(f"⏳ Tiempo restante: {remaining/60:.1f} minutos")

        print(f"📄 Archivo: {filename}")
        if step:
            print(f"🔄 Estado: {step}")
        print("="*80)

class BatchContentExtractor:
    def __init__(self, api_key: str = None, batch_size: int = 100):
        """Initialize batch content extractor"""
        load_dotenv()
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY in .env file")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.batch_size = batch_size

    def get_pdf_info(self, pdf_path: str) -> Dict[str, Any]:
        """Get basic PDF information"""
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        doc.close()
        return {"total_pages": total_pages}

    def create_batch_pdf(self, original_pdf_path: str, start_page: int, end_page: int, temp_path: str) -> str:
        """Create a temporary PDF with specified page range"""
        doc = fitz.open(original_pdf_path)

        # Create new document with selected pages
        new_doc = fitz.open()
        for page_num in range(start_page, min(end_page + 1, len(doc))):
            page = doc.load_page(page_num)
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

        # Save temporary PDF
        new_doc.save(temp_path)
        new_doc.close()
        doc.close()

        return temp_path

    def extract_content_from_batch(self, batch_pdf_path: str, subject: str, batch_num: int, start_page: int) -> Dict[str, Any]:
        """Extract content from a batch PDF using Gemini"""

        print(f"📤 Subiendo lote {batch_num} a Gemini...")
        pdf_file = genai.upload_file(batch_pdf_path)
        print(f"   ✅ Lote {batch_num} subido")

        print(f"⏳ Esperando procesamiento del lote {batch_num}...")
        dots = 0
        while pdf_file.state.name == "PROCESSING":
            dots = (dots + 1) % 4
            print(f"\r   🔄 Procesando lote {batch_num}{'.' * dots}{' ' * (3-dots)}", end='', flush=True)
            time.sleep(2)
            pdf_file = genai.get_file(pdf_file.name)

        if pdf_file.state.name == "FAILED":
            raise Exception(f"PDF batch processing failed: {pdf_file.state}")

        print(f"\n   ✅ Lote {batch_num} procesado")

        # Prompt específico para el lote
        prompt = f"""
        Analiza este lote de páginas del PDF educativo de {subject} (lote {batch_num}).

        ## INSTRUCCIONES ESPECÍFICAS:

        1. **CONTENIDO EDUCATIVO ÚNICAMENTE**:
           - Extrae SOLO el contenido educativo principal de cada página
           - IGNORA: encabezados, pies de página, números de página, referencias
           - IGNORA: preguntas, ejercicios, exámenes, evaluaciones
           - ENFÓCATE en: teoría, conceptos, definiciones, explicaciones

        2. **NUMERACIÓN CORRECTA**:
           - Las páginas en este lote empiezan desde la página {start_page + 1}
           - Mantén la numeración original del documento completo

        3. **IDENTIFICACIÓN DE TEMAS**:
           - Identifica los temas específicos de cada página
           - Mantén coherencia con el documento completo

        ## FORMATO DE RESPUESTA:

        {{
            "batch_info": {{
                "batch_number": {batch_num},
                "start_page": {start_page + 1},
                "pages_in_batch": "número de páginas procesadas en este lote"
            }},
            "topics": [
                "Lista de temas encontrados en este lote"
            ],
            "pages": [
                {{
                    "page_number": {start_page + 1},
                    "content": "Contenido educativo de esta página",
                    "topics": ["temas de esta página"],
                    "has_content": true
                }}
            ]
        }}

        IMPORTANTE: Responde ÚNICAMENTE con JSON válido.
        """

        try:
            print(f"🤖 Analizando contenido del lote {batch_num}...")

            response = self.model.generate_content([pdf_file, prompt])
            print(f"   ✅ Lote {batch_num} analizado")

            # Clean and extract JSON
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)

                # Clean up the file
                genai.delete_file(pdf_file.name)
                print(f"   🗑️ Lote {batch_num} limpiado")
                return data
            else:
                raise Exception("No se encontró JSON válido en la respuesta")

        except Exception as e:
            try:
                genai.delete_file(pdf_file.name)
            except:
                pass
            raise e

    def combine_batch_results(self, batch_results: List[Dict], subject: str, total_pages: int) -> Dict[str, Any]:
        """Combine all batch results into final structure"""
        print(f"📋 Combinando resultados de {len(batch_results)} lotes...")

        # Combine all topics (remove duplicates)
        all_topics = set()
        all_pages = []

        for batch_data in batch_results:
            # Add topics
            batch_topics = batch_data.get('topics', [])
            all_topics.update(batch_topics)

            # Add pages
            batch_pages = batch_data.get('pages', [])
            all_pages.extend(batch_pages)

        # Sort pages by page number
        all_pages.sort(key=lambda x: x.get('page_number', 0))

        # Count pages with actual content
        pages_with_content = len([p for p in all_pages if p.get('has_content', False) and p.get('content', '').strip()])

        # Create final structure (same as original extractor)
        final_result = {
            "metadata": {
                "subject": subject,
                "total_pages": total_pages,
                "processing_method": "gemini-2.5-pro-batch-100pages",
                "batches_processed": len(batch_results)
            },
            "topics": sorted(list(all_topics)),
            "pages": all_pages,
            "content_summary": {
                "pages_with_content": pages_with_content,
                "main_topics_covered": sorted(list(all_topics))[:10],  # Top 10 topics
                "content_type": "educational_theory_only"
            }
        }

        print(f"   ✅ Combinación completada")
        print(f"   📄 Total páginas: {len(all_pages)}")
        print(f"   🎯 Total temas: {len(all_topics)}")
        print(f"   📚 Páginas con contenido: {pages_with_content}")

        return final_result

    def process_single_pdf_in_batches(self, pdf_path: str, output_dir: str, progress: ProgressTracker) -> str:
        """Process a single PDF in batches"""
        filename = Path(pdf_path).stem
        subject = filename.replace("BANCO DE CONTENIDO DIGITAL - ", "").replace(".pdf", "")

        progress.update_file(filename, "Analizando PDF y dividiendo en lotes")

        try:
            # Get PDF info
            file_size = Path(pdf_path).stat().st_size / (1024 * 1024)  # MB
            pdf_info = self.get_pdf_info(pdf_path)
            total_pages = pdf_info['total_pages']

            print(f"📏 Tamaño: {file_size:.1f} MB")
            print(f"📄 Total páginas: {total_pages}")

            # Calculate batches needed
            total_batches = (total_pages + self.batch_size - 1) // self.batch_size
            print(f"🔢 Dividiendo en {total_batches} lotes de {self.batch_size} páginas")

            batch_results = []
            temp_dir = f"temp_batches_{subject}"
            os.makedirs(temp_dir, exist_ok=True)

            try:
                # Process each batch
                for batch_num in range(total_batches):
                    start_page = batch_num * self.batch_size
                    end_page = min(start_page + self.batch_size - 1, total_pages - 1)

                    print(f"\n📦 PROCESANDO LOTE {batch_num + 1}/{total_batches}")
                    print(f"   📄 Páginas {start_page + 1} a {end_page + 1}")

                    # Create temporary batch PDF
                    temp_batch_path = os.path.join(temp_dir, f"batch_{batch_num}.pdf")
                    self.create_batch_pdf(pdf_path, start_page, end_page, temp_batch_path)

                    # Process batch
                    batch_result = self.extract_content_from_batch(
                        temp_batch_path, subject, batch_num + 1, start_page
                    )
                    batch_results.append(batch_result)

                    # Clean up temporary batch file
                    os.remove(temp_batch_path)

                    # Pause between batches
                    if batch_num < total_batches - 1:
                        print(f"   ⏳ Pausa de 2 segundos antes del siguiente lote...")
                        time.sleep(2)

                # Combine all batch results
                print(f"\n🔄 COMBINANDO RESULTADOS...")
                final_result = self.combine_batch_results(batch_results, subject, total_pages)

                # Add processing metadata
                final_result['metadata']['filename'] = filename
                final_result['metadata']['processing_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Save final result
                output_file = os.path.join(output_dir, f"{subject.lower().replace(' ', '_')}_content.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(final_result, f, ensure_ascii=False, indent=2)

                print(f"\n📊 RESULTADOS FINALES DE {subject}:")
                print(f"   📄 Total páginas: {final_result['metadata']['total_pages']}")
                print(f"   📚 Páginas con contenido: {final_result['content_summary']['pages_with_content']}")
                print(f"   🎯 Temas identificados: {len(final_result['topics'])}")
                print(f"   🔢 Lotes procesados: {final_result['metadata']['batches_processed']}")
                print(f"   💾 Guardado en: {output_file}")

                return output_file

            finally:
                # Clean up temp directory
                import shutil
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

        except Exception as e:
            print(f"❌ ERROR procesando {pdf_path}: {e}")
            raise e

    def process_all_pdfs(self, pdfs_dir: str, output_dir: str) -> List[str]:
        """Process all PDF files in batches"""
        pdf_files = list(Path(pdfs_dir).glob("*.pdf"))

        if not pdf_files:
            print("❌ No se encontraron archivos PDF")
            return []

        progress = ProgressTracker(len(pdf_files))

        print("\n🚀 INICIANDO PROCESAMIENTO POR LOTES")
        print(f"📁 Directorio: {pdfs_dir}")
        print(f"📄 Total archivos: {len(pdf_files)}")
        print(f"🔢 Tamaño de lote: {self.batch_size} páginas")
        print(f"🕐 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Sort files by size (smallest first)
        pdf_files.sort(key=lambda x: x.stat().st_size)

        output_files = []
        successful = 0
        failed = 0

        for i, pdf_file in enumerate(pdf_files):
            try:
                print(f"\n🎯 PROCESANDO ARCHIVO {i+1}/{len(pdf_files)}")
                output_file = self.process_single_pdf_in_batches(str(pdf_file), output_dir, progress)
                output_files.append(output_file)
                successful += 1

                # Pause between files
                if i < len(pdf_files) - 1:
                    print(f"⏳ Pausa de 5 segundos entre archivos...")
                    time.sleep(5)

            except Exception as e:
                failed += 1
                print(f"❌ ERROR en {pdf_file.name}: {e}")
                print("⏭️ Continuando con el siguiente archivo...")
                continue

        # Final summary
        total_time = time.time() - progress.start_time
        print("\n" + "="*80)
        print("🎉 PROCESAMIENTO POR LOTES COMPLETADO")
        print("="*80)
        print(f"✅ Archivos exitosos: {successful}")
        print(f"❌ Archivos fallidos: {failed}")
        print(f"⏱️ Tiempo total: {total_time/60:.1f} minutos")
        print("="*80)

        return output_files

def main():
    """Main function"""
    print("📦 Batch Content Extractor - Procesamiento por Lotes de 100 páginas")
    print("=" * 70)

    # Check API key
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key or api_key == 'your_gemini_api_key_here':
        print("❌ ERROR: API key no configurado")
        return

    # Initialize extractor
    extractor = BatchContentExtractor(batch_size=100)

    # Process all PDFs
    pdfs_dir = "bancos"
    output_dir = "output/content"

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Process all PDFs
    output_files = extractor.process_all_pdfs(pdfs_dir, output_dir)

    if output_files:
        print(f"\n📁 Archivos generados:")
        for file in output_files:
            print(f"  📄 {file}")

if __name__ == "__main__":
    main()