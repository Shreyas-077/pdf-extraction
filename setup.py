#!/usr/bin/env python3
"""
Setup verification and quick start guide for the Adobe India Hackathon PDF Extraction Challenge.
"""

import os
import sys

def print_header():
    """Print the header."""
    print("=" * 70)
    print("🏆 ADOBE INDIA HACKATHON - PDF EXTRACTION CHALLENGE")
    print("=" * 70)
    print()

def check_environment():
    """Check if the environment is properly set up."""
    print("🔍 ENVIRONMENT CHECK")
    print("-" * 30)
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"✓ Python {python_version.major}.{python_version.minor}")
    else:
        print(f"✗ Python {python_version.major}.{python_version.minor} (Requires Python 3.8+)")
        return False
    
    # Check required files
    required_files = [
        "main.py",
        "utils.py", 
        "requirements.txt",
        "sample_dataset/pdfs",
        "sample_dataset/schema/output_schema.json"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - Missing")
            return False
    
    # Check dependencies
    try:
        import pdfplumber
        import google.generativeai as genai
        import dotenv
        import pandas
        print("✓ All dependencies installed")
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        return False
    
    # Check API key
    from dotenv import load_dotenv
    load_dotenv()
    
    if os.getenv('GEMINI_API_KEY'):
        print("✓ GEMINI_API_KEY configured")
        api_configured = True
    else:
        print("⚠️  GEMINI_API_KEY not configured")
        api_configured = False
    
    return api_configured

def show_project_structure():
    """Show the project structure."""
    print("\n📁 PROJECT STRUCTURE")
    print("-" * 30)
    
    structure = """
pdf-extract/
├── main.py                 # Main execution script
├── utils.py                # PDF processing utilities  
├── requirements.txt        # Dependencies
├── test.py                 # Test script
├── example.py              # Usage examples
├── README.md               # Documentation
├── .env.example            # Environment template
├── sample_dataset/
│   ├── pdfs/               # Input PDF files (5 files)
│   ├── outputs/            # Reference outputs (5 JSON files)
│   └── schema/
│       └── output_schema.json  # Output format specification
└── Adobe_India_Hackathon_-_Challenge_Doc.pdf
"""
    print(structure)

def show_usage_instructions():
    """Show usage instructions."""
    print("🚀 QUICK START GUIDE")
    print("-" * 30)
    
    print("1. Install Dependencies:")
    print("   pip install -r requirements.txt")
    print()
    
    print("2. Configure Google Gemini API Key:")
    print("   - Copy .env.example to .env")
    print("   - Add your Google Gemini API key to .env")
    print("   - Get API key from: https://makersuite.google.com/app/apikey")
    print()
    
    print("3. Run the Model:")
    print("   python main.py")
    print()
    
    print("4. Test the Setup:")
    print("   python test.py")
    print()
    
    print("5. See Examples:")
    print("   python example.py")
    print()

def show_output_format():
    """Show the expected output format."""
    print("📊 OUTPUT FORMAT")
    print("-" * 30)
    
    example_output = """
{
    "title": "Document Title",
    "outline": [
        {
            "level": "H1",
            "text": "Main Heading",
            "page": 1
        },
        {
            "level": "H2", 
            "text": "Sub Heading",
            "page": 2
        }
    ]
}
"""
    print(example_output)

def show_features():
    """Show the features of the model."""
    print("⭐ MODEL FEATURES")
    print("-" * 30)
    
    features = [
        "✅ Extracts document titles",
        "✅ Identifies hierarchical headings (H1-H4)",
        "✅ Tracks page numbers for each heading",
        "✅ Handles various PDF formats", 
        "✅ Validates output against JSON schema",
        "✅ Batch processing of multiple PDFs",
        "✅ Error handling and logging",
        "✅ Uses GPT-4 for intelligent text understanding"
    ]
    
    for feature in features:
        print(f"  {feature}")
    print()

def main():
    """Main setup function."""
    print_header()
    
    # Check environment
    api_configured = check_environment()
    
    # Show project info
    show_project_structure()
    show_features()
    show_output_format()
    show_usage_instructions()
    
    # Final status
    print("🎯 STATUS")
    print("-" * 30)
    
    if api_configured:
        print("✅ Setup complete! Ready to process PDFs with AI extraction.")
        print("   Run: python main.py")
    else:
        print("⚠️  Setup mostly complete. Configure Google Gemini API key for full functionality.")
        print("   Basic PDF reading works without API key.")
        print("   Run: python test.py")
    
    print()
    print("📚 For more information, see README.md")
    print("=" * 70)

if __name__ == "__main__":
    main()
