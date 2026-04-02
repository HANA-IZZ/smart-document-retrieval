import re
import time
from collections import Counter
from geopy.geocoders import Nominatim
from .nlp import nlp, NLP_AVAILABLE

geolocator = Nominatim(user_agent="smart_document_retrieval")

def extract_all_locations(text):
    if not text or not NLP_AVAILABLE:
        return []

    doc = nlp(text[:8000])
    raw = [ent.text.strip() for ent in doc.ents if ent.label_ in ["GPE", "LOC", "FAC"]]

    cleaned = []
    seen = set()
    for loc in raw:
        norm = re.sub(r"\s+", " ", loc).strip()
        key = norm.lower()
        if key and key not in seen:
            seen.add(key)
            cleaned.append(norm)

    return cleaned


def extract_most_frequent_location(text):
    if not text or not NLP_AVAILABLE:
        return None

    doc = nlp(text[:8000])
    raw = [ent.text.strip() for ent in doc.ents if ent.label_ in ["GPE", "LOC", "FAC"]]
    if not raw:
        return None

    norm = [re.sub(r"\s+", " ", x).lower().strip() for x in raw]
    counts = Counter(norm)
    top_norm = counts.most_common(1)[0][0]

    for loc in raw:
        if re.sub(r"\s+", " ", loc).lower().strip() == top_norm:
            return re.sub(r"\s+", " ", loc).strip()

    return None


GEOCODE_CACHE = {}

def geocode_locations(location_names, limit=10):
    points = []
    for name in location_names[:limit]:
        key = str(name).strip().lower()
        if not key:
            continue

        if key in GEOCODE_CACHE:
            cached = GEOCODE_CACHE[key]
            if cached:
                points.append(cached)
            continue

        try:
            loc = geolocator.geocode(name, timeout=5)
            time.sleep(0.15)
            if loc:
                point = {"lat": loc.latitude, "lon": loc.longitude}
                GEOCODE_CACHE[key] = point
                points.append(point)
            else:
                GEOCODE_CACHE[key] = None
        except:
            GEOCODE_CACHE[key] = None

    return points


def ensure_document_has_location(document, do_geocode=True, geo_limit=1):
    text = ((document.get("content") or "") + " " + (document.get("title") or "")).strip()

    existing = document.get("georeferences") or []
    if isinstance(existing, str):
        existing = [existing]

    cleaned_existing = []
    for x in existing:
        v = str(x).strip()
        if v:
            cleaned_existing.append(v)

    cleaned_existing = list(dict.fromkeys(cleaned_existing))

    if cleaned_existing:
        document["georeferences"] = cleaned_existing
        document["location_source"] = document.get("location_source", "from-places")
    else:
        all_locs = extract_all_locations(text) if text else []
        if all_locs:
            document["georeferences"] = all_locs
            document["location_source"] = "auto-extracted"
        else:
            document["georeferences"] = []
            document["location_source"] = "default"

    if do_geocode and document["georeferences"]:
        document["geo_points"] = geocode_locations(document["georeferences"], limit=geo_limit)

        main_loc = extract_most_frequent_location(text)
        if main_loc:
            main_point = geocode_locations([main_loc], limit=1)
            if main_point:
                document["geopoint"] = main_point[0]

    return document