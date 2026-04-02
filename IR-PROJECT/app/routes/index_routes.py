from pathlib import Path
from flask import request, jsonify
from opensearchpy import helpers
from ..opensearch_client import client
from ..config import INDEX_NAME
from ..dates import ensure_document_has_date
from ..geo import ensure_document_has_location
from ..reuters_parser import parse_sgm_file

def register_index_routes(app):

    @app.route("/api/index/document", methods=["POST"])
    def index_document():
        try:
            document = request.json or {}

            document = ensure_document_has_date(document)
            document = ensure_document_has_location(document, do_geocode=True, geo_limit=1)

            response = client.index(
                index=INDEX_NAME,
                body=document,
                refresh="wait_for"
            )

            doc_id = response["_id"]
            verify = client.get(index=INDEX_NAME, id=doc_id)

            return jsonify({
                "success": True,
                "message": "Document indexed successfully and persisted",
                "document_id": doc_id,
                "georeferences": document.get("georeferences", []),
                "geo_points": document.get("geo_points", []),
                "geopoint": document.get("geopoint"),
                "date": document.get("date"),
                "extracted_dates": document.get("extracted_dates", []),
                "location_source": document.get("location_source", "manual"),
                "verified": verify["found"]
            }), 201

        except Exception as e:
            import traceback
            return jsonify({
                "success": False,
                "error": str(e),
                "trace": traceback.format_exc()
            }), 500

    @app.route('/api/index/reuters', methods=['POST'])
    def index_reuters_files():
        try:
            reuters_dir = Path("database")

            if not reuters_dir.exists():
                return jsonify({"success": False, "error": f"Directory '{reuters_dir}' not found"}), 404

            sgm_files = list(reuters_dir.rglob(".sgm")) + list(reuters_dir.rglob(".SGM"))
            sgm_files = list(dict.fromkeys(sgm_files))

            if not sgm_files:
                return jsonify({
                    "success": False,
                    "error": "No .sgm/.SGM files found",
                    "searched_in": str(reuters_dir.resolve())
                }), 404

            batch_size = 1000
            total_indexed = 0
            total_failed = 0
            total_docs_found = 0
            debug_first_files = []

            for fp in sgm_files:
                docs = parse_sgm_file(fp)

                if len(debug_first_files) < 5:
                    debug_first_files.append({
                        "file": fp.name,
                        "docs_parsed": len(docs)
                    })

                if not docs:
                    continue

                total_docs_found += len(docs)

                for i in range(0, len(docs), batch_size):
                    chunk = docs[i:i+batch_size]
                    actions = [{"_index": INDEX_NAME, "_source": d} for d in chunk]

                    success, failed = helpers.bulk(
                        client,
                        actions,
                        raise_on_error=False,
                        refresh=False
                    )

                    total_indexed += success
                    total_failed += (len(failed) if isinstance(failed, list) else int(failed))

            client.indices.refresh(index=INDEX_NAME)
            count = client.count(index=INDEX_NAME)

            return jsonify({
                "success": True,
                "searched_in": str(reuters_dir.resolve()),
                "files_found": len(sgm_files),
                "debug_first_files": debug_first_files,
                "documents_found": total_docs_found,
                "documents_indexed": total_indexed,
                "failed": total_failed,
                "total_in_index": count["count"]
            })

        except Exception as e:
            import traceback
            return jsonify({"success": False, "error": str(e), "trace": traceback.format_exc()}), 500