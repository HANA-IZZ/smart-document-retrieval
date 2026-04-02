import re
from datetime import datetime
import dateparser

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12
}

def normalize_date_value(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%dT%H:%M:%S")

    if isinstance(value, str):
        s = value.strip()

        m = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(\.\d+)?(Z)?$", s)
        if m:
            return m.group(1)

        m2 = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(\.\d+)?([+-]\d{2}:\d{2})$", s)
        if m2:
            return m2.group(1)

        dt = dateparser.parse(s)
        if dt:
            return dt.strftime("%Y-%m-%dT%H:%M:%S")

    return None


def parse_date_candidates_from_text(text, limit=10):
    if not text:
        return []

    cands = []

    for m in re.findall(r"\b(\d{4})-(\d{2})-(\d{2})\b", text):
        y, mo, d = map(int, m)
        try:
            cands.append(datetime(y, mo, d))
        except:
            pass

    for m in re.findall(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b", text):
        mo, d, y = m
        y = int(y)
        if y < 100:
            y += 1900 if y >= 50 else 2000
        try:
            cands.append(datetime(int(y), int(mo), int(d)))
        except:
            pass

    for m in re.findall(
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b",
        text,
        re.IGNORECASE
    ):
        mon, day, year = m
        try:
            cands.append(datetime(int(year), MONTHS[mon.lower()], int(day)))
        except:
            pass

    uniq = []
    seen = set()
    for d in cands:
        key = d.date().isoformat()
        if key not in seen:
            seen.add(key)
            uniq.append(d)

    return uniq[:limit]


def ensure_document_has_date(document):
    if document.get("date"):
        fixed = normalize_date_value(document.get("date"))
        if fixed:
            document["date"] = fixed
        else:
            document.pop("date", None)

        if "extracted_dates" not in document:
            document["extracted_dates"] = []
        return document

    text = ((document.get("title") or "") + " " + (document.get("content") or "")).strip()
    cands = parse_date_candidates_from_text(text, limit=10)

    if cands:
        chosen = max(cands)
        document["date"] = chosen.strftime("%Y-%m-%dT%H:%M:%S")
        document["extracted_dates"] = [d.strftime("%Y-%m-%dT%H:%M:%S") for d in cands]
    else:
        document["extracted_dates"] = []

    return document