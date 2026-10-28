"""
Converts Markdown reports in docs/ into beautifully formatted PDF documents
using python-markdown and headless Microsoft Edge / Google Chrome.
"""

import os
import sys
import subprocess
import markdown

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))

def convert_md_to_pdf(md_filename, pdf_filename):
    md_path = os.path.join(DOCS_DIR, md_filename)
    pdf_path = os.path.join(DOCS_DIR, pdf_filename)
    html_preview_path = os.path.join(DOCS_DIR, f"temp_{os.path.splitext(md_filename)[0]}.html")

    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found.")
        return False

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    html_content = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"]
    )

    styled_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{os.path.splitext(pdf_filename)[0]}</title>
    <style>
        @page {{
            size: A4;
            margin: 18mm 14mm 18mm 14mm;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            color: #0f172a;
            line-height: 1.55;
            font-size: 10.5pt;
            padding: 10px;
        }}
        h1 {{
            color: #047857;
            font-size: 17pt;
            border-bottom: 2px solid #059669;
            padding-bottom: 6px;
            margin-top: 0;
            text-align: center;
        }}
        h2 {{
            color: #065f46;
            font-size: 13pt;
            margin-top: 18px;
            margin-bottom: 8px;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 4px;
        }}
        h3 {{
            color: #1e293b;
            font-size: 11pt;
            margin-top: 12px;
            margin-bottom: 6px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 12px 0;
            font-size: 9pt;
        }}
        table th, table td {{
            border: 1px solid #cbd5e1;
            padding: 6px 8px;
            text-align: left;
        }}
        table th {{
            background-color: #f1f5f9;
            color: #0f172a;
            font-weight: 700;
        }}
        table tr:nth-child(even) {{
            background-color: #f8fafc;
        }}
        pre, code {{
            font-family: Consolas, "Courier New", monospace;
            background-color: #f1f5f9;
            border-radius: 4px;
            font-size: 8.5pt;
        }}
        code {{
            padding: 2px 4px;
            color: #0f172a;
        }}
        pre {{
            padding: 10px;
            overflow-x: auto;
            border: 1px solid #e2e8f0;
            line-height: 1.4;
            white-space: pre-wrap;
        }}
        blockquote {{
            border-left: 4px solid #059669;
            margin: 10px 0;
            padding: 6px 12px;
            background-color: #ecfdf5;
            color: #065f46;
            font-size: 9.5pt;
        }}
        img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            margin: 10px 0;
        }}
        ul, ol {{
            padding-left: 20px;
            margin: 6px 0;
        }}
        li {{
            margin-bottom: 3px;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""

    with open(html_preview_path, "w", encoding="utf-8") as f:
        f.write(styled_html)

    browser_candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    browser_exe = None
    for cand in browser_candidates:
        if os.path.exists(cand):
            browser_exe = cand
            break

    if not browser_exe:
        print("Warning: Neither Edge nor Chrome found.")
        return False

    cmd = [
        browser_exe,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_preview_path
    ]

    subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(html_preview_path):
        os.remove(html_preview_path)

    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
        print(f"[SUCCESS] Generated: {pdf_filename} ({os.path.getsize(pdf_path)} bytes)")
        return True
    else:
        print(f"[ERROR] Failed: {pdf_filename}")
        return False

if __name__ == "__main__":
    convert_md_to_pdf("REPORT.md", "REPORT.pdf")
    convert_md_to_pdf("PROJECT_COMPLETE_REPORT.md", "PROJECT_COMPLETE_REPORT.pdf")
