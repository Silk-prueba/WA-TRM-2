from datetime import date, timedelta


def _easter_sunday(year: int) -> date:
    """Anonymous Gregorian algorithm to compute Easter Sunday."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def _next_monday(d: date) -> date:
    """Returns d unchanged if already Monday, otherwise the next Monday (Ley Emiliani)."""
    days_ahead = -d.weekday()  # Monday is weekday 0
    if days_ahead < 0:
        days_ahead += 7
    return d + timedelta(days=days_ahead)


def get_colombian_holidays(year: int) -> list[date]:
    """
    Returns all Colombian public holidays for the given year.

    Colombia has two categories:
    - Fixed-date holidays (always the same calendar date).
    - Ley Emiliani holidays (moved to the following Monday when not already on Monday),
      including three holidays tied to the Easter cycle.
    """
    holidays: list[date] = []

    # --- Fixed holidays ---
    holidays += [
        date(year, 1, 1),    # Año Nuevo
        date(year, 5, 1),    # Día del Trabajo
        date(year, 7, 20),   # Día de la Independencia
        date(year, 8, 7),    # Batalla de Boyacá
        date(year, 12, 8),   # Inmaculada Concepción
        date(year, 12, 25),  # Navidad
    ]

    # --- Ley Emiliani holidays (moved to next Monday) ---
    emiliani = [
        date(year, 1, 6),    # Reyes Magos
        date(year, 3, 19),   # San José
        date(year, 6, 29),   # San Pedro y San Pablo
        date(year, 8, 15),   # Asunción de la Virgen
        date(year, 10, 12),  # Día de la Hispanidad
        date(year, 11, 1),   # Todos los Santos
        date(year, 11, 11),  # Independencia de Cartagena
    ]
    holidays += [_next_monday(d) for d in emiliani]

    # --- Easter-based holidays ---
    easter = _easter_sunday(year)
    holidays += [
        easter - timedelta(days=3),             # Jueves Santo
        easter - timedelta(days=2),             # Viernes Santo
        _next_monday(easter + timedelta(days=39)),  # Ascensión del Señor
        _next_monday(easter + timedelta(days=60)),  # Corpus Christi
        _next_monday(easter + timedelta(days=68)),  # Sagrado Corazón de Jesús
    ]

    return sorted(set(holidays))


def is_colombian_holiday(d: date | None = None) -> bool:
    """Returns True if *d* (defaults to today) is a Colombian public holiday."""
    if d is None:
        d = date.today()
    return d in get_colombian_holidays(d.year)
