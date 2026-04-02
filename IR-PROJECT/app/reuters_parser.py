import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
from .dates import ensure_document_has_date
from .geo import ensure_document_has_location

def parse_reuters_date(date_str):
    try:
        date_str = re.sub(r"\.\d+$", "", date_str)
        dt = datetime.strptime(date_str, "%d-%b-%Y %H:%M:%S")
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except:
        return None


def extract_temporal_expressions(text):
    temporal_patterns = [
        r"\b\d{4}\b",
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
    ]

    expressions = []
    for pattern in temporal_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        expressions.extend(matches)

    return list(set(expressions))[:10]


def parse_sgm_file(file_path):
    documents = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        soup = BeautifulSoup(content, "html.parser")
        reuters_docs = soup.find_all("reuters")

        for doc in reuters_docs:
            try:
                title_tag = doc.find("title")
                body_tag = doc.find("body")
                text_tag = doc.find("text")
                date_tag = doc.find("date")
                places_tag = doc.find("places")

                title = title_tag.get_text(" ", strip=True) if title_tag else ""
                body = body_tag.get_text(" ", strip=True) if body_tag else ""
                date_str = date_tag.get_text(" ", strip=True) if date_tag else ""

                if not body and text_tag:
                    body = text_tag.get_text(" ", strip=True)

                places = []
                if places_tag:
                    place_tags = places_tag.find_all("d")
                    places = [p.get_text(" ", strip=True) for p in place_tags]

                doc_date = parse_reuters_date(date_str) if date_str else None

                document = {
                    "title": title,
                    "content": body,
                    "date": doc_date,
                    "authors": [
                        {
                              "first_name": "Reuters",
                              "last_name": "Staff",
                              "email": "staff@reuters.com"
                        }
                              ], 
                    "georeferences": places if places else [],
                    "temporal_expressions": extract_temporal_expressions(body),
                    "source_file": os.path.basename(file_path)
                }

                document = ensure_document_has_date(document)
                document = ensure_document_has_location(document, do_geocode=False)

                if title or body:
                    documents.append(document)

            except Exception as e:
                print(f"Error parsing document: {str(e)}")
                continue

        return documents

    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return []