"""
Create the golden benchmark dataset in Langfuse.
Run once: python labs/07-offline-evals/create_dataset.py
"""

import sys
from pathlib import Path

# Add project root to path so .env and app module can be found
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

from langfuse import get_client

langfuse = get_client()

DATASET_NAME = "datastream-support-benchmark"


test_cases = [

    {
        "input": {"question": "What is the price of the Pro plan?"},
        "expected_output": "$49/month with up to 50M events and 10 pipelines",
    },
    {
        "input": { "question": "What connectors does DataStream support?"},
        "expected_output": "50+ connectors including Kafka, PostgreSQL, MySQL, BigQuery, Snowflake, S3",
    },
    {
        "input": { "question": "I'm getting an AUTH_FAILED error, what should I do?"},
        "expected_output": "Verify your API keys and permissions in Settings > Credentials",
    },
    {
        "input": { "question": "How do I set up monitoring alerts?"},
        "expected_output": "Go to Settings > Alerts and configure triggers for error rate, pipeline lag, or pipeline stopped",
    },
    {
        "input": { "question": "Is DataStream GDPR compliant?"},
        "expected_output": "Yes, DataStream is SOC 2 Type II certified and GDPR compliant with AES-256 encryption at rest",
    },
    {
        "input": { "question": "What is the API rate limit on the Free plan?"},
        "expected_output": "100 requests per minute on the Free plan",
    },
    {
        "input": { "question": "How do I create a new pipeline?"},
        "expected_output": "Use the UI or CLI with: datastream init my-pipeline",
    },
    {
        "input": { "question": "What encryption does DataStream use?"},
        "expected_output": "TLS 1.3 for data in transit and AES-256 for data at rest",
    },
    {
        "input": { "question": "How many pipelines can I have on the Free plan?"},
        "expected_output": "1 pipeline on the Free plan",
    },
]

for case in test_cases:
    langfuse.create_dataset_item(
        dataset_name=DATASET_NAME,
        input=case["input"],
        expected_output=case["expected_output"],
    )
    print(f"  Added: {case['input']['question'][:60]}")

print(f"\nDataset '{DATASET_NAME}' created with {len(test_cases)} items.")
print(f"View in Langfuse: Datasets → {DATASET_NAME}")
