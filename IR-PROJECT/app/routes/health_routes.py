from flask import jsonify
from ..opensearch_client import client
from ..config import INDEX_NAME
from ..nlp import NLP_AVAILABLE

def register_health_routes(app):

    @app.route("/api/document/<doc_id>", methods=["GET"])
    def get_document(doc_id):
        try:
            doc = client.get(index=INDEX_NAME, id=doc_id)
            return jsonify({
                "success": True,
                "found": doc["found"],
                "document": doc["_source"]
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e),
                "found": False
            }), 404


    @app.route("/api/index/verify", methods=["GET"])
    def verify_index():
        try:
            count = client.count(index=INDEX_NAME)
            health = client.cluster.health(index=INDEX_NAME)

            return jsonify({
                "success": True,
                "document_count": count["count"],
                "index_health": health["status"],
                "shards": {
                    "total": health["active_shards"],
                    "primary": health["active_primary_shards"]
                },
                "message": "Index is stable" if count["count"] > 0 else "Index is empty"
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


    @app.route("/api/health", methods=["GET"])
    def health_check():
        try:
            info = client.info()
            return jsonify({
                "success": True,
                "opensearch": info,
                "nlp_available": NLP_AVAILABLE
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


    @app.route("/api/index/stats", methods=["GET"])
    def index_stats():
        try:
            if not client.indices.exists(index=INDEX_NAME):
                return jsonify({"success": False, "error": f"Index '{INDEX_NAME}' does not exist"}), 404

            stats = client.indices.stats(index=INDEX_NAME)
            count = client.count(index=INDEX_NAME)

            index_stats_data = stats.get("indices", {}).get(INDEX_NAME, {})
            total_stats = index_stats_data.get("total", {})
            store_stats = total_stats.get("store", {})

            return jsonify({
                "success": True,
                "document_count": count["count"],
                "index_size": store_stats.get("size_in_bytes", 0),
                "index_name": INDEX_NAME,
                "status": "ready" if count["count"] > 0 else "empty"
            })

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500