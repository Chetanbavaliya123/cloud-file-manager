"""
Converts docs/REPORT.md into a beautifully formatted PDF report
using python-markdown and headless Microsoft Edge / Google Chrome.
"""

import os
import subprocess
import markdown

REPORT_MD_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "REPORT.md"))
HTML_OUT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "report_preview.html"))
PDF_OUT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "REPORT.pdf"))

def build_pdf():
    if not os.path.exists(REPORT_MD_PATH):
        print(f"Error: {REPORT_MD_PATH} not found.")
        return False

    with open(REPORT_MD_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Convert markdown to HTML with tables, code fences, etc.
    html_content = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"]
    )

    styled_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Cloud Computing Assignment Report</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm 15mm 20mm 15mm;
            @bottom-right {{
                content: counter(page);
            }}
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            color: #1e293b;
            line-height: 1.6;
            font-size: 11pt;
            padding: 10px;
        }}
        h1 {{
            color: #047857;
            font-size: 18pt;
            border-bottom: 2px solid #059669;
            padding-bottom: 6px;
            margin-top: 0;
            text-align: center;
        }}
        h2 {{
            color: #065f46;
            font-size: 14pt;
            margin-top: 18px;
            margin-bottom: 8px;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 4px;
        }}
        h3 {{
            color: #1e293b;
            font-size: 12pt;
            margin-top: 14px;
            margin-bottom: 6px;
        }}
        hr {{
            border: 0;
            height: 1px;
            background: #cbd5e1;
            margin: 16px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 14px 0;
            font-size: 9.5pt;
        }}
        table th, table td {{
            border: 1px solid #cbd5e1;
            padding: 8px 10px;
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
            font-size: 9pt;
        }}
        code {{
            padding: 2px 5px;
            color: #0f172a;
        }}
        pre {{
            padding: 12px;
            overflow-x: auto;
            border: 1px solid #e2e8f0;
            line-height: 1.4;
            white-space: pre-wrap;
        }}
        blockquote {{
            border-left: 4px solid #059669;
            margin: 12px 0;
            padding: 6px 14px;
            background-color: #ecfdf5;
            color: #065f46;
            font-size: 10pt;
        }}
        ul, ol {{
            padding-left: 24px;
            margin: 8px 0;
        }}
        li {{
            margin-bottom: 4px;
        }}
        .header-box {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 20px;
            text-align: center;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""

    with open(HTML_OUT_PATH, "w", encoding="utf-8") as f:
        f.write(styled_html)
    print(f"Generated HTML preview at: {HTML_OUT_PATH}")

    # Look for Edge or Chrome
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
        print("Warning: Neither Edge nor Chrome found for headless PDF generation.")
        return False

    cmd = [
        browser_exe,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF_OUT_PATH}",
        HTML_OUT_PATH
    ]

    print(f"Running headless browser: {browser_exe} to produce PDF...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(PDF_OUT_PATH) and os.path.getsize(PDF_OUT_PATH) > 0:
        print(f"Successfully generated PDF: {PDF_OUT_PATH} ({os.path.getsize(PDF_OUT_PATH)} bytes)")
        return True
    else:
        print(f"PDF generation failed: {res.stderr}")
        return False

if __name__ == "__main__":
    build_pdf()
