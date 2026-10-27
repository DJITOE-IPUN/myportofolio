"""
Afterburner presentation helpers.

Pure functions that turn the models' free-text fields into what the themed
pages need: chronological order, flight time, semester progress and the
stripes of each award ribbon. Nothing here writes to the database; the views
call these and hand the results to the templates.
"""
import hashlib
import re
from dataclasses import dataclass
from datetime import date
from typing import Optional

# --------------------------------------------------------------------------
# Periods: "Aug 2026 – Present", "2022 - 2025", "Agustus 2024 s/d Sekarang"
# --------------------------------------------------------------------------

MONTHS = {
    "jan": 1, "feb": 2, "peb": 2, "mar": 3, "apr": 4, "may": 5, "mei": 5,
    "jun": 6, "jul": 7, "aug": 8, "agu": 8, "agt": 8, "sep": 9, "oct": 10,
    "okt": 10, "nov": 11, "dec": 12, "des": 12,
}
ONGOING_WORDS = ("present", "now", "current", "ongoing", "sekarang", "kini", "saat ini", "berlangsung")
SPLIT_RE = re.compile(r"\s*(?:–|—|-|\bto\b|\buntil\b|s/d|\bsampai\b|\bhingga\b)\s*", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
WORD_RE = re.compile(r"[A-Za-z]+")


@dataclass
class Period:
    start: Optional[date]
    end: Optional[date]
    ongoing: bool

    @property
    def months(self):
        """Inclusive length in months, or None when the start is unknown."""
        if not self.start or not self.end:
            return None
        return max(1, (self.end.year - self.start.year) * 12 + self.end.month - self.start.month + 1)


def _point(text, default_month):
    """First month + year found in a fragment, as a date (day 1)."""
    year = YEAR_RE.search(text or "")
    if not year:
        return None
    month = default_month
    for word in WORD_RE.findall(text):
        found = MONTHS.get(word[:3].lower())
        if found:
            month = found
            break
    return date(int(year.group(1)), month, 1)


def parse_period(text, ongoing=None, today=None, start_month=1, end_month=12):
    """Best-effort reading of a free-text date range. Never raises."""
    today = today or date.today()
    text = (text or "").strip()
    lowered = text.lower()
    parts = [p for p in SPLIT_RE.split(text) if p.strip()] if text else []

    start = _point(parts[0], start_month) if parts else None
    end = _point(parts[-1], end_month) if len(parts) > 1 else None

    is_ongoing = any(word in lowered for word in ONGOING_WORDS)
    if ongoing is not None:
        is_ongoing = is_ongoing or bool(ongoing)
    if end and (end.year, end.month) > (today.year, today.month):
        is_ongoing = True  # an expected end date that hasn't arrived yet

    if is_ongoing:
        end = date(today.year, today.month, 1)
    elif start and not end:
        end = start  # a single point in time
    if start and end and end < start:
        start, end = end, start
    return Period(start=start, end=end, ongoing=is_ongoing)


def format_months(months):
    """14 -> '1 yr 2 mo'."""
    if not months:
        return "—"
    years, rest = divmod(months, 12)
    if not years:
        return f"{rest} mo"
    if not rest:
        return f"{years} yr"
    return f"{years} yr {rest} mo"


def split_list(text):
    """'Django, Python,, Git' -> ['Django', 'Python', 'Git']"""
    return [item.strip() for item in (text or "").split(",") if item.strip()]


def _sort_key(period):
    return (period.start is None, period.start or date.max)


# --------------------------------------------------------------------------
# Experience -> Sorties
# --------------------------------------------------------------------------

def build_sorties(experiences, user=None, today=None):
    """Experiences in flight order (oldest first), with derived debrief data."""
    rows = []
    for exp in experiences:
        period = parse_period(exp.date_range, ongoing=exp.is_ongoing, today=today)
        rows.append((period, exp))
    rows.sort(key=lambda row: _sort_key(row[0]))

    sorties = []
    for index, (period, exp) in enumerate(rows, start=1):
        star_ids = {u.pk for u in exp.stars.all()}
        sorties.append({
            "obj": exp,
            "index": index,
            "code": f"SRT-{index:02d}",
            "ongoing": period.ongoing,
            "start": period.start,
            "months": period.months,
            "flight_time": format_months(period.months),
            "outcome": "In flight" if period.ongoing else "Returned to base",
            "kit": split_list(getattr(exp, "kit", "")),
            "star_count": len(star_ids),
            "starred": bool(user and user.is_authenticated and user.pk in star_ids),
        })
    return sorties


def flight_path(count):
    """SVG path through the waypoints, in a viewBox of (count * 100) x 100.

    Waypoints alternate high (y=38) and low (y=62) in the middle of each
    100-unit column; the path takes off at the left edge and ends at "now"
    on the right. Horizontal tangents keep every bend smooth.
    """
    if not count:
        return {"d": "", "width": 100}
    width = count * 100
    points = [(0, 50)] + [(i * 100 + 50, 38 if i % 2 == 0 else 62) for i in range(count)] + [(width, 50)]
    d = [f"M {points[0][0]} {points[0][1]}"]
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        mid = (x2 - x1) / 2
        d.append(f"C {x1 + mid:g} {y1} {x2 - mid:g} {y2} {x2} {y2}")
    return {"d": " ".join(d), "width": width}


def sortie_stats(sorties):
    months = sum(s["months"] or 0 for s in sorties)
    return {
        "count": len(sorties),
        "in_flight": sum(1 for s in sorties if s["ongoing"]),
        "flight_time": format_months(months) if months else "—",
        "categories": len({s["obj"].category for s in sorties}),
    }


# --------------------------------------------------------------------------
# Education -> Qualifications (type ratings)
# --------------------------------------------------------------------------

# rating label, semesters in the programme
DEGREE_PLAN = {
    "bachelor": ("S1", 8),
    "master": ("S2", 4),
    "diploma": ("D3", 6),
    "secondary_school": ("SMA", 6),
}


def build_qualifications(educations, today=None):
    """Education records newest first, each with a status stamp and progress."""
    today = today or date.today()
    rows = []
    for edu in educations:
        # Indonesian academic years start in August
        period = parse_period(edu.date_range, today=today, start_month=8, end_month=6)
        rows.append((period, edu))
    rows.sort(key=lambda row: _sort_key(row[0]), reverse=True)

    quals = []
    for index, (period, edu) in enumerate(rows, start=1):
        rating, semesters = DEGREE_PLAN.get(edu.degree, (None, None))
        semester = None
        progress = 100
        if period.ongoing:
            progress = None
            if period.start and semesters:
                elapsed = (today.year - period.start.year) * 12 + today.month - period.start.month
                semester = min(semesters, max(1, elapsed // 6 + 1))
                progress = round(semester / semesters * 100)
        quals.append({
            "obj": edu,
            "index": index,
            "code": f"TR-{index:02d}",
            "rating": rating or (edu.degree or "—").upper()[:4],
            "ongoing": period.ongoing,
            "status": "In training" if period.ongoing else "Qualified",
            "semester": semester,
            "semesters": semesters,
            "progress": progress,
        })
    return quals


# --------------------------------------------------------------------------
# Awards -> Ribbon rack
# --------------------------------------------------------------------------

# Stripe "colours" are CSS class names, so the night-vision palettes can
# recolour every ribbon without touching this code.
GREYS = ("r-ink", "r-steel", "r-grey", "r-silver")
RIBBON_UNITS = 100  # the SVG is drawn 100 units wide


def _rng(seed_text):
    digest = hashlib.sha256(seed_text.encode("utf-8")).digest()
    position = 0

    def take(n):
        nonlocal position
        value = digest[position % len(digest)] % n
        position += 1
        return value
    return take


def ribbon_stripes(award):
    """Symmetric stripes for one award: a list of {x, w, cls} in 0–100 units.

    The category decides where the red goes; a hash of the title and issuer
    decides the rest, so the same award always gets the same ribbon.
    """
    take = _rng(f"{award.title}|{award.issuer}|{award.category}")
    category = award.category or "honor"
    base = ("r-steel", "r-grey")[take(2)]  # the field colour
    others = [c for c in GREYS + ("r-white",) if c != base]
    contrast = ("r-ink", "r-white") if base == "r-grey" else ("r-silver", "r-white")

    # Bands at the edges, listed from the outer edge inwards.
    edge = [(6 + take(3), "r-red")] if category == "leadership" else [(3 + take(3), contrast[take(2)])]
    for _ in range(1 + take(2)):
        edge.append((2 + take(4), others[take(len(others))]))

    # The centre stripe, plus flanking pinstripes listed from the centre outwards.
    if category == "competition":
        core, flanks = (10 + take(5), "r-red"), [(2, base), (2, "r-silver")]
    elif category == "academic":
        core, flanks = (4 + take(3), "r-white"), [(2, base), (2, "r-red")]
    elif category == "leadership":
        core, flanks = (6 + take(5), "r-silver"), []
    else:  # honor and anything unrecognised: no red at all
        core, flanks = (5 + take(6), "r-white"), [(2, base), (1, "r-grey")]

    def mirrored(x, width, cls):
        return [{"x": x, "w": width, "cls": cls},
                {"x": RIBBON_UNITS - x - width, "w": width, "cls": cls}]

    stripes = [{"x": 0, "w": RIBBON_UNITS, "cls": base}]
    cursor = 0
    for width, cls in edge:
        stripes += mirrored(cursor, width, cls)
        cursor += width

    half_core = core[0] / 2
    reach = 50 - half_core
    for width, cls in flanks:
        reach -= width
        stripes += mirrored(reach, width, cls)
    stripes.append({"x": 50 - half_core, "w": core[0], "cls": core[1]})
    return stripes


def build_rack(awards):
    """Awards newest first with ribbons, plus rows of three for the rack.

    The short row goes on top, centred, the way a real ribbon rack is worn.
    """
    rows = []
    for award in awards:
        period = parse_period(award.date_awarded, start_month=1)
        rows.append((period, award))
    rows.sort(key=lambda row: _sort_key(row[0]), reverse=True)

    items = [{
        "obj": award,
        "index": index,
        "code": f"CIT-{index:02d}",
        "stripes": ribbon_stripes(award),
        "category": award.get_category_display() or "Honor",
    } for index, (_, award) in enumerate(rows, start=1)]

    rack, rest = [], list(items)
    first = len(rest) % 3 or 3
    if rest:
        rack.append(rest[:first])
        rest = rest[first:]
    while rest:
        rack.append(rest[:3])
        rest = rest[3:]
    return items, rack
