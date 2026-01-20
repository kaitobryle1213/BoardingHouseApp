#!/usr/bin/env python3
"""
Convert Tagalog documentation to PDF format
"""

from fpdf import FPDF
import re

def clean_tagalog_text(text):
    """Clean Tagalog text for PDF encoding"""
    # Remove all emojis and special Unicode characters
    replacements = {
        '•': '*', '≥': '>=', '≤': '<=', '→': '->', '—': '--',
        '–': '-', '“': '"', '”': '"', '‘': "'", '’': "'",
        '❓': '[TANONG]', '✅': '[CHECK]', '❌': '[X]',
        '🟢': '[BERDE]', '🔴': '[PULA]', '🟡': '[DILAW]',
        '⚫': '[ITIM]', '⚪': '[PUTI]', '🏠': '[BAHAY]',
        '📅': '[KALENDARYO]', '📊': '[REPORT]', '🛠️': '[TOOLS]',
        '📈': '[GRAPH]', '📱': '[MOBILE]', '🆘': '[HELP]',
        '💡': '[IDEA]', '💻': '[COMPUTER]', '🔧': '[WRENCH]',
        '🔄': '[REFRESH]', '📋': '[LIST]', '🎯': '[TARGET]',
        '📝': '[NOTE]', '🔍': '[SEARCH]', '📂': '[FOLDER]',
        '🔔': '[BELL]', '💰': '[MONEY]', '👥': '[PEOPLE]',
        '⏰': '[CLOCK]', '📞': '[PHONE]', '📧': '[EMAIL]',
        '🌐': '[WEB]', '🔒': '[LOCK]', '🔓': '[UNLOCK]',
        '📎': '[CLIP]', '📄': '[DOCUMENT]', '📁': '[FILE]',
        '📊': '[CHART]', '📈': '[TREND]', '📉': '[DOWN]',
        '🔴': '[RED]', '🟠': '[ORANGE]', '🟡': '[YELLOW]',
        '🟢': '[GREEN]', '🔵': '[BLUE]', '🟣': '[PURPLE]',
        '🟤': '[BROWN]', '⚫': '[BLACK]', '⚪': '[WHITE]',
        '🔶': '[DIAMOND]', '🔷': '[BLUE_DIAMOND]', '🔸': '[SMALL_ORANGE]',
        '🔹': '[SMALL_BLUE]', '🔺': '[RED_TRIANGLE]', '🔻': '[RED_TRIANGLE_DOWN]',
        '💬': '[SPEECH]', '📢': '[ANNOUNCE]', '📣': '[MEGAPHONE]',
        '📯': '[HORN]', '🔕': '[NO_BELL]', '🛑': '[STOP]',
        '⛔': '[NO_ENTRY]', '🚫': '[PROHIBITED]', '💯': '[100]',
        '✔️': '[OK]', '➕': '[PLUS]', '➖': '[MINUS]', '➗': '[DIVIDE]',
        '✖️': '[MULTIPLY]', '❓': '[QUESTION]', '❔': '[WHITE_QUESTION]',
        '❕': '[WHITE_EXCLAMATION]', '❗': '[EXCLAMATION]', '〰️': '[WAVY]',
        '➰': '[CURLY_LOOP]', '➿': '[DOUBLE_LOOP]', '🔚': '[END]',
        '🔙': '[BACK]', '🔛': '[ON]', '🔝': '[TOP]', '🔜': '[SOON]'
    }
    
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    
    # Remove any remaining Unicode characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return text

def convert_tagalog_to_pdf(markdown_file, pdf_file):
    """Convert Tagalog markdown to PDF"""
    
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = clean_tagalog_text(content)
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Set font for Tagalog text
    pdf.add_font('Arial', '', 'C:\\Windows\\Fonts\\arial.ttf', uni=True)
    pdf.set_font('Arial', '', 12)
    
    # Process content
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            pdf.ln(5)
            continue
            
        # Handle headers
        if line.startswith('# '):
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, line[2:], 0, 1, 'C')
            pdf.ln(5)
            pdf.set_font('Arial', '', 12)
        
        elif line.startswith('## '):
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, line[3:], 0, 1)
            pdf.ln(3)
            pdf.set_font('Arial', '', 12)
        
        elif line.startswith('### '):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, line[4:], 0, 1)
            pdf.ln(2)
            pdf.set_font('Arial', '', 12)
        
        # Handle bullet points
        elif line.startswith('- '):
            pdf.set_font('Arial', '', 11)
            pdf.multi_cell(0, 6, '* ' + line[2:], 0, 'L')
            pdf.set_font('Arial', '', 12)
        
        # Handle numbered lists
        elif re.match(r'^\d+\. ', line):
            pdf.set_font('Arial', '', 11)
            pdf.multi_cell(0, 6, line, 0, 'L')
            pdf.set_font('Arial', '', 12)
        
        # Handle code blocks
        elif line.startswith('```'):
            pdf.set_font('Courier', '', 10)
            pdf.set_fill_color(240, 240, 240)
        
        # Regular text
        else:
            # Handle long text with word wrap
            if len(line) > 80:
                pdf.set_font('Arial', '', 11)
                pdf.multi_cell(0, 6, line, 0, 'L')
                pdf.set_font('Arial', '', 12)
            else:
                pdf.cell(0, 6, line, 0, 1)
    
    pdf.output(pdf_file)
    print(f"Tagalog documentation converted to {pdf_file}")

if __name__ == "__main__":
    convert_tagalog_to_pdf('MONTHLY_CYCLE_TAGALOG.md', 'MONTHLY_CYCLE_TAGALOG.pdf')