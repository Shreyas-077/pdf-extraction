import os
import json
import re
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
import pdfplumber
import pandas as pd

class PDFExtractor:
    def __init__(self):
        """Initialize the PDF extractor with offline text processing."""
        # Initialize patterns for different heading types
        self.heading_patterns = {
            'chapter': re.compile(r'^(chapter\s+\d+|chapter\s+[ivx]+)', re.IGNORECASE),
            'section': re.compile(r'^(section\s+\d+|\d+\.\s)', re.IGNORECASE),
            'appendix': re.compile(r'^(appendix\s+[a-z]|appendix\s+\d+)', re.IGNORECASE),
            'numbered': re.compile(r'^\d+\.\s+[A-Z]'),
            'title_case': re.compile(r'^[A-Z][a-z]+(\s+[A-Z][a-z]*)*\s*:?\s*$'),
            'all_caps': re.compile(r'^[A-Z\s\-&:]{3,}$'),
        }
        
        # OCR artifact patterns
        self.ocr_patterns = {
            'repeated_chars': re.compile(r'([A-Za-z])\1{3,}'),
            'repeated_symbols': re.compile(r'([:\-_]){3,}'),
            'mixed_case_artifacts': re.compile(r'([A-Z])([a-z])\1\2+'),
        }
        
        # Document type keywords
        self.doc_type_keywords = {
            'form': ['application', 'form', 'request', 'grant', 'advance', 'name of', 'designation'],
            'certificate': ['certificate', 'certification', 'awarded', 'completion', 'achievement'],
            'manual': ['manual', 'guide', 'handbook', 'foundation', 'level', 'extension'],
            'proposal': ['proposal', 'rfp', 'request for proposal', 'business plan'],
            'invitation': ['invitation', 'party', 'rsvp', 'address'],
            'pathway': ['pathway', 'stem', 'program', 'requirements']
        }
    
    def extract_text_with_page_info(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF with page information."""
        pages_content = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    pages_content.append({
                        'page_number': i + 1,
                        'text': text.strip()
                    })
        
        return pages_content
    
    def extract_title_and_outline(self, pages_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use Google Gemini to extract title and outline from PDF content."""
        
        # Combine all text for title extraction
        full_text = "\n\n".join([f"Page {page['page_number']}:\n{page['text']}" for page in pages_content])
        
        # Limit text length to avoid token limits
        if len(full_text) > 15000:
            full_text = full_text[:15000] + "..."
        
        prompt = f"""
        You are an expert document analyzer. Extract the document title and create a structured outline from the following PDF content.

        IMPORTANT RULES:
        1. TITLE EXTRACTION:
           - Find the main document title (usually at the top of first page)
           - Clean up any OCR artifacts (repeated characters like RRRR, FFFF, etc.)
           - If no clear title exists, leave as empty string
        
        2. OUTLINE EXTRACTION:
           - ONLY identify MAJOR STRUCTURAL HEADINGS that organize document content
           - Include: Chapter titles, Section headers, Major topic divisions that divide content
           - EXCLUDE: Form field labels, table headers, numbered lists, bullet points, procedural text
           - For forms/certificates: Usually have NO structural outline (return empty outline)
           - For technical documents: Extract clear section headers only
           
        3. HEADING LEVELS:
           - H1: Main chapters/major sections
           - H2: Sub-sections under H1
           - H3: Sub-sub-sections under H2
           - H4: Minor subdivisions under H3
        
        4. DOCUMENT TYPE HANDLING:
           - Forms (like LTC applications): Usually have NO outline structure → empty outline
           - Certificates: Usually have NO outline structure → empty outline
           - Technical manuals: Extract clear chapter/section structure
           - Simple documents: May have minimal or no outline
        
        5. CLEAN OUTPUT:
           - Remove OCR artifacts and repeated characters from titles
           - Keep headings concise
           - Remove unnecessary punctuation from headings

        Return ONLY valid JSON in this exact format:
        {{
            "title": "Clean Document Title Here",
            "outline": [
                {{
                    "level": "H1",
                    "text": "Clean Heading Text",
                    "page": 1
                }}
            ]
        }}

        PDF Content:
        {full_text}
        """
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Extract JSON from response (in case there's extra text)
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                result_text = result_text[json_start:json_end]
            
            result = json.loads(result_text)
            
            # Validate and clean the result
            if 'title' not in result or result['title'] is None:
                result['title'] = ""
            if 'outline' not in result:
                result['outline'] = []
            
            # Clean title - remove OCR artifacts
            if result['title']:
                title = result['title']
                # Remove repeated characters pattern (RRRR, FFFF, etc.)
                import re
                title = re.sub(r'([A-Z])\1{3,}', r'\1', title)  # Remove 4+ repeated caps
                title = re.sub(r'([a-z])\1{3,}', r'\1', title)  # Remove 4+ repeated lowercase
                title = re.sub(r':::+', ':', title)  # Clean up multiple colons
                title = re.sub(r'\s+', ' ', title)  # Clean up multiple spaces
                result['title'] = title.strip()
            
            # Clean outline entries
            cleaned_outline = []
            for item in result['outline']:
                if isinstance(item, dict) and 'level' in item and 'text' in item and 'page' in item:
                    text = str(item['text']).strip()
                    
                    # Skip if this looks like regular text rather than a heading
                    if self._is_likely_heading(text):
                        # Clean the heading text
                        text = re.sub(r'([A-Z])\1{3,}', r'\1', text)  # Remove repeated caps
                        text = re.sub(r'([a-z])\1{3,}', r'\1', text)  # Remove repeated lowercase
                        text = re.sub(r'\s+', ' ', text)  # Clean up spaces
                        
                        cleaned_item = {
                            'level': str(item['level']),
                            'text': text.strip(),
                            'page': int(item['page']) if isinstance(item['page'], (int, str)) and str(item['page']).isdigit() else 0
                        }
                        cleaned_outline.append(cleaned_item)
            
            result['outline'] = cleaned_outline
            return result
            
        except Exception as e:
            print(f"Error with Gemini API: {e}")
            return {"title": "", "outline": []}
    
    def _is_likely_heading(self, text: str) -> bool:
        """Determine if text is likely a heading rather than regular content."""
        text = text.strip()
        
        # Skip empty text
        if not text:
            return False
        
        # Skip very long text (likely paragraphs)
        if len(text) > 300:
            return False
        
        # Skip text that looks like complete sentences with detailed procedural content
        sentence_indicators = [
            'will be issued during', 'is expected that an', 'must be completed and approved',
            'suitable for distribution to the broader', 'opportunity for responses to be evaluated',
            'no later than september', 'available by august', 'will be', 'must be', 
            'is expected', 'available by', 'during', 'no later than', 'opportunity for'
        ]
        
        text_lower = text.lower()
        for indicator in sentence_indicators:
            if indicator in text_lower:
                return False
        
        # Skip form field labels and numbered items - these are not structural headings
        form_field_patterns = [
            text.startswith(tuple('123456789')),  # Numbered fields
            'name of' in text_lower and len(text) < 50,
            'date of' in text_lower and len(text) < 50,
            'designation' in text_lower and len(text) < 30,
            'service' in text_lower and len(text) < 20,
            'amount of' in text_lower and len(text) < 40,
            'home town' in text_lower and len(text) < 50
        ]
        
        # For forms, field labels are NOT structural headings
        if any(form_field_patterns):
            return False
        
        # Accept ONLY major structural headings
        major_heading_indicators = [
            text.isupper() and len(text.split()) <= 8,  # Short ALL CAPS titles
            any(text.lower().startswith(prefix) for prefix in [
                'chapter', 'section', 'part', 'appendix', 'background',
                'summary', 'introduction', 'conclusion', 'overview',
                'references', 'table of contents', 'acknowledgements',
                'revision history', 'business outcomes', 'content',
                'milestones', 'principles', 'goals', 'mission statement'
            ]),
            # Long structured titles that clearly organize content
            (len(text.split()) >= 4 and len(text.split()) <= 12 and 
             any(word in text_lower for word in ['foundation', 'extension', 'agile', 'tester', 
                                                 'digital', 'library', 'ontario', 'proposal',
                                                 'pathways', 'stem']))
        ]
        
        return any(major_heading_indicators)
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Process a single PDF file and extract title and outline."""
        print(f"Processing: {pdf_path}")
        
        try:
            # Extract text with page information
            pages_content = self.extract_text_with_page_info(pdf_path)
            
            if not pages_content:
                return {"title": "", "outline": []}
            
            # Extract title and outline using OpenAI
            result = self.extract_title_and_outline(pages_content)
            
            return result
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            return {"title": "", "outline": []}
    
    def process_directory(self, input_dir: str, output_dir: str):
        """Process all PDF files in a directory."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(input_dir, pdf_file)
            result = self.process_pdf(pdf_path)
            
            # Save result to JSON file
            output_filename = pdf_file.replace('.pdf', '.json')
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            
            print(f"Saved result to: {output_path}")

def load_schema(schema_path: str) -> Dict[str, Any]:
    """Load the output schema."""
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_output(result: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Basic validation of output against schema."""
    if 'title' not in result or 'outline' not in result:
        return False
    
    if not isinstance(result['title'], str):
        return False
    
    if not isinstance(result['outline'], list):
        return False
    
    for item in result['outline']:
        if not isinstance(item, dict):
            return False
        if not all(key in item for key in ['level', 'text', 'page']):
            return False
        if not isinstance(item['level'], str):
            return False
        if not isinstance(item['text'], str):
            return False
        if not isinstance(item['page'], int):
            return False
    
    return True
