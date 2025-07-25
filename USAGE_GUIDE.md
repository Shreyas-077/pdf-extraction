# 🏆 Adobe India Hackathon - PDF Extraction Usage Guide

## Quick Start - Choose Your Method

### Method 1: Interactive Mode (Recommended for beginners) 🎯

```bash
python process_pdf.py
```

**What you get:**
- Friendly menu-driven interface
- Step-by-step guidance
- Options to process single files, directories, or samples
- Automatic output path generation
- Built-in validation

**Perfect for:**
- First-time users
- Non-technical users
- When you want guided experience

---

### Method 2: Command Line Interface (For power users) ⚡

```bash
# Basic usage
python cli_pdf.py "path/to/your/document.pdf"

# Advanced usage
python cli_pdf.py "document.pdf" --output "custom_results.json" --verbose --validate

# Process entire directory
python cli_pdf.py "C:/Documents/PDFs/" --output "C:/Results/" --verbose
```

**Command Line Options:**
- `-o, --output`: Custom output path
- `-v, --verbose`: Detailed output
- `--validate`: Validate against schema
- `--schema`: Custom schema file path

**Perfect for:**
- Advanced users
- Automation and scripting
- Batch processing
- Integration with other tools

---

### Method 3: Drag and Drop (Windows users) 🖱️

```bash
python drag_drop_pdf.py
```

**How to use:**
1. Run the script
2. Drag PDF files onto the command window
3. Or enter file paths when prompted
4. Results saved automatically in same directory

**Perfect for:**
- Windows users
- Quick one-off processing
- Non-technical users who prefer GUI-like experience

---

### Method 4: Original Batch Mode (For samples) 📚

```bash
python main.py
```

**What it does:**
- Processes all PDFs in `sample_dataset/pdfs/`
- Saves results to `sample_dataset/outputs/`
- Validates against provided schema

**Perfect for:**
- Testing the setup
- Processing the provided sample dataset
- Demonstration purposes

---

## Real-World Examples

### Example 1: Process Your Research Paper
```bash
python cli_pdf.py "C:/Documents/my_research_paper.pdf" --verbose
```

### Example 2: Process All Company Reports
```bash
python cli_pdf.py "C:/Reports/2024/" --output "C:/Extracted/" --validate
```

### Example 3: Interactive Processing with Custom Output
```bash
python process_pdf.py
# Choose option 1 (single file)
# Enter: C:/Important/contract.pdf
# Choose custom output location
```

### Example 4: Quick Drag and Drop
```bash
python drag_drop_pdf.py
# Drag your PDF file onto the console window
```

---

## Output Format

All methods produce the same JSON format:

```json
{
    "title": "Your Document Title",
    "outline": [
        {
            "level": "H1",
            "text": "Main Chapter Title",
            "page": 1
        },
        {
            "level": "H2",
            "text": "Section Title",
            "page": 3
        },
        {
            "level": "H3",
            "text": "Subsection Title",
            "page": 5
        }
    ]
}
```

## File Organization Tips

### For Single PDFs:
- Results saved as `{filename}_extraction.json` in same directory
- Example: `contract.pdf` → `contract_extraction.json`

### For Directories:
- Creates `pdf_extraction_outputs/` folder
- Each PDF gets its own JSON file
- Maintains original PDF filenames

### Custom Output:
- Specify exactly where you want results
- Use absolute paths for clarity
- Directory will be created if it doesn't exist

---

## Troubleshooting

### Common Issues:

1. **"GEMINI_API_KEY not found"**
   - Make sure `.env` file exists
   - Check API key is correctly set
   - Restart script after adding key

2. **"File not found"**
   - Use full file paths
   - Check spelling and file extension
   - Ensure PDF file exists

3. **"No PDF files found"**
   - Check directory contains .pdf files
   - Case-sensitive on some systems
   - Try absolute paths

4. **"Schema validation failed"**
   - Output structure issue (usually auto-fixed)
   - Check if custom schema file exists
   - Use `--verbose` for more details

### Getting Help:

```bash
# Command line help
python cli_pdf.py --help

# Test your setup
python test.py

# Verify installation
python setup.py
```

---

## Pro Tips 💡

1. **Use Interactive Mode First**: Get familiar with the tool before using CLI
2. **Test with Sample**: Try `python main.py` to test your setup
3. **Use Verbose Mode**: Add `--verbose` to see what's happening
4. **Validate Important Results**: Use `--validate` for critical documents
5. **Organize Your Outputs**: Create dedicated folders for extraction results
6. **Process in Batches**: Use directory processing for multiple PDFs

---

## Integration Examples

### Windows Batch Script:
```batch
@echo off
python cli_pdf.py "%1" --verbose --validate
pause
```

### PowerShell Script:
```powershell
param($PdfPath)
python cli_pdf.py $PdfPath --output "extractions/" --verbose
```

### Python Integration:
```python
from utils import PDFExtractor
extractor = PDFExtractor()
result = extractor.process_pdf("document.pdf")
print(f"Title: {result['title']}")
```

Happy PDF extracting! 🎉
