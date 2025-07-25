#!/usr/bin/env python3
"""
Drag and Drop PDF Processor - Adobe India Hackathon

Simple script that processes PDF files dropped onto it.
Works on Windows - users can drag PDF files onto this script.

Usage:
    1. Drag a PDF file onto this script
    2. Or run: python drag_drop_pdf.py path/to/file.pdf
    3. Results will be saved in the same directory as the PDF
"""

import os
import sys
import json
from pathlib import Path
from utils import PDFExtractor, validate_output, load_schema

def process_dropped_file(file_path):
    """Process a PDF file that was dropped onto the script."""
    print("🏆 Adobe India Hackathon - PDF Extractor")
    print("=" * 50)
    
    # Validate file
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        input("Press Enter to exit...")
        return False
    
    if not file_path.lower().endswith('.pdf'):
        print(f"❌ Not a PDF file: {file_path}")
        input("Press Enter to exit...")
        return False
    
    # Generate output path
    input_dir = os.path.dirname(file_path)
    input_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(input_dir, f"{input_name}_extraction.json")
    
    print(f"📄 Processing: {os.path.basename(file_path)}")
    print(f"💾 Output will be saved to: {os.path.basename(output_path)}")
    print()
    
    try:
        # Initialize extractor
        print("🤖 Initializing AI extractor...")
        extractor = PDFExtractor()
        
        # Process PDF
        print("🔍 Extracting content from PDF...")
        result = extractor.process_pdf(file_path)
        
        # Save result
        print("💾 Saving results...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        
        # Display results
        print("\n" + "="*50)
        print("📊 EXTRACTION RESULTS")
        print("="*50)
        print(f"📑 Title: {result['title']}")
        print(f"📋 Outline items: {len(result['outline'])}")
        
        if result['outline']:
            print(f"\n📝 Document Structure:")
            for i, item in enumerate(result['outline'][:10], 1):  # Show first 10 items
                indent = "  " * (int(item['level'][1:]) - 1) if item['level'].startswith('H') else ""
                print(f"   {indent}• {item['text']} (Page {item['page']})")
            
            if len(result['outline']) > 10:
                print(f"   ... and {len(result['outline']) - 10} more items")
        
        print(f"\n✅ Results saved to: {output_path}")
        
        # Validate if schema is available
        schema_path = "sample_dataset/schema/output_schema.json"
        if os.path.exists(schema_path):
            try:
                schema = load_schema(schema_path)
                if validate_output(result, schema):
                    print("✅ Output format validation: PASSED")
                else:
                    print("⚠️  Output format validation: FAILED")
            except:
                pass
        
        print("\n🎉 Processing completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error processing PDF: {e}")
        return False

def main():
    """Main function for drag and drop processing."""
    
    # Check API key
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY not configured!")
        print("Please set up your Google Gemini API key in the .env file first.")
        input("Press Enter to exit...")
        return
    
    # Get file path from command line arguments or user input
    if len(sys.argv) > 1:
        # File was dropped onto script or passed as argument
        file_path = sys.argv[1]
        success = process_dropped_file(file_path)
        
        # Keep console open to show results
        if success:
            print("\n📁 Check the output file in the same directory as your PDF!")
        input("\nPress Enter to exit...")
        
    else:
        # No file provided, ask user for input
        print("🏆 Adobe India Hackathon - PDF Extractor")
        print("=" * 50)
        print("📄 Drag a PDF file onto this script, or enter the path below:")
        print()
        
        while True:
            file_path = input("Enter PDF file path (or 'quit' to exit): ").strip()
            
            if file_path.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            # Remove quotes if user added them
            file_path = file_path.strip('"\'')
            
            if file_path:
                success = process_dropped_file(file_path)
                
                if success:
                    continue_choice = input("\nProcess another PDF? (y/n): ").strip().lower()
                    if continue_choice not in ['y', 'yes']:
                        print("👋 Thank you for using PDF Extractor!")
                        break
                else:
                    retry = input("\nTry another file? (y/n): ").strip().lower()
                    if retry not in ['y', 'yes']:
                        break

if __name__ == "__main__":
    main()
