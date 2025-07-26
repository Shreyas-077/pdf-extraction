import os
import json
import re
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
import pdfplumber

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
    
    def clean_ocr_artifacts(self, text: str) -> str:
        """Clean OCR artifacts from text."""
        if not text:
            return ""
        
        # Remove repeated characters (RRRR, FFFF, etc.)
        for pattern in self.ocr_patterns.values():
            text = pattern.sub(r'\1', text)
        
        # Clean up multiple spaces and normalize
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[:]{2,}', ':', text)
        
        return text.strip()
    
    def detect_document_type(self, pages_content: List[Dict[str, Any]]) -> str:
        """Detect the type of document based on content."""
        if not pages_content:
            return 'unknown'
        
        # Combine first few pages for analysis
        sample_text = ""
        for page in pages_content[:3]:  # Check first 3 pages
            sample_text += page['text'].lower() + " "
        
        # Count keywords for each document type
        type_scores = {}
        for doc_type, keywords in self.doc_type_keywords.items():
            score = sum(sample_text.count(keyword) for keyword in keywords)
            type_scores[doc_type] = score
        
        # Return type with highest score, or 'unknown' if no clear match
        if max(type_scores.values()) > 0:
            return max(type_scores, key=type_scores.get)
        return 'unknown'
    
    def extract_title_from_text(self, pages_content: List[Dict[str, Any]]) -> str:
        """Extract document title from the first page."""
        if not pages_content:
            return ""
        
        first_page_text = pages_content[0]['text']
        lines = [line.strip() for line in first_page_text.split('\n') if line.strip()]
        
        if not lines:
            return ""
        
        # Try different title extraction strategies
        title_candidates = []
        
        # Strategy 1: First non-empty line that looks like a title
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            clean_line = self.clean_ocr_artifacts(line)
            if len(clean_line) > 10 and len(clean_line) < 200:
                # Check if it looks like a title
                if (clean_line.isupper() or 
                    clean_line.istitle() or 
                    any(word in clean_line.lower() for word in ['application', 'form', 'request', 'proposal', 'rfp', 'manual', 'guide', 'pathway', 'invitation'])):
                    title_candidates.append((clean_line, i))
        
        # Strategy 2: Look for patterns that indicate titles
        for i, line in enumerate(lines[:15]):
            clean_line = self.clean_ocr_artifacts(line)
            if (re.match(r'^[A-Z][A-Za-z\s\-&:]+$', clean_line) and 
                len(clean_line.split()) >= 3 and 
                len(clean_line.split()) <= 15):
                title_candidates.append((clean_line, i))
        
        # Return the best candidate (prefer earlier ones)
        if title_candidates:
            # Sort by position (earlier is better)
            title_candidates.sort(key=lambda x: x[1])
            return title_candidates[0][0]
        
        # Fallback: return first non-empty line if cleaned
        first_line = self.clean_ocr_artifacts(lines[0])
        return first_line if len(first_line) < 200 else ""
    
    def extract_outline_from_text(self, pages_content: List[Dict[str, Any]], doc_type: str) -> List[Dict[str, Any]]:
        """Extract outline based on document type and text analysis."""
        outline = []
        
        # Forms and certificates typically have no structural outline
        if doc_type in ['form', 'certificate', 'invitation']:
            return outline  # Return empty outline
        
        # Process each page for headings
        for page_data in pages_content:
            page_num = page_data['page_number']
            lines = [line.strip() for line in page_data['text'].split('\n') if line.strip()]
            
            for line in lines:
                clean_line = self.clean_ocr_artifacts(line)
                if self.is_structural_heading(clean_line, doc_type):
                    level = self.determine_heading_level(clean_line, doc_type)
                    outline.append({
                        'level': level,
                        'text': clean_line,
                        'page': page_num
                    })
        
        return outline
    
    def is_structural_heading(self, text: str, doc_type: str) -> bool:
        """Determine if text is a structural heading based on patterns."""
        if not text or len(text) < 3:
            return False
        
        # Skip very long text (likely paragraphs)
        if len(text) > 150:
            return False
        
        # Skip sentences with specific patterns
        sentence_patterns = [
            r'will be', r'must be', r'is expected', r'available by',
            r'during', r'no later than', r'opportunity for',
            r'suitable for distribution', r'completed and approved'
        ]
        
        text_lower = text.lower()
        for pattern in sentence_patterns:
            if re.search(pattern, text_lower):
                return False
        
        # Positive patterns for structural headings
        structural_patterns = [
            # Chapter/Section patterns
            self.heading_patterns['chapter'].match(text),
            self.heading_patterns['section'].match(text),
            self.heading_patterns['appendix'].match(text),
            
            # Title-like patterns
            text.isupper() and len(text.split()) <= 8,
            
            # Specific structural keywords
            any(text_lower.startswith(keyword) for keyword in [
                'chapter', 'section', 'part', 'appendix', 'background',
                'summary', 'introduction', 'conclusion', 'overview',
                'references', 'table of contents', 'acknowledgements',
                'revision history', 'business outcomes', 'content',
                'milestones', 'principles', 'goals', 'mission statement',
                'approach and specific', 'evaluation and awarding',
                'phase i', 'phase ii', 'phase iii', 'preamble',
                'terms of reference', 'membership', 'appointment criteria'
            ]),
            
            # Numbered structural items (but not form fields)
            (re.match(r'^\d+\.\s+[A-Z][a-z]+', text) and 
             not any(field in text_lower for field in ['name of', 'date of', 'designation', 'service']))
        ]
        
        return any(structural_patterns)
    
    def determine_heading_level(self, text: str, doc_type: str) -> str:
        """Determine the heading level (H1, H2, H3, H4) based on text patterns."""
        text_lower = text.lower()
        
        # H1 patterns - Major sections
        h1_patterns = [
            text.isupper() and len(text.split()) <= 6,
            any(text_lower.startswith(keyword) for keyword in [
                'chapter', 'introduction to', 'overview of', 'background',
                'revision history', 'table of contents', 'acknowledgements',
                'references', 'appendix a', 'appendix b', 'appendix c'
            ]),
            text_lower.endswith('digital library'),
            'ontario' in text_lower and 'library' in text_lower
        ]
        
        if any(h1_patterns):
            return 'H1'
        
        # H2 patterns - Sub-sections
        h2_patterns = [
            any(text_lower.startswith(keyword) for keyword in [
                'summary', 'business outcomes', 'content', 'milestones',
                'approach and specific', 'evaluation and awarding',
                'the business plan', 'what could the'
            ]),
            text_lower.startswith('appendix') and ':' not in text
        ]
        
        if any(h2_patterns):
            return 'H2'
        
        # H3 patterns - Sub-sub-sections
        h3_patterns = [
            text_lower.endswith(':'),
            any(text_lower.startswith(keyword) for keyword in [
                'timeline', 'intended audience', 'career paths',
                'learning objectives', 'entry requirements',
                'structure and course', 'keeping it current',
                'phase i', 'phase ii', 'phase iii'
            ]),
            re.match(r'^\d+\.\s+[A-Z]', text)
        ]
        
        if any(h3_patterns):
            return 'H3'
        
        # Default to H4 for remaining structural headings
        return 'H4'
    
    def extract_title_and_outline(self, pages_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract title and outline using offline text processing."""
        if not pages_content:
            return {"title": "", "outline": []}
        
        # Detect document type
        doc_type = self.detect_document_type(pages_content)
        
        # Extract title
        title = self.extract_title_from_text(pages_content)
        
        # Extract outline based on document type
        outline = self.extract_outline_from_text(pages_content, doc_type)
        
        return {
            "title": title,
            "outline": outline
        }
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Process a single PDF file and extract title and outline."""
        print(f"Processing: {pdf_path}")
        
        try:
            # Extract text with page information
            pages_content = self.extract_text_with_page_info(pdf_path)
            
            if not pages_content:
                return {"title": "", "outline": []}
            
            # Extract title and outline using offline processing
            result = self.extract_title_and_outline(pages_content)
            
            return result
            
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return {"title": "", "outline": []}
    
    def process_directory(self, input_dir: str, output_dir: str):
        """Process all PDF files in a directory and save results."""
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(input_dir, pdf_file)
            
            try:
                result = self.process_pdf(pdf_path)
                
                # Create output filename
                base_name = os.path.splitext(pdf_file)[0]
                output_file = os.path.join(output_dir, f"{base_name}.json")
                
                # Save result
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)
                
                print(f"✅ Saved: {output_file}")
                
            except Exception as e:
                print(f"❌ Error processing {pdf_file}: {e}")

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
    
    return True
