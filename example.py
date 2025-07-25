#!/usr/bin/env python3
"""
Example usage of the PDF extraction model.

This demonstrates how to:
1. Set up the environment
2. Process a single PDF
3. Validate the output

Before running this example, make sure to:
1. Set your OPENAI_API_KEY in a .env file
2. Install the required dependencies: pip install -r requirements.txt
"""

import os
import json
from utils import PDFExtractor, load_schema, validate_output

def example_single_pdf():
    """Example: Process a single PDF file."""
    
    # Initialize the extractor
    extractor = PDFExtractor()
    
    # Process a sample PDF
    pdf_path = "sample_dataset/pdfs/file01.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return
    
    print(f"Processing: {pdf_path}")
    
    # Extract title and outline
    result = extractor.process_pdf(pdf_path)
    
    # Display results
    print("\n" + "="*50)
    print("EXTRACTION RESULTS")
    print("="*50)
    print(f"Title: {result['title']}")
    print(f"Outline items: {len(result['outline'])}")
    
    if result['outline']:
        print("\nOutline:")
        for i, item in enumerate(result['outline'], 1):
            print(f"  {i}. [{item['level']}] {item['text']} (Page {item['page']})")
    
    # Save result
    output_path = "example_output.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    
    print(f"\nResult saved to: {output_path}")
    
    # Validate against schema
    schema_path = "sample_dataset/schema/output_schema.json"
    if os.path.exists(schema_path):
        schema = load_schema(schema_path)
        if validate_output(result, schema):
            print("✓ Output validation: PASSED")
        else:
            print("✗ Output validation: FAILED")

def example_batch_processing():
    """Example: Process all PDFs in a directory."""
    
    extractor = PDFExtractor()
    
    input_dir = "sample_dataset/pdfs"
    output_dir = "example_outputs"
    
    print(f"Processing all PDFs from: {input_dir}")
    print(f"Output directory: {output_dir}")
    
    # Process all PDFs
    extractor.process_directory(input_dir, output_dir)
    
    print("Batch processing completed!")

def main():
    """Main example function."""
    
    print("Adobe India Hackathon - PDF Extraction Example")
    print("=" * 60)
    
    # Check if Gemini API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  GEMINI_API_KEY not found!")
        print("To use AI extraction, create a .env file with:")
        print("GEMINI_API_KEY=your_api_key_here")
        print("\nRunning basic PDF reading test instead...\n")
        
        # Run without AI
        import pdfplumber
        pdf_path = "sample_dataset/pdfs/file01.pdf"
        if os.path.exists(pdf_path):
            with pdfplumber.open(pdf_path) as pdf:
                print(f"✓ Successfully read PDF: {len(pdf.pages)} pages")
                print(f"✓ First page text preview: {pdf.pages[0].extract_text()[:100]}...")
        return
    
    print("🚀 Running with AI extraction...\n")
    
    # Example 1: Single PDF processing
    print("Example 1: Single PDF Processing")
    print("-" * 40)
    example_single_pdf()
    
    print("\n\n")
    
    # Example 2: Batch processing (commented out to avoid overwriting sample outputs)
    # print("Example 2: Batch Processing")
    # print("-" * 40)
    # example_batch_processing()

if __name__ == "__main__":
    main()
