#!/usr/bin/env python3
"""
Command Line PDF Processor - Adobe India Hackathon

Process PDF files from command line with various options.

Usage:
    python cli_pdf.py <input_path> [options]

Examples:
    # Process single PDF
    python cli_pdf.py "path/to/document.pdf"
    
    # Process single PDF with custom output
    python cli_pdf.py "path/to/document.pdf" --output "results.json"
    
    # Process directory of PDFs
    python cli_pdf.py "path/to/pdf_folder" --output "output_folder"
    
    # Process with verbose output
    python cli_pdf.py "document.pdf" --verbose
    
    # Show help
    python cli_pdf.py --help
"""

import os
import sys
import argparse
import json
from pathlib import Path
from utils import PDFExtractor, load_schema, validate_output

def setup_argument_parser():
    """Setup command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Extract title and structured outline from PDF files using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf
  %(prog)s document.pdf --output results.json
  %(prog)s pdf_folder/ --output output_folder/
  %(prog)s document.pdf --verbose --validate
        """
    )
    
    parser.add_argument(
        'input_path',
        help='Path to PDF file or directory containing PDF files'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output path (file for single PDF, directory for multiple PDFs)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate output against schema (if available)'
    )
    
    parser.add_argument(
        '--schema',
        default='sample_dataset/schema/output_schema.json',
        help='Path to JSON schema file for validation'
    )
    
    return parser

def validate_input_path(input_path):
    """Validate and process input path."""
    input_path = os.path.abspath(input_path)
    
    if not os.path.exists(input_path):
        print(f"❌ Error: Input path does not exist: {input_path}")
        return None, None
    
    if os.path.isfile(input_path):
        if not input_path.lower().endswith('.pdf'):
            print(f"❌ Error: File is not a PDF: {input_path}")
            return None, None
        return input_path, 'file'
    
    elif os.path.isdir(input_path):
        pdf_files = [f for f in os.listdir(input_path) if f.lower().endswith('.pdf')]
        if not pdf_files:
            print(f"❌ Error: No PDF files found in directory: {input_path}")
            return None, None
        return input_path, 'directory'
    
    else:
        print(f"❌ Error: Invalid input path: {input_path}")
        return None, None

def generate_output_path(input_path, input_type, custom_output=None):
    """Generate appropriate output path."""
    if custom_output:
        return os.path.abspath(custom_output)
    
    if input_type == 'file':
        # For single file, create JSON file with same name
        input_dir = os.path.dirname(input_path)
        input_name = os.path.splitext(os.path.basename(input_path))[0]
        return os.path.join(input_dir, f"{input_name}_extraction.json")
    
    else:  # directory
        # For directory, create output subdirectory
        return os.path.join(os.path.dirname(input_path), "pdf_extraction_outputs")

def process_single_file(pdf_path, output_path, verbose=False, validate_schema=False, schema_path=None):
    """Process a single PDF file."""
    if verbose:
        print(f"🔍 Processing: {os.path.basename(pdf_path)}")
        print(f"📁 Input: {pdf_path}")
        print(f"💾 Output: {output_path}")
    
    try:
        # Initialize extractor
        extractor = PDFExtractor()
        
        # Process PDF
        result = extractor.process_pdf(pdf_path)
        
        # Create output directory if needed
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Save result
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        
        # Display results
        print(f"✅ Successfully processed: {os.path.basename(pdf_path)}")
        if verbose:
            print(f"   Title: {result['title']}")
            print(f"   Outline items: {len(result['outline'])}")
            print(f"   Saved to: {output_path}")
        
        # Validate if requested
        if validate_schema and schema_path and os.path.exists(schema_path):
            try:
                schema = load_schema(schema_path)
                if validate_output(result, schema):
                    print(f"✅ Schema validation: PASSED")
                else:
                    print(f"❌ Schema validation: FAILED")
            except Exception as e:
                print(f"⚠️  Schema validation error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing {os.path.basename(pdf_path)}: {e}")
        return False

def process_directory(input_dir, output_dir, verbose=False, validate_schema=False, schema_path=None):
    """Process all PDF files in a directory."""
    if verbose:
        print(f"📁 Processing directory: {input_dir}")
        print(f"💾 Output directory: {output_dir}")
    
    try:
        # Initialize extractor
        extractor = PDFExtractor()
        
        # Process all PDFs
        extractor.process_directory(input_dir, output_dir)
        
        print(f"✅ Successfully processed all PDFs in directory")
        if verbose:
            print(f"   Output saved to: {output_dir}")
        
        # Validate if requested
        if validate_schema and schema_path and os.path.exists(schema_path):
            print("🔍 Validating outputs...")
            schema = load_schema(schema_path)
            output_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
            
            valid_count = 0
            for output_file in output_files:
                file_path = os.path.join(output_dir, output_file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        result = json.load(f)
                    
                    if validate_output(result, schema):
                        if verbose:
                            print(f"   ✅ {output_file} - Valid")
                        valid_count += 1
                    else:
                        print(f"   ❌ {output_file} - Invalid")
                except Exception as e:
                    print(f"   ❌ {output_file} - Error: {e}")
            
            print(f"📊 Validation summary: {valid_count}/{len(output_files)} files valid")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing directory: {e}")
        return False

def main():
    """Main command line function."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Validate input path
    input_path, input_type = validate_input_path(args.input_path)
    if not input_path:
        sys.exit(1)
    
    # Generate output path
    output_path = generate_output_path(input_path, input_type, args.output)
    
    # Process based on input type
    if input_type == 'file':
        success = process_single_file(
            input_path, output_path, 
            args.verbose, args.validate, args.schema
        )
    else:  # directory
        success = process_directory(
            input_path, output_path,
            args.verbose, args.validate, args.schema
        )
    
    if success:
        print("🎉 Processing completed successfully!")
    else:
        print("💥 Processing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
