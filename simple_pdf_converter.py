#!/usr/bin/env python3
"""
Simple PDF converter for markdown documentation
"""

from fpdf import FPDF
import re

def clean_text(text):
    """Clean text by replacing problematic Unicode characters"""
    replacements = {
        '•': '*',
        '≥': '>=',
        '≤': '<=',
        '→': '->',
        '—': '--',
        '–': '-',
        '“': '"',
        '”': '"',
        '‘': "'",
        '’': "'"
    }
    
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    
    return text

def convert_markdown_to_pdf(markdown_file, pdf_file):
    """Convert markdown file to PDF"""
    
    # Read markdown content
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Clean content of problematic Unicode characters
    content = clean_text(content)
    
    # Create PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Set font for main content
    pdf.set_font('Arial', '', 12)
    
    # Add title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Boarding House Management System', 0, 1, 'C')
    pdf.cell(0, 10, 'Monthly Cycle Documentation', 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    
    # Process content line by line
    lines = content.split('\n')
    
    for line in lines:
        line = clean_text(line.strip())
        
        if not line:
            pdf.ln(6)
            continue
            
        # Handle headings
        if line.startswith('# '):
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, line[2:], 0, 1)
            pdf.ln(5)
            pdf.set_font('Arial', '', 12)
        
        elif line.startswith('## '):
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 8, line[3:], 0, 1)
            pdf.ln(3)
            pdf.set_font('Arial', '', 12)
        
        elif line.startswith('### '):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, line[4:], 0, 1)
            pdf.ln(2)
            pdf.set_font('Arial', '', 12)
        
        # Handle code blocks (simple approach)
        elif line.startswith('```'):
            pdf.set_font('Courier', '', 10)
        
        # Handle lists
        elif line.startswith('- '):
            pdf.cell(10)
            pdf.multi_cell(0, 6, '* ' + line[2:])
        
        elif line.startswith('1. '):
            pdf.cell(10)
            pdf.multi_cell(0, 6, line)
        
        # Handle regular text
        else:
            # Simple line wrapping
            if len(line) > 100:
                # Basic word wrapping
                words = line.split()
                current_line = []
                
                for word in words:
                    current_line.append(word)
                    test_line = ' '.join(current_line)
                    
                    if len(test_line) > 100:
                        if len(current_line) > 1:
                            # Print all but the last word
                            pdf.multi_cell(0, 6, ' '.join(current_line[:-1]))
                            current_line = [current_line[-1]]
                        else:
                            # Single long word, just print it
                            pdf.multi_cell(0, 6, test_line)
                            current_line = []
                
                if current_line:
                    pdf.multi_cell(0, 6, ' '.join(current_line))
            else:
                pdf.multi_cell(0, 6, line)
    
    # Save PDF
    pdf.output(pdf_file)
    print(f"PDF created successfully: {pdf_file}")

if __name__ == "__main__":
    convert_markdown_to_pdf(
        "MONTHLY_CYCLE_DOCUMENTATION.md",
        "Monthly_Cycle_Documentation.pdf"
    )