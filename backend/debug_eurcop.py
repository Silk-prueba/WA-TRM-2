import sys, os, re, requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

URL = "https://suameca.banrep.gov.co/indicadores-economicos-del-dia/"

r = requests.get(URL, headers=_HEADERS, timeout=15)
print(f"HTTP {r.status_code}  len={len(r.text)}")

soup = BeautifulSoup(r.text, "lxml")

print("\n--- All table rows ---")
for row in soup.find_all("tr"):
    cells = [td.get_text(" ", strip=True) for td in row.find_all(["td", "th"])]
    if cells:
        print(cells)

print("\n--- Text snippet around 'euro' ---")
text = soup.get_text(" ", strip=True)
for m in re.finditer(r'.{0,80}euro.{0,80}', text, re.IGNORECASE):
    print(repr(m.group()))
    print()
