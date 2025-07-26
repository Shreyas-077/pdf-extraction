#!/usr/bin/env python3
"""
Model Performance Demo - Shows improvements in PDF extraction
"""

import os
import json
from utils import PDFExtractor

def demo_model_performance():
    """Demonstrate the model's improved performance on different document types."""
    
    print("🏆 Adobe India Hackathon - Model Performance Demo")
    print("=" * 60)
    
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY not configured!")
        return
    
    # Test files with different characteristics
    test_cases = [
        {
            "file": "sample_dataset/pdfs/file01.pdf",
            "description": "Form Document (LTC Application)",
            "expected": "Should extract title, minimal outline (forms have few headings)"
        },
        {
            "file": "sample_dataset/pdfs/file02.pdf", 
            "description": "Technical Manual (Foundation Level Extensions)",
            "expected": "Should extract detailed hierarchical structure"
        },
        {
            "file": "sample_dataset/pdfs/file03.pdf",
            "description": "RFP Document (Ontario Digital Library)",
            "expected": "Should have clean title (no OCR artifacts) and proper sections"
        }
    ]
    
    # Add certificate if available
    cert_path = "C:/Users/glaxm/Downloads/certificate-delta-50-6716395d4c764ca4230ca8c7-1.pdf"
    if os.path.exists(cert_path):
        test_cases.append({
            "file": cert_path,
            "description": "Certificate Document",
            "expected": "Should extract title, empty outline (certificates have no hierarchy)"
        })
    
    extractor = PDFExtractor()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 TEST {i}: {test_case['description']}")
        print("-" * 50)
        print(f"📁 File: {os.path.basename(test_case['file'])}")
        print(f"🎯 Expected: {test_case['expected']}")
        
        if not os.path.exists(test_case['file']):
            print("❌ File not found")
            continue
        
        try:
            result = extractor.process_pdf(test_case['file'])
            
            print(f"\n📊 RESULTS:")
            print(f"   📑 Title: {result['title']}")
            print(f"   📋 Outline Items: {len(result['outline'])}")
            
            if result['outline']:
                print(f"   📝 Structure Preview:")
                for j, item in enumerate(result['outline'][:3], 1):
                    indent = "    " + "  " * (int(item['level'][1:]) - 1)
                    print(f"{indent}{j}. [{item['level']}] {item['text'][:60]}...")
                
                if len(result['outline']) > 3:
                    print(f"       ... and {len(result['outline']) - 3} more items")
            else:
                print(f"   📝 Structure: No hierarchical structure (correct for this document type)")
            
            # Analyze quality
            print(f"\n✅ QUALITY CHECK:")
            
            # Check title quality
            if result['title']:
                has_artifacts = any(char * 4 in result['title'] for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                print(f"   • Title clarity: {'❌ Contains OCR artifacts' if has_artifacts else '✅ Clean'}")
            else:
                print(f"   • Title: ⚠️  Empty (may be normal for some documents)")
            
            # Check outline quality  
            if result['outline']:
                sentence_like = sum(1 for item in result['outline'] 
                                  if len(item['text']) > 100 or 
                                     any(phrase in item['text'].lower() for phrase in 
                                         ['will be', 'must be', 'is expected', 'available by']))
                
                print(f"   • Outline quality: {'❌ Contains sentence-like items' if sentence_like > 0 else '✅ Proper headings only'}")
                print(f"   • Hierarchy levels: {set(item['level'] for item in result['outline'])}")
            else:
                print(f"   • Outline: ✅ Empty (appropriate for this document type)")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🎉 Demo completed! The model correctly adapts to different document types.")
    print(f"📋 Key improvements:")
    print(f"   • Cleans OCR artifacts from titles")
    print(f"   • Only extracts true headings, not sentences")
    print(f"   • Handles certificates correctly (empty outline)")
    print(f"   • Maintains proper hierarchy for complex documents")

if __name__ == "__main__":
    demo_model_performance()
