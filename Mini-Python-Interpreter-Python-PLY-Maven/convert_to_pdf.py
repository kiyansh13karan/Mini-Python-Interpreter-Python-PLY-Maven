import markdown2
from weasyprint import HTML, CSS
from pathlib import Path

def markdown_to_pdf(markdown_file, output_pdf):
    """Convert a markdown file to PDF using WeasyPrint."""
    
    # Read the markdown file
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown2.markdown(
        markdown_content,
        extras=['fenced-code-blocks', 'tables', 'break-on-newline', 'header-ids']
    )
    
    # Add CSS styling for better PDF appearance
    css_style = """
    <style>
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 11pt;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
            font-size: 24pt;
        }
        h2 {
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 8px;
            margin-top: 25px;
            font-size: 18pt;
        }
        h3 {
            color: #2980b9;
            margin-top: 20px;
            font-size: 14pt;
        }
        h4 {
            color: #16a085;
            margin-top: 15px;
            font-size: 12pt;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 9pt;
            color: #c7254e;
        }
        pre {
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
            font-size: 9pt;
            line-height: 1.4;
        }
        pre code {
            background-color: transparent;
            padding: 0;
            color: #333;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            font-size: 10pt;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        blockquote {
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-left: 0;
            color: #555;
            font-style: italic;
        }
        ul, ol {
            margin: 10px 0;
            padding-left: 30px;
        }
        li {
            margin: 5px 0;
        }
        hr {
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }
        a {
            color: #3498db;
            text-decoration: none;
        }
        .page-break {
            page-break-after: always;
        }
    </style>
    """
    
    # Combine CSS and HTML
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        {css_style}
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Convert HTML to PDF
    print(f"Converting {markdown_file} to {output_pdf}...")
    HTML(string=full_html).write_pdf(output_pdf)
    print(f"✓ Successfully created {output_pdf}")

if __name__ == "__main__":
    # Convert both markdown files
    files_to_convert = [
        ("PROJECT_ROLES.md", "PROJECT_ROLES.pdf"),
        ("DETAILED_ROLES.md", "DETAILED_ROLES.pdf")
    ]
    
    for md_file, pdf_file in files_to_convert:
        if Path(md_file).exists():
            markdown_to_pdf(md_file, pdf_file)
        else:
            print(f"✗ File not found: {md_file}")
    
    print("\n✓ PDF conversion complete!")
