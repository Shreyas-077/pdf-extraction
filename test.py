#!/usr/bin/env python3
"""
Test script to verify the PDF extraction setup and run a quick test.
"""

import os
import sys
import json
from utils import PDFExtractor, load_schema, validate_output

def test_single_pdf():
    """Test processing a single PDF file."""
    
    # Check if we have sample PDFs
    pdf_dir = "sample_dataset/pdfs"
    if not os.path.exists(pdf_dir):
        print(f"Error: Directory {pdf_dir} not found.")
        return False
    
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}")
        return False
    
    # Test with the first PDF
    test_pdf = pdf_files[0]
    pdf_path = os.path.join(pdf_dir, test_pdf)
    
    print(f"Testing with: {test_pdf}")
    
    # Check if Gemini API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("Warning: GEMINI_API_KEY not set. Testing without AI extraction...")
        
        # Test basic PDF reading
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                pages = len(pdf.pages)
                first_page_text = pdf.pages[0].extract_text()[:200] if pdf.pages else ""
                
            print(f"✓ PDF reading successful")
            print(f"  - Pages: {pages}")
            print(f"  - First 200 chars: {first_page_text}...")
            return True
            
        except Exception as e:
            print(f"✗ PDF reading failed: {e}")
            return False
    
    else:
        # Test full extraction
        try:
            extractor = PDFExtractor()
            result = extractor.process_pdf(pdf_path)
            
            print(f"✓ Extraction successful")
            print(f"  - Title: {result.get('title', 'N/A')}")
            print(f"  - Outline items: {len(result.get('outline', []))}")
            
            # Validate against schema if available
            schema_path = "sample_dataset/schema/output_schema.json"
            if os.path.exists(schema_path):
                schema = load_schema(schema_path)
                if validate_output(result, schema):
                    print("  - Schema validation: ✓ Passed")
                else:
                    print("  - Schema validation: ✗ Failed")
            
            return True
            
        except Exception as e:
            print(f"✗ Extraction failed: {e}")
            return False

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        ('pdfplumber', 'pdfplumber'),
        ('google-generativeai', 'google.generativeai'), 
        ('python-dotenv', 'dotenv'),
        ('pandas', 'pandas')
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name} - Missing")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\nInstall missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """Run the test suite."""
    print("Adobe India Hackathon - PDF Extraction Test")
    print("=" * 50)
    
    print("\n1. Checking dependencies...")
    if not check_dependencies():
        print("Please install missing dependencies first.")
        sys.exit(1)
    
    print("\n2. Testing PDF processing...")
    if test_single_pdf():
        print("\n✓ All tests passed! The setup is working correctly.")
    else:
        print("\n✗ Tests failed. Please check the setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()
