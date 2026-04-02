from app import create_app
from app.config import OPENSEARCH_HOST, OPENSEARCH_PORT, INDEX_NAME
from app.nlp import NLP_AVAILABLE

app = create_app()

if __name__ == "__main__":
    print("=" * 60)
    print("Smart Document Retrieval System")
    print("=" * 60)
    print(f"OpenSearch: {OPENSEARCH_HOST}:{OPENSEARCH_PORT}")
    print(f"Index: {INDEX_NAME}")
    print(f"NLP Available: {NLP_AVAILABLE}")
    print(f"Auto-location extraction: {'Enabled' if NLP_AVAILABLE else 'Disabled'}")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)