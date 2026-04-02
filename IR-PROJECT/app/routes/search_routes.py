import re
from datetime import datetime, timedelta
from flask import request, jsonify
from ..opensearch_client import client
from ..config import INDEX_NAME
from ..remove_duplicates import remove_duplicates

def parse_temporal_to_date_filter(t):
    if not t:
        return None

    t = t.strip()

    try:
        d = datetime.strptime(t, "%Y-%m-%d")
        start = d.strftime("%Y-%m-%dT00:00:00")
        end = (d + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00")
        return {"range": {"date": {"gte": start, "lt": end}}}
    except:
        pass

    try:
        d = datetime.strptime(t, "%m/%d/%Y")
        start = d.strftime("%Y-%m-%dT00:00:00")
        end = (d + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00")
        return {"range": {"date": {"gte": start, "lt": end}}}
    except:
        pass

    if re.fullmatch(r"\d{4}", t):
        y = int(t)
        start = f"{y}-01-01T00:00:00"
        end = f"{y+1}-01-01T00:00:00"
        return {
            "bool": {
                "should": [
                    {"range": {"date": {"gte": start, "lt": end}}},
                    {"match": {"temporal_expressions": {"query": t, "boost": 2.0}}}
                ],
                "minimum_should_match": 1
            }
        }

    return {"match": {"temporal_expressions": {"query": t, "boost": 1.5}}}


def register_search_routes(app):

    @app.route("/api/search/autocomplete", methods=["GET"])
    def autocomplete():
        try:
            query = request.args.get("q", "").strip()
            size = int(request.args.get("size", 10))

            if len(query) < 3:
                return jsonify({"success": True, "results": []})

            search_query = {
                "size": size * 3,
                "query": {
                    "bool": {
                        "should": [
                            {"match": {"title": {"query": query, "fuzziness": "AUTO", "boost": 2}}},
                            {"match_phrase_prefix": {"title": {"query": query, "boost": 3}}}
                        ],
                        "minimum_should_match": 1
                    }
                },
                "_source": ["title", "content", "georeferences", "location_source", "date"]
            }

            response = client.search(index=INDEX_NAME, body=search_query)

            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                results.append({
                    "id": hit["_id"],
                    "title": source.get("title", ""),
                    "content": source.get("content", ""),
                    "georeferences": source.get("georeferences", []),
                    "location_source": source.get("location_source", "unknown"),
                    "score": hit["_score"]
                })

            results = remove_duplicates(results, key="title")
            return jsonify({"success": True, "results": results[:size]})

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


    @app.route("/api/search/smart", methods=["POST"])
    def smart_search():
        try:
            data = request.json or {}
            query_text = (data.get("query") or "").strip()
            temporal = (data.get("temporal_expression") or "").strip()
            geo = (data.get("georeference") or "").strip()
            size = int(data.get("size", 10))

            must_clauses = []
            should_clauses = []
            filter_clauses = []

            if query_text:
                must_clauses.append({
                    "bool": {
                        "should": [
                            {"term": {"title.keyword": {"value": query_text, "boost": 40}}},
                            {"match_phrase": {"title": {"query": query_text, "boost": 18}}},
                            {"match": {"title": {"query": query_text, "boost": 6, "fuzziness": "AUTO"}}},
                            {"match_phrase": {"content": {"query": query_text, "boost": 6}}},
                            {"match": {"content": {"query": query_text, "boost": 3, "fuzziness": "AUTO"}}}
                        ],
                        "minimum_should_match": 1
                    }
                })

            if temporal:
                tf = parse_temporal_to_date_filter(temporal)
                if tf:
                    if "range" in tf:
                        should_clauses.append({
                            "constant_score": {"filter": tf, "boost": 3}
                        })
                    else:
                        should_clauses.append(tf)

            if geo:
                should_clauses.append({"term": {"georeferences.keyword": {"value": geo, "boost": 60}}})
                should_clauses.append({"match": {"georeferences": {"query": geo, "boost": 15}}})

            search_query = {
                "size": size * 3,
                "query": {
                    "bool": {
                        "must": must_clauses,
                        "filter": filter_clauses,
                        "should": should_clauses,
                        "minimum_should_match": 0
                    }
                },
                "sort": [
                    "_score",
                    {"date": {"order": "desc", "missing": "_last"}}
                ]
            }

            response = client.search(index=INDEX_NAME, body=search_query)

            results = []
            for hit in response["hits"]["hits"]:
                result = hit["_source"]
                result["id"] = hit["_id"]
                result["score"] = hit["_score"]
                if not result.get("georeferences"):
                    result["georeferences"] = []
                results.append(result)

            results = remove_duplicates(results, key="title")

            return jsonify({
                "success": True,
                "results": results[:size],
                "total": len(results)
            })

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500