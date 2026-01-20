#!/usr/bin/env python3
"""
Convert markdown documentation to PDF format using fpdf2 library
"""

from fpdf import FPDF
import re

class PDF(FPDF):
    def header(self):
        # Add header to each page
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Boarding House Management System - Monthly Cycle Documentation', 0, 1, 'C')
        self.line(10, 20, 200, 20)
        self.ln(10)

    def footer(self):
        # Add footer to each page
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def convert_markdown_to_pdf(markdown_file, pdf_file):
    """Convert markdown file to PDF"""
    
    # Read markdown content
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create PDF
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Set font for main content
    pdf.set_font('Arial', '', 12)
    
    # Process markdown content
    lines = content.split('\n')
    
    for line in lines:
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
        
        # Handle code blocks
        elif line.startswith('```'):
            pdf.set_font('Courier', '', 10)
        
        # Handle lists
        elif line.startswith('- '):
            pdf.cell(10)  # Indent
            pdf.multi_cell(0, 6, '* ' + line[2:])
        
        elif line.startswith('1. '):
            pdf.cell(10)  # Indent
            pdf.multi_cell(0, 6, line)
        
        # Handle regular text
        elif line.strip():
            # Handle long lines by splitting into multiple lines
            if len(line) > 100:
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line + ' ' + word) < 100:
                        current_line += ' ' + word if current_line else word
                    else:
                        pdf.multi_cell(0, 6, current_line)
                        current_line = word
                if current_line:
                    pdf.multi_cell(0, 6, current_line)
            else:
                pdf.multi_cell(0, 6, line)
        
        # Empty line for spacing
        else:
            pdf.ln(6)
    
    # Save PDF
    pdf.output(pdf_file)
    print(f"PDF created successfully: {pdf_file}")

if __name__ == "__main__":
    # Convert the documentation
    convert_markdown_to_pdf(
        "MONTHLY_CYCLE_DOCUMENTATION.md",
        "Monthly_Cycle_Documentation.pdf"
    )