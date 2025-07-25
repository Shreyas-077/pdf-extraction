import os
import json
import re
from typing import Dict, List, Any
from dotenv import load_dotenv
import google.generativeai as genai
import pdfplumber
import pandas as pd

# Load environment variables
load_dotenv()

class PDFExtractor:
    def __init__(self):
        """Initialize the PDF extractor with Google Gemini API."""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
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
        Analyze the following PDF content and extract:
        1. The document title (main title of the document)
        2. A structured outline with heading levels and page numbers

        For the outline, identify headings at different levels:
        - H1: Main headings/chapters
        - H2: Sub-headings under H1
        - H3: Sub-headings under H2  
        - H4: Sub-headings under H3

        Look for patterns like:
        - Bold or capitalized text that appears to be headings
        - Numbered sections (1., 2., 1.1, 1.2, etc.)
        - Text that stands alone on lines
        - Chapter titles, section titles, appendices

        Return the result in this exact JSON format:
        {{
            "title": "Document Title Here",
            "outline": [
                {{
                    "level": "H1",
                    "text": "Heading text",
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
            
            # Clean outline entries
            cleaned_outline = []
            for item in result['outline']:
                if isinstance(item, dict) and 'level' in item and 'text' in item and 'page' in item:
                    cleaned_item = {
                        'level': str(item['level']),
                        'text': str(item['text']).strip(),
                        'page': int(item['page']) if isinstance(item['page'], (int, str)) and str(item['page']).isdigit() else 0
                    }
                    cleaned_outline.append(cleaned_item)
            
            result['outline'] = cleaned_outline
            return result
            
        except Exception as e:
            print(f"Error with Gemini API: {e}")
            return {"title": "", "outline": []}
    
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
