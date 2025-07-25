# Adobe India Hackathon - PDF Extraction Challenge

This project extracts structured information from PDF documents, specifically:
- Document title
- Hierarchical outline with heading levels (H1, H2, H3, H4) and page numbers

## 🚀 Multiple Ways to Use

### 1. Interactive Mode (Recommended for beginners)
```bash
python process_pdf.py
```
- Follow interactive prompts
- Process single PDFs or entire directories
- User-friendly interface

### 2. Command Line Interface (For advanced users)
```bash
# Process single PDF
python cli_pdf.py "path/to/document.pdf"

# Process with custom output
python cli_pdf.py "document.pdf" --output "results.json" --verbose

# Process entire directory
python cli_pdf.py "pdf_folder/" --output "output_folder/"

# With validation
python cli_pdf.py "document.pdf" --validate --verbose
```

### 3. Drag and Drop (Windows users)
```bash
python drag_drop_pdf.py
```
- Drag PDF files onto the script
- Or run and enter file paths
- Results saved in same directory as PDF

### 4. Batch Processing (Original method)
```bash
python main.py
```
- Processes sample dataset PDFs
- Good for testing the setup

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Google Gemini API Key**
   - Copy `.env.example` to `.env`
   - Replace `your_gemini_api_key_here` with your actual Google Gemini API key
   - Get an API key from: https://makersuite.google.com/app/apikey

3. **Run the Model**
   ```bash
   # Interactive mode (recommended)
   python process_pdf.py
   
   # Command line mode
   python cli_pdf.py "your_document.pdf"
   
   # Drag and drop mode
   python drag_drop_pdf.py
   
   # Original batch mode
   python main.py
   ```

## Project Structure

```
pdf-extract/
├── main.py                          # Main execution script
├── utils.py                         # PDF processing utilities
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── sample_dataset/
│   ├── pdfs/                       # Input PDF files
│   ├── outputs/                    # Generated JSON outputs
│   └── schema/
│       └── output_schema.json      # Output format schema
└── Adobe_India_Hackathon_-_Challenge_Doc.pdf
```

## How It Works

1. **PDF Text Extraction**: Uses `pdfplumber` to extract text from PDF pages
2. **AI Processing**: Leverages Google Gemini Pro to intelligently identify:
   - Document titles
   - Heading hierarchy (H1, H2, H3, H4)
   - Page numbers for each heading
3. **JSON Output**: Generates structured JSON files matching the required schema

## Output Format

Each processed PDF generates a JSON file with this structure:

```json
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
```

## Features

- ✅ Extracts document titles
- ✅ Identifies hierarchical headings (H1-H4)
- ✅ Tracks page numbers
- ✅ Handles various PDF formats
- ✅ Validates output against schema
- ✅ Batch processing of multiple PDFs
- ✅ Error handling and logging

## Dependencies

- `PyPDF2`: PDF text extraction
- `pdfplumber`: Enhanced PDF processing
- `google-generativeai`: Google Gemini integration for intelligent extraction
- `python-dotenv`: Environment variable management
- `pandas`: Data manipulation (if needed)

## Notes

- Ensure your Google Gemini API key is valid and has sufficient quota
- The model uses Gemini Pro for best accuracy in structure recognition
- Processing time depends on PDF size and complexity
- Output files are saved in UTF-8 encoding with proper JSON formatting
