def remove_duplicates(results, key="title"):
    seen = set()
    unique_results = []
    for item in results:
        identifier = item.get(key, "") if isinstance(item, dict) else getattr(item, key, "")
        identifier = str(identifier).lower().strip()
        if identifier and identifier not in seen:
            seen.add(identifier)
            unique_results.append(item)
    return unique_results