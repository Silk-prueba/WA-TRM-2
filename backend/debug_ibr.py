import sys, os, re, requests, json
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json, application/xml, text/html, */*",
}

# Try likely SDMX / REST endpoints on suameca.banrep.gov.co
# Series ID for IBR appears to be 241 from the page URL
candidates = [
    "https://suameca.banrep.gov.co/estadisticas-economicas/rest/data/IBR/all/all?lastNObservations=2",
    "https://suameca.banrep.gov.co/estadisticas-economicas/rest/data/241/all/all?lastNObservations=2",
    "https://suameca.banrep.gov.co/estadisticas-economicas/rest/series/241/data?lastN=2",
    "https://suameca.banrep.gov.co/estadisticas-economicas/api/series/241/data",
    "https://suameca.banrep.gov.co/ws/rest/data/IBR?lastNObservations=2",
    "https://suameca.banrep.gov.co/ws/rest/data/241?lastNObservations=2",
    # SDMX standard pattern with agency
    "https://suameca.banrep.gov.co/estadisticas-economicas/rest/data/BR,IBR,1.0/all/all?lastNObservations=2",
]

for url in candidates:
    try:
        r = requests.get(url, headers=_HEADERS, timeout=10)
        ct = r.headers.get("Content-Type", "?")
        print(f"\n[HTTP {r.status_code}] {ct}")
        print(f"  URL: {url}")
        if r.status_code == 200 and len(r.text) < 50000:
            print(f"  Body: {r.text[:400]}")
        else:
            print(f"  len={len(r.text)}")
    except Exception as e:
        print(f"\n  ERROR {url}: {e}")

# Also download the PDF and try to read it as raw bytes for any clues
print("\n\n=== PDF raw text (first 3000 chars after decoding) ===")
try:
    pdf_url = "https://suameca.banrep.gov.co/archivos/webservices/documento_tecnico_ws_consumo_sdmx_ibr.pdf"
    r = requests.get(pdf_url, headers=_HEADERS, timeout=15)
    print(f"HTTP {r.status_code}  Content-Type: {r.headers.get('Content-Type','?')}  len={len(r.content)}")
    # Save to disk so it can be read
    pdf_path = "/tmp/ibr_doc.pdf"
    with open(pdf_path, "wb") as f:
        f.write(r.content)
    print(f"Saved to {pdf_path}")

    # Try pdfplumber or pypdf2 if available
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages[:5]):
                print(f"\n--- Page {i+1} ---")
                print(page.extract_text())
    except ImportError:
        try:
            import pypdf
            reader = pypdf.PdfReader(pdf_path)
            for i, page in enumerate(reader.pages[:5]):
                print(f"\n--- Page {i+1} ---")
                print(page.extract_text())
        except ImportError:
            # Last resort: grep for URLs in raw bytes
            raw = r.content.decode("latin-1", errors="replace")
            urls = re.findall(r'https?://[^\s\x00-\x1f"\'<>]+', raw)
            print("URLs found in PDF bytes:", urls[:20])
            # Also look for text fragments
            readable = re.sub(r'[^\x20-\x7e\n]', ' ', raw)
            readable = re.sub(r' {3,}', '  ', readable)
            print("\nReadable fragments:\n", readable[:3000])
except Exception as e:
    print(f"ERROR: {e}")
