import re
import logging
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta

logger = logging.getLogger(__name__)

_DAYS_ES = {
    0: "Lunes", 1: "Martes", 2: "Miércoles",
    3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo",
}
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


# ── Formatting helpers ──────────────────────────────────────────────────────

def _cop_fmt(value: float) -> str:
    """4167.06  →  '4.167,06'  (Colombian thousands/decimal separators)"""
    s = f"{value:,.2f}"                                   # '4,167.06'
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _ibr_fmt(value: float) -> str:
    """9.521  →  '9,521'  (Colombian decimal separator, 3 decimals)"""
    return f"{value:.3f}".replace(".", ",")


def _change_tag(current: float, previous: float) -> str:
    """Returns  '(+0,39%)🔼'  or  '(-0,15%)🔽'  based on the relative change."""
    if previous == 0:
        return "(-0,00%)🔽"
    pct = (current - previous) / previous * 100
    sign = "+" if pct > 0 else "-"
    arrow = "🔼" if pct > 0 else "🔽"
    formatted = f"{abs(pct):.2f}".replace(".", ",")
    return f"({sign}{formatted}%){arrow}"


def _arrow(current: float, previous: float) -> str:
    return "🔼" if current > previous else "🔽"


# ── TRM ─────────────────────────────────────────────────────────────────────

def _fetch_trm() -> tuple[float, float]:
    """
    Official TRM from datos.gov.co (Superintendencia Financiera de Colombia).
    Same rate published by La República and validated by BANREP.
    """
    resp = requests.get(
        "https://www.datos.gov.co/resource/mcec-87by.json",
        params={"$limit": 2, "$order": "vigenciadesde DESC"},
        timeout=10,
    )
    resp.raise_for_status()
    records = resp.json()
    current = float(records[0]["valor"])
    previous = float(records[1]["valor"]) if len(records) > 1 else current
    return current, previous


# ── EUR/COP ──────────────────────────────────────────────────────────────────

def _fetch_eurcop() -> tuple[float, float]:
    """
    EUR/COP from dineroeneltiempo.com (SSR page, rate shown as $X,XXX.XX near
    'PRECIO HOY'). Falls back to Frankfurter ECB API on any parse failure.
    """
    try:
        resp = requests.get(
            "https://www.dineroeneltiempo.com/divisas/eur-cop",
            headers=_HEADERS,
            timeout=12,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        text = soup.get_text(" ", strip=True)

        # Site uses US number format: $4,273.76
        candidates = re.findall(r'\$\s*([\d]{1,2},[\d]{3}(?:\.[\d]{2})?)', text)
        for raw in candidates:
            value = float(raw.replace(",", ""))
            if 3_000 < value < 8_000:
                _, prev = _fetch_frankfurter("COP")
                return value, prev

        # Broader fallback: any large number in the plausible COP range
        candidates2 = re.findall(r'\b(\d{1,2}[,\.]\d{3}(?:[,\.]\d{2})?)\b', text)
        for raw in candidates2:
            norm = raw.replace(".", "").replace(",", ".")
            try:
                value = float(norm)
                if 3_000 < value < 8_000:
                    _, prev = _fetch_frankfurter("COP")
                    return value, prev
            except ValueError:
                continue

        raise ValueError("No plausible EUR/COP value found on dineroeneltiempo.com")

    except Exception as exc:
        logger.warning("dineroeneltiempo.com scrape failed, using Frankfurter: %s", exc)
        return _fetch_frankfurter("COP")


# ── EUR/USD ──────────────────────────────────────────────────────────────────

def _fetch_eurusd() -> tuple[float, float]:
    """
    Official EUR/USD reference rate from the ECB.
    Same data as: https://www.ecb.europa.eu/stats/policy_and_exchange_rates/
                  euro_reference_exchange_rates/html/eurofxref-graph-usd.en.html
    """
    resp = requests.get(
        "https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A"
        "?lastNObservations=5&format=csvdata",
        headers=_HEADERS,
        timeout=10,
    )
    resp.raise_for_status()

    values = []
    for line in resp.text.strip().splitlines():
        if not line or line.startswith("KEY"):
            continue
        parts = line.split(",")
        if len(parts) >= 8:
            try:
                values.append(float(parts[7]))
            except ValueError:
                continue

    if len(values) >= 2:
        return values[-1], values[-2]
    if len(values) == 1:
        return values[0], values[0]
    raise RuntimeError("No EUR/USD data returned from ECB data API")


def _fetch_frankfurter(target: str) -> tuple[float, float]:
    """
    Fetches EUR/{target} for the latest available date and the previous business
    day from the Frankfurter API (api.frankfurter.dev).
    """
    resp = requests.get(
        f"https://api.frankfurter.dev/v1/latest?from=EUR&to={target}",
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    current = data["rates"][target]
    today_str = data["date"]

    start_str = (
        datetime.strptime(today_str, "%Y-%m-%d") - timedelta(days=5)
    ).strftime("%Y-%m-%d")
    prev_end_str = (
        datetime.strptime(today_str, "%Y-%m-%d") - timedelta(days=1)
    ).strftime("%Y-%m-%d")

    range_resp = requests.get(
        f"https://api.frankfurter.dev/v1/{start_str}..{prev_end_str}?from=EUR&to={target}",
        timeout=10,
    )
    range_resp.raise_for_status()
    range_data = range_resp.json()

    past_dates = sorted(range_data["rates"].keys())
    previous = range_data["rates"][past_dates[-1]][target] if past_dates else current
    return current, previous


# ── IBR Overnight ────────────────────────────────────────────────────────────

_IBR_URL = "https://www.banrep.gov.co/es/glosario/indicador-bancario-referencia-ibr"

def _fetch_ibr() -> tuple[float, float]:
    """
    IBR Overnight from BANREP.
    Source: https://www.banrep.gov.co/es/glosario/indicador-bancario-referencia-ibr
    Returns (current, previous); previous == current when history is unavailable.
    """
    resp = requests.get(_IBR_URL, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # 1. Try structured table: look for a row containing "overnight"
    for row in soup.find_all("tr"):
        cells = [td.get_text(" ", strip=True) for td in row.find_all(["td", "th"])]
        row_text = " ".join(cells).lower()
        if "overnight" in row_text:
            for cell in cells:
                m = re.search(r'(\d{1,2}[,\.]\d{3,4})', cell)
                if m:
                    val = float(m.group(1).replace(",", "."))
                    if 5.0 <= val <= 25.0:
                        return val, val

    # 2. Regex scan over plain text
    text = soup.get_text(" ", strip=True)
    patterns = [
        r'overnight[^%\n]{0,80}?(\d{1,2}[,\.]\d{3,4})\s*%',
        r'IBR[^%\n]{0,80}?overnight[^%\n]{0,80}?(\d{1,2}[,\.]\d{3,4})\s*%',
        r'(\d{1,2}[,\.]\d{3,4})\s*%[^%\n]{0,40}?overnight',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = float(m.group(1).replace(",", "."))
            if 5.0 <= val <= 25.0:
                return val, val

    # 3. Broad scan: any plausible rate near "IBR"
    ibr_section = re.search(r'IBR.{0,200}', text, re.IGNORECASE | re.DOTALL)
    if ibr_section:
        for n in re.findall(r'\b(\d{1,2}[,\.]\d{3,4})\b', ibr_section.group()):
            val = float(n.replace(",", "."))
            if 5.0 <= val <= 25.0:
                return val, val

    raise RuntimeError("Could not retrieve IBR overnight rate from BANREP")


# ── Message builder ──────────────────────────────────────────────────────────

def get_exchange_rate_message() -> str:
    today = date.today()
    header = f"{_DAYS_ES[today.weekday()]}  {today.day:02d}/{today.month:02d}"
    lines = [header]

    try:
        trm, trm_prev = _fetch_trm()
        lines.append(f"TRM: {_cop_fmt(trm)} {_change_tag(trm, trm_prev)}")
    except Exception as exc:
        logger.error("TRM error: %s", exc)
        lines.append("TRM: No disponible ⚠️")

    try:
        eurcop, eurcop_prev = _fetch_eurcop()
        lines.append(f"EURCOP: {_cop_fmt(eurcop)} {_change_tag(eurcop, eurcop_prev)}")
    except Exception as exc:
        logger.error("EURCOP error: %s", exc)
        lines.append("EURCOP: No disponible ⚠️")

    try:
        eurusd, eurusd_prev = _fetch_eurusd()
        lines.append(f"EUR/USD: {eurusd:.4f} {_change_tag(eurusd, eurusd_prev)}")
    except Exception as exc:
        logger.error("EUR/USD error: %s", exc)
        lines.append("EUR/USD: No disponible ⚠️")

    try:
        ibr, ibr_prev = _fetch_ibr()
        lines.append(f"IBR OVERNIGHT: {_ibr_fmt(ibr)}%")
    except Exception as exc:
        logger.error("IBR error: %s", exc)
        lines.append("IBR OVERNIGHT: No disponible ⚠️")

    return "\n".join(lines)
