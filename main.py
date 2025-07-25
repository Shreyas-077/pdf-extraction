#!/usr/bin/env python3
"""
Adobe India Hackathon - PDF Title and Outline Extraction

This script processes PDF files and extracts:
1. Document title
2. Structured outline with heading levels (H1, H2, H3, H4) and page numbers

Usage:
    python main.py

Make sure to set your OPENAI_API_KEY in a .env file or environment variable.
"""

import os
import sys
from utils import PDFExtractor, load_schema, validate_output

def main():
    """Main function to process PDF files."""
    
    # Check if Gemini API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("Error: GEMINI_API_KEY not found in environment variables.")
        print("Please create a .env file with your Google Gemini API key:")
        print("GEMINI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Define paths
    input_dir = "sample_dataset/pdfs"
    output_dir = "sample_dataset/outputs"
    schema_path = "sample_dataset/schema/output_schema.json"
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' not found.")
        sys.exit(1)
    
    # Load schema for validation
    try:
        schema = load_schema(schema_path)
        print("Schema loaded successfully.")
    except Exception as e:
        print(f"Warning: Could not load schema from {schema_path}: {e}")
        schema = None
    
    # Initialize PDF extractor
    extractor = PDFExtractor()
    
    # Process all PDFs in the input directory
    print(f"Processing PDFs from: {input_dir}")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    try:
        extractor.process_directory(input_dir, output_dir)
        print("-" * 50)
        print("Processing completed successfully!")
        
        # Validate outputs if schema is available
        if schema:
            print("Validating outputs against schema...")
            output_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
            
            for output_file in output_files:
                output_path = os.path.join(output_dir, output_file)
                try:
                    import json
                    with open(output_path, 'r', encoding='utf-8') as f:
                        result = json.load(f)
                    
                    if validate_output(result, schema):
                        print(f"✓ {output_file} - Valid")
                    else:
                        print(f"✗ {output_file} - Invalid")
                except Exception as e:
                    print(f"✗ {output_file} - Error: {e}")
        
    except Exception as e:
        print(f"Error during processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
