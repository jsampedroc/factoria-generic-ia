\
import os
import time
import uuid
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .pipeline import run_pipeline

import warnings
from pydantic.warnings import PydanticDeprecatedSince20

warnings.filterwarnings(
    "ignore",
    category=PydanticDeprecatedSince20
)

# Optional OpenTelemetry (safe fallback if not installed/configured)
def _setup_otel():
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        service_name = os.getenv("OTEL_SERVICE_NAME", "factoria-ai")
        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if not endpoint:
            return

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

        # Auto-instrument FastAPI if available
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
            # instrument after app creation
            return FastAPIInstrumentor
        except Exception:
            return
    except Exception:
        return

FastAPIInstrumentor = _setup_otel()

app = FastAPI(title="Factoria AI Service", version="1.0.0")

if FastAPIInstrumentor:
    FastAPIInstrumentor.instrument_app(app)

class AiRequest(BaseModel):
    caseId: str = Field(..., description="Business case identifier")
    task: str = Field("pipeline", description="Logical task name (reserved)")
    input: Dict[str, Any] = Field(default_factory=dict)
    traceId: Optional[str] = None
    promptVersion: Optional[str] = "v1"

class AiResponse(BaseModel):
    status: str
    approved: bool
    needsHumanApproval: bool
    riskScore: float
    result: Dict[str, Any]
    requirements: Dict[str, Any]
    compliance: Dict[str, Any]
    audit: Dict[str, Any]

@app.get("/health")
def health():
    return {"status": "UP"}

@app.get("/")
def root():
    return {"status": "ok", "service": "ai-api"}

@app.post("/ai/run", response_model=AiResponse)
def run(req: AiRequest):
    trace_id = req.traceId or str(uuid.uuid4())
    payload = req.model_dump()
    payload["traceId"] = trace_id

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
        return out
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
