"""
Simple in-memory knowledge base for the DataStream support assistant.
In a real application this would be a vector database with embeddings.
"""

DOCS = [
    {
        "id": "gs-001",
        "title": "Getting Started with DataStream",
        "content": (
            "DataStream is a real-time data pipeline platform. To get started: "
            "1) Create an account at app.datastream.io. "
            "2) Install the CLI: pip install datastream-cli. "
            "3) Authenticate with: datastream login. "
            "4) Create your first pipeline with: datastream init my-pipeline."
        ),
        "tags": ["getting started", "install", "setup", "cli"],
    },
    {
        "id": "pricing-001",
        "title": "Pricing & Plans",
        "content": (
            "DataStream offers three plans: "
            "Free (up to 1M events/month, 1 pipeline), "
            "Pro ($49/month, up to 50M events, 10 pipelines, priority support), "
            "Enterprise (custom pricing, unlimited everything, SLA guarantee, dedicated support)."
        ),
        "tags": ["pricing", "plans", "billing", "cost"],
    },
    {
        "id": "pipelines-001",
        "title": "Creating and Managing Pipelines",
        "content": (
            "Pipelines in DataStream define how data flows from sources to destinations. "
            "Use the UI or CLI to create pipelines. Each pipeline has: a source connector, "
            "optional transformation steps, and one or more destination connectors. "
            "Pipelines can be paused, resumed, or deleted from the dashboard."
        ),
        "tags": ["pipelines", "create", "manage", "connectors"],
    },
    {
        "id": "connectors-001",
        "title": "Available Connectors",
        "content": (
            "DataStream supports 50+ connectors. Popular sources: Kafka, PostgreSQL, MySQL, "
            "S3, HTTP webhooks, Stripe, Salesforce. Popular destinations: BigQuery, Snowflake, "
            "Redshift, Elasticsearch, S3, Slack, PagerDuty. "
            "Custom connectors can be built using the DataStream SDK."
        ),
        "tags": ["connectors", "integrations", "kafka", "postgres", "bigquery", "snowflake"],
    },
    {
        "id": "errors-001",
        "title": "Troubleshooting & Common Errors",
        "content": (
            "Common issues and solutions: "
            "CONNECTION_REFUSED - check firewall rules and that the source service is running. "
            "AUTH_FAILED - verify your API keys and permissions in Settings > Credentials. "
            "RATE_LIMITED - you have exceeded your plan's event quota; upgrade or wait for reset. "
            "SCHEMA_MISMATCH - your source schema changed; update the pipeline schema in the UI."
        ),
        "tags": ["errors", "troubleshooting", "connection", "auth", "rate limit"],
    },
    {
        "id": "api-001",
        "title": "DataStream REST API",
        "content": (
            "The DataStream REST API is available at https://api.datastream.io/v2. "
            "Authentication uses Bearer tokens (generate in Settings > API Keys). "
            "Key endpoints: GET /pipelines, POST /pipelines, GET /pipelines/{id}/status, "
            "POST /pipelines/{id}/pause, POST /pipelines/{id}/resume. "
            "Rate limit: 1000 requests/minute on Pro, 100/minute on Free."
        ),
        "tags": ["api", "rest", "authentication", "endpoints"],
    },
    {
        "id": "monitoring-001",
        "title": "Monitoring & Alerts",
        "content": (
            "DataStream provides real-time monitoring for all pipelines. "
            "View throughput, latency, and error rates in the Monitoring dashboard. "
            "Set up alerts via Settings > Alerts: trigger on error rate > threshold, "
            "pipeline lag > N seconds, or pipeline stopped. "
            "Alerts can be sent to Slack, PagerDuty, email, or webhooks."
        ),
        "tags": ["monitoring", "alerts", "metrics", "throughput", "latency"],
    },
    {
        "id": "security-001",
        "title": "Security & Compliance",
        "content": (
            "DataStream is SOC 2 Type II certified and GDPR compliant. "
            "All data in transit is encrypted with TLS 1.3. Data at rest uses AES-256 encryption. "
            "Enterprise plans include: SSO/SAML, IP allowlisting, audit logs, "
            "data residency options (US, EU, APAC), and BAA for HIPAA compliance."
        ),
        "tags": ["security", "compliance", "gdpr", "soc2", "hipaa", "encryption"],
    },
]


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """
    Retrieve relevant docs for a query using simple keyword matching.
    Returns up to top_k results sorted by relevance score.
    """
    query_terms = set(query.lower().split())
    scored = []

    for doc in DOCS:
        score = 0
        searchable = (doc["title"] + " " + doc["content"] + " " + " ".join(doc["tags"])).lower()
        for term in query_terms:
            if term in searchable:
                score += 1
        if score > 0:
            scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:top_k]]


def format_context(docs: list[dict]) -> str:
    """Format retrieved docs into a context string for the prompt."""
    if not docs:
        return "No relevant documentation found."
    parts = []
    for doc in docs:
        parts.append(f"[{doc['title']}]\n{doc['content']}")
    return "\n\n".join(parts)
