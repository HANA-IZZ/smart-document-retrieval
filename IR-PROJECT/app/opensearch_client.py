from opensearchpy import OpenSearch
from .config import OPENSEARCH_HOST, OPENSEARCH_PORT

client = OpenSearch(
    hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
    http_auth=None,
    use_ssl=False,
    verify_certs=False,
    ssl_show_warn=False
)