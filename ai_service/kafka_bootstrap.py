import os
import time
from typing import Dict, Any

from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

def _env(name: str, default: str) -> str:
    return os.getenv(name, default)

def get_env() -> str:
    return _env("ENV", "local").lower()

def _parse_topics() -> Dict[str, Dict[str, Any]]:
    """
    Topics configuration:
      - In local/dev/test we can create missing topics.
      - In preprod/prod we only validate (fail fast).
    Override partitions/replication via env vars if needed.
    """
    jobs_p = int(_env("KAFKA_PARTITIONS_JOBS", "6"))
    res_p  = int(_env("KAFKA_PARTITIONS_RESULTS", "6"))
    dlq_p  = int(_env("KAFKA_PARTITIONS_DLQ", "3"))

    repl = int(_env("KAFKA_REPLICATION_FACTOR", "1"))
    return {
        _env("KAFKA_TOPIC_JOBS", "ai.jobs"): {"partitions": jobs_p, "replication": repl},
        _env("KAFKA_TOPIC_RESULTS", "ai.results"): {"partitions": res_p, "replication": repl},
        _env("KAFKA_TOPIC_DLQ", "ai.dlq"): {"partitions": dlq_p, "replication": repl},
    }

def bootstrap_kafka(bootstrap_servers: str) -> None:
    env = get_env()
    topics_cfg = _parse_topics()

    admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers, client_id="ai-service-admin")
    try:
        existing = set(admin.list_topics())
        missing = [t for t in topics_cfg.keys() if t not in existing]

        if not missing:
            print(f"[kafka_bootstrap] all topics exist: {sorted(topics_cfg.keys())}")
            return

        if env in ("local", "dev", "test"):
            new_topics = [
                NewTopic(name=t,
                         num_partitions=topics_cfg[t]["partitions"],
                         replication_factor=topics_cfg[t]["replication"])
                for t in missing
            ]
            print(f"[kafka_bootstrap] creating topics in env={env}: {missing}")
            try:
                admin.create_topics(new_topics=new_topics, validate_only=False)
            except TopicAlreadyExistsError:
                pass

            # Wait a bit for metadata propagation
            time.sleep(1)
            print(f"[kafka_bootstrap] topics ready")
            return

        # preprod/prod: fail fast
        raise RuntimeError(
            f"Missing Kafka topics {missing} in env={env}. "
            f"Create them via infrastructure (Terraform/Helm/scripts) before starting the worker."
        )
    finally:
        try:
            admin.close()
        except Exception:
            pass
