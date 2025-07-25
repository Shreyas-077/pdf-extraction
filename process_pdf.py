#!/usr/bin/env python3
"""
Interactive PDF Processor - Adobe India Hackathon

This script allows users to process any PDF file by providing the path as input.
It can process single files or entire directories containing PDFs.

Usage:
    python process_pdf.py
    
Then follow the interactive prompts to:
1. Process a single PDF file
2. Process all PDFs in a directory
3. Process sample dataset
"""

import os
import sys
from pathlib import Path
from utils import PDFExtractor, load_schema, validate_output

def get_user_choice():
    """Get user's choice for processing mode."""
    print("🎯 PDF Processing Options:")
    print("1. Process a single PDF file")
    print("2. Process all PDFs in a directory")
    print("3. Process sample dataset")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            return int(choice)
        print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

def get_file_path():
    """Get PDF file path from user."""
    while True:
        file_path = input("\n📁 Enter the path to your PDF file: ").strip()
        
        # Remove quotes if user added them
        file_path = file_path.strip('"\'')
        
        # Convert to absolute path
        file_path = os.path.abspath(file_path)
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue
            
        if not file_path.lower().endswith('.pdf'):
            print(f"❌ File is not a PDF: {file_path}")
            continue
            
        return file_path

def get_directory_path():
    """Get directory path from user."""
    while True:
        dir_path = input("\n📁 Enter the path to directory containing PDFs: ").strip()
        
        # Remove quotes if user added them
        dir_path = dir_path.strip('"\'')
        
        # Convert to absolute path
        dir_path = os.path.abspath(dir_path)
        
        if not os.path.exists(dir_path):
            print(f"❌ Directory not found: {dir_path}")
            continue
            
        if not os.path.isdir(dir_path):
            print(f"❌ Path is not a directory: {dir_path}")
            continue
            
        # Check if directory contains PDF files
        pdf_files = [f for f in os.listdir(dir_path) if f.lower().endswith('.pdf')]
        if not pdf_files:
            print(f"❌ No PDF files found in directory: {dir_path}")
            continue
            
        print(f"✅ Found {len(pdf_files)} PDF file(s) in directory")
        return dir_path

def get_output_path(input_path, is_directory=False):
    """Get output path from user or generate default."""
    if is_directory:
        default_output = os.path.join(os.path.dirname(input_path), "pdf_extraction_outputs")
    else:
        # For single file, create output in same directory
        input_dir = os.path.dirname(input_path)
        input_name = os.path.splitext(os.path.basename(input_path))[0]
        default_output = os.path.join(input_dir, f"{input_name}_extraction.json")
    
    print(f"\n💾 Default output location: {default_output}")
    use_default = input("Use default output location? (y/n) [y]: ").strip().lower()
    
    if use_default in ['', 'y', 'yes']:
        return default_output
    else:
        while True:
            custom_output = input("Enter custom output path: ").strip()
            custom_output = custom_output.strip('"\'')
            custom_output = os.path.abspath(custom_output)
            
            # Create directory if it doesn't exist
            if is_directory:
                try:
                    os.makedirs(custom_output, exist_ok=True)
                    return custom_output
                except Exception as e:
                    print(f"❌ Cannot create directory: {e}")
            else:
                # For single file, ensure directory exists
                output_dir = os.path.dirname(custom_output)
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    return custom_output
                except Exception as e:
                    print(f"❌ Cannot create output directory: {e}")

def process_single_pdf():
    """Process a single PDF file."""
    print("\n" + "="*60)
    print("🔍 SINGLE PDF PROCESSING")
    print("="*60)
    
    # Get input file
    pdf_path = get_file_path()
    
    # Get output path
    output_path = get_output_path(pdf_path, is_directory=False)
    
    # Initialize extractor
    try:
        extractor = PDFExtractor()
    except Exception as e:
        print(f"❌ Error initializing extractor: {e}")
        return
    
    # Process the PDF
    print(f"\n🚀 Processing: {os.path.basename(pdf_path)}")
    print("-" * 50)
    
    try:
        result = extractor.process_pdf(pdf_path)
        
        # Save result
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        
        # Display results
        print(f"\n📊 EXTRACTION RESULTS")
        print("-" * 30)
        print(f"Title: {result['title']}")
        print(f"Outline items: {len(result['outline'])}")
        
        if result['outline']:
            print(f"\nFirst 5 outline items:")
            for i, item in enumerate(result['outline'][:5], 1):
                print(f"  {i}. [{item['level']}] {item['text']} (Page {item['page']})")
            
            if len(result['outline']) > 5:
                print(f"  ... and {len(result['outline']) - 5} more items")
        
        print(f"\n✅ Result saved to: {output_path}")
        
        # Validate against schema if available
        schema_path = "sample_dataset/schema/output_schema.json"
        if os.path.exists(schema_path):
            try:
                schema = load_schema(schema_path)
                if validate_output(result, schema):
                    print("✅ Schema validation: PASSED")
                else:
                    print("⚠️  Schema validation: FAILED")
            except Exception as e:
                print(f"⚠️  Could not validate schema: {e}")
        
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")

def process_directory():
    """Process all PDFs in a directory."""
    print("\n" + "="*60)
    print("📁 DIRECTORY PROCESSING")
    print("="*60)
    
    # Get input directory
    input_dir = get_directory_path()
    
    # Get output directory
    output_dir = get_output_path(input_dir, is_directory=True)
    
    # Initialize extractor
    try:
        extractor = PDFExtractor()
    except Exception as e:
        print(f"❌ Error initializing extractor: {e}")
        return
    
    # Process all PDFs
    print(f"\n🚀 Processing PDFs from: {input_dir}")
    print(f"💾 Output directory: {output_dir}")
    print("-" * 50)
    
    try:
        extractor.process_directory(input_dir, output_dir)
        print(f"\n✅ Batch processing completed!")
        print(f"📁 Check outputs in: {output_dir}")
        
    except Exception as e:
        print(f"❌ Error during batch processing: {e}")

def process_sample_dataset():
    """Process the sample dataset."""
    print("\n" + "="*60)
    print("📚 SAMPLE DATASET PROCESSING")
    print("="*60)
    
    input_dir = "sample_dataset/pdfs"
    output_dir = "sample_dataset/outputs"
    
    if not os.path.exists(input_dir):
        print(f"❌ Sample dataset not found: {input_dir}")
        return
    
    # Initialize extractor
    try:
        extractor = PDFExtractor()
    except Exception as e:
        print(f"❌ Error initializing extractor: {e}")
        return
    
    # Process sample PDFs
    print(f"🚀 Processing sample PDFs...")
    print("-" * 30)
    
    try:
        extractor.process_directory(input_dir, output_dir)
        print(f"\n✅ Sample processing completed!")
        
        # Validate outputs
        schema_path = "sample_dataset/schema/output_schema.json"
        if os.path.exists(schema_path):
            print("\n🔍 Validating outputs...")
            schema = load_schema(schema_path)
            output_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
            
            for output_file in output_files:
                output_path = os.path.join(output_dir, output_file)
                try:
                    import json
                    with open(output_path, 'r', encoding='utf-8') as f:
                        result = json.load(f)
                    
                    if validate_output(result, schema):
                        print(f"✅ {output_file} - Valid")
                    else:
                        print(f"❌ {output_file} - Invalid")
                except Exception as e:
                    print(f"❌ {output_file} - Error: {e}")
        
    except Exception as e:
        print(f"❌ Error processing samples: {e}")

def main():
    """Main interactive function."""
    print("🏆 ADOBE INDIA HACKATHON - PDF EXTRACTION")
    print("=" * 60)
    print("📄 Process any PDF file to extract title and structured outline")
    print("🤖 Powered by Google Gemini AI")
    print()
    
    # Check if API key is configured
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY not found!")
        print("Please configure your API key in the .env file first.")
        return
    
    while True:
        choice = get_user_choice()
        
        if choice == 1:
            process_single_pdf()
        elif choice == 2:
            process_directory()
        elif choice == 3:
            process_sample_dataset()
        elif choice == 4:
            print("\n👋 Thank you for using PDF Extraction tool!")
            break
        
        # Ask if user wants to continue
        print("\n" + "="*60)
        continue_choice = input("Would you like to process another PDF? (y/n) [y]: ").strip().lower()
        if continue_choice in ['n', 'no']:
            print("\n👋 Thank you for using PDF Extraction tool!")
            break
        print()

if __name__ == "__main__":
    main()
