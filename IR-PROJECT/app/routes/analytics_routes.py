from flask import request, jsonify
from ..opensearch_client import client
from ..config import INDEX_NAME

def register_analytics_routes(app):

    @app.route("/api/analytics/top-georeferences", methods=["GET"])
    def top_georeferences():
        try:
            size = int(request.args.get("size", 10))

            query = {
                "size": 0,
                "aggs": {
                    "top_georeferences": {
                        "terms": {
                            "field": "georeferences.keyword",
                            "size": size * 2
                        }
                    }
                }
            }

            response = client.search(index=INDEX_NAME, body=query)

            buckets = response.get("aggregations", {}).get("top_georeferences", {}).get("buckets", [])
            filtered = [b for b in buckets if b.get("key")]

            results = [{"georeference": b["key"], "count": b["doc_count"]} for b in filtered[:size]]
            return jsonify({"success": True, "results": results})

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


    @app.route("/api/analytics/time-distribution", methods=["GET"])
    def time_distribution():
        try:
            interval = request.args.get("interval", "1d")

            query = {
                "size": 0,
                "aggs": {
                    "documents_over_time": {
                        "date_histogram": {
                            "field": "date",
                            "calendar_interval": interval,
                            "format": "yyyy-MM-dd"
                        }
                    }
                }
            }

            response = client.search(index=INDEX_NAME, body=query)

            buckets = response.get("aggregations", {}).get("documents_over_time", {}).get("buckets", [])
            results = [{"date": b["key_as_string"], "count": b["doc_count"]} for b in buckets]

            return jsonify({"success": True, "results": results})

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


    @app.route("/api/analytics/dashboard", methods=["GET"])
    def dashboard():
        try:
            total_docs = client.count(index=INDEX_NAME)["count"]

            unique_geo_query = {
                "size": 0,
                "aggs": {
                    "unique_locations": {
                        "cardinality": {
                            "field": "georeferences.keyword"
                        }
                    }
                }
            }
            unique_geo_response = client.search(index=INDEX_NAME, body=unique_geo_query)
            unique_locations_count = unique_geo_response.get("aggregations", {}).get("unique_locations", {}).get("value", 0)

            top_geo_query = {
                "size": 0,
                "aggs": {
                    "top_georeferences": {
                        "terms": {
                            "field": "georeferences.keyword",
                            "size": 10
                        }
                    }
                }
            }
            geo_response = client.search(index=INDEX_NAME, body=top_geo_query)
            buckets = geo_response.get("aggregations", {}).get("top_georeferences", {}).get("buckets", [])
            top_geo = [{"georeference": b["key"], "count": b["doc_count"]} for b in buckets if b.get("key")]

            time_query = {
                "size": 0,
                "aggs": {
                    "documents_over_time": {
                        "date_histogram": {
                            "field": "date",
                            "calendar_interval": "1d",
                            "format": "yyyy-MM-dd"
                        }
                    }
                }
            }
            time_response = client.search(index=INDEX_NAME, body=time_query)
            tb = time_response.get("aggregations", {}).get("documents_over_time", {}).get("buckets", [])
            time_dist = [{"date": b["key_as_string"], "count": b["doc_count"]} for b in tb]

            return jsonify({
                "success": True,
                "total_documents": total_docs,
                "unique_locations": unique_locations_count,
                "top_georeferences": top_geo,
                "documents_over_time": time_dist
            })

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500