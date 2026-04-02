def normalize_authors(document):
    authors = document.get("authors", [])

    if isinstance(authors, str):
        authors = [authors]

    if isinstance(authors, dict):
        authors = [authors]

    cleaned = []
    if isinstance(authors, list):
        for a in authors:
            if not isinstance(a, dict):
                continue

            first_name = str(a.get("first_name", "")).strip()
            last_name = str(a.get("last_name", "")).strip()
            email = str(a.get("email", "")).strip()

            if first_name or last_name or email:
                cleaned.append({
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email
                })

    document["authors"] = cleaned
    return document