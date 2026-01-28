\
import json
import os
import time
import uuid
from typing import Any, Dict

from kafka import KafkaConsumer, KafkaProducer

from .pipeline import run_pipeline
from .kafka_bootstrap import bootstrap_kafka

def _env(name: str, default: str) -> str:
    return os.getenv(name, default)

BOOTSTRAP = _env("KAFKA_BOOTSTRAP", "redpanda:9092")
TOPIC_JOBS = _env("KAFKA_TOPIC_JOBS", "ai.jobs")
TOPIC_RESULTS = _env("KAFKA_TOPIC_RESULTS", "ai.results")
TOPIC_DLQ = _env("KAFKA_TOPIC_DLQ", "ai.dlq")
GROUP_ID = _env("KAFKA_GROUP_ID", "ai-workers")

def main():
    bootstrap_kafka(BOOTSTRAP)

    consumer = KafkaConsumer(
        TOPIC_JOBS,
        bootstrap_servers=BOOTSTRAP,
        group_id=GROUP_ID,
        enable_auto_commit=True,
        auto_offset_reset="earliest",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        key_deserializer=lambda v: v.decode("utf-8") if v else None,
    )

    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
        key_serializer=lambda v: v.encode("utf-8") if isinstance(v, str) else v,
    )

    print(f"[kafka_worker] listening on {BOOTSTRAP} topic={TOPIC_JOBS} group={GROUP_ID}")
    for msg in consumer:
        key = msg.key or (msg.value.get("caseId") if isinstance(msg.value, dict) else None) or str(uuid.uuid4())
        payload: Dict[str, Any] = msg.value
        payload.setdefault("traceId", str(uuid.uuid4()))
        payload.setdefault("promptVersion", "v1")
        t0 = time.time()
        try:
            pr = run_pipeline(payload)
            out = {
                "status": pr.status,
                "approved": pr.approved,
                "needsHumanApproval": pr.needsHumanApproval,
                "riskScore": pr.riskScore,
                "result": pr.result,
                "requirements": pr.requirements,
                "compliance": pr.compliance,
                "audit": {**pr.audit, "latencyMs": int((time.time() - t0) * 1000)},
            }
            producer.send(TOPIC_RESULTS, key=key, value=out)
            producer.flush()
        except Exception as e:
            dlq = {
                "error": str(e),
                "original": payload,
                "ts": int(time.time()),
            }
            producer.send(TOPIC_DLQ, key=key, value=dlq)
            producer.flush()

if __name__ == "__main__":
    main()
