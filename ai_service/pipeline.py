import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from dotenv import load_dotenv
from jsonschema import validate as js_validate, ValidationError

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

from .prompts import load_prompt

# Grounding / RAG
from ai.llm.grounding import build_grounded_prompt
from ai.llm.policies import DEFAULT_SYSTEM_RULES
from ai.rag.retriever import retrieve_context


load_dotenv()

# ----------------------------
# Feature flags (env-driven)
# ----------------------------
def env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "y", "on")

FEATURE_STRICT_JSON = env_bool("FEATURE_STRICT_JSON", True)
FEATURE_RETRY_ON_INVALID_JSON = env_bool("FEATURE_RETRY_ON_INVALID_JSON", True)
FEATURE_REQUIRE_HUMAN_APPROVAL = env_bool("FEATURE_REQUIRE_HUMAN_APPROVAL", True)

# ----------------------------
# DeepSeek via OpenAI-compatible API (langchain-openai)
# ----------------------------
def build_llm() -> ChatOpenAI:
    model = os.getenv("AI_MODEL", "deepseek-chat")
    base_url = os.getenv("AI_BASE_URL", "https://api.deepseek.com")
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing DEEPSEEK_API_KEY (or OPENAI_API_KEY).")
    temperature = float(os.getenv("AI_TEMPERATURE", "0.1"))
    max_tokens = int(os.getenv("AI_MAX_TOKENS", "4000"))
    return ChatOpenAI(
        model=model,
        base_url=base_url,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )

# ----------------------------
# Schemas (validate outputs)
# ----------------------------
REQUIREMENTS_SCHEMA = {
    "type": "object",
    "required": [
        "domain",
        "business_objectives",
        "functional_requirements",
        "non_functional_requirements",
        "constraints",
        "assumptions",
        "open_questions",
    ],
    "properties": {
        "domain": {"type": "string"},
        "business_objectives": {"type": "array", "items": {"type": "string"}},
        "functional_requirements": {"type": "array", "items": {"type": "string"}},
        "non_functional_requirements": {"type": "array", "items": {"type": "string"}},
        "constraints": {"type": "array", "items": {"type": "string"}},
        "assumptions": {"type": "array", "items": {"type": "string"}},
        "open_questions": {"type": "array", "items": {"type": "string"}},
    },
    "additionalProperties": True,
}

ARCHITECTURE_SCHEMA = {
    "type": "object",
    "required": [
        "architecture_overview",
        "components",
        "data_model",
        "apis",
        "security",
        "operability",
        "assumptions",
        "risks",
    ],
    "properties": {
        "architecture_overview": {"type": "string"},
        "components": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "responsibility", "tech", "interfaces"],
                "properties": {
                    "name": {"type": "string"},
                    "responsibility": {"type": "string"},
                    "tech": {"type": "string"},
                    "interfaces": {"type": "array", "items": {"type": "string"}},
                },
                "additionalProperties": True,
            },
        },
        "data_model": {
            "type": "object",
            "required": ["entities", "notes"],
            "properties": {
                "entities": {"type": "array", "items": {"type": "string"}},
                "notes": {"type": "string"},
            },
            "additionalProperties": True,
        },
        "apis": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "method", "path", "request", "response"],
                "properties": {
                    "name": {"type": "string"},
                    "method": {"type": "string"},
                    "path": {"type": "string"},
                    "request": {"type": "string"},
                    "response": {"type": "string"},
                },
                "additionalProperties": True,
            },
        },
        "security": {"type": "object"},
        "operability": {"type": "object"},
        "assumptions": {"type": "array", "items": {"type": "string"}},
        "risks": {"type": "array", "items": {"type": "string"}},
    },
    "additionalProperties": True,
}

COMPLIANCE_SCHEMA = {
    "type": "object",
    "required": [
        "approved",
        "needsHumanApproval",
        "riskScore",
        "violations",
        "risks",
        "recommendations",
        "reasonCodes",
    ],
    "properties": {
        "approved": {"type": "boolean"},
        "needsHumanApproval": {"type": "boolean"},
        "riskScore": {"type": "number"},
        "violations": {"type": "array", "items": {"type": "string"}},
        "risks": {"type": "array", "items": {"type": "string"}},
        "recommendations": {"type": "array", "items": {"type": "string"}},
        "reasonCodes": {"type": "array", "items": {"type": "string"}},
    },
    "additionalProperties": True,
}

# ----------------------------
# Helpers
# ----------------------------
def _parse_json_maybe(text: Any) -> Dict[str, Any]:
    """
    CrewAI may return a string. We accept dict too.
    """
    if isinstance(text, dict):
        return text
    if not isinstance(text, str):
        raise ValueError("Expected string or dict result.")
    # Trim code fences if any
    s = text.strip()
    if s.startswith("```"):
        s = s.strip("`")
        # Try to remove language marker
        s = s.split("\n", 1)[-1].strip()
    # Extract first JSON object if extra text exists
    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end != -1 and end > start:
        s = s[start : end + 1]
    return json.loads(s)

def _validate(schema: Dict[str, Any], data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    try:
        js_validate(instance=data, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)

def _run_task_with_retry(crew: Crew, schema: Dict[str, Any], max_retries: int = 2) -> Dict[str, Any]:
    last_err = None
    for attempt in range(max_retries + 1):
        out = crew.kickoff()
        try:
            normalized = normalize_crew_output(out)
            data = _parse_json_maybe(normalized)
        except Exception as e:
            last_err = f"parse_error: {e}"
            data = None
        if data is not None and FEATURE_STRICT_JSON:
            ok, err = _validate(schema, data)
            if ok:
                return data
            last_err = f"schema_error: {err}"
        elif data is not None:
            return data

        if not FEATURE_RETRY_ON_INVALID_JSON:
            break
        # small backoff
        time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"Invalid output after retries. last_err={last_err}")

@dataclass
class PipelineResult:
    status: str
    approved: bool
    needsHumanApproval: bool
    riskScore: float
    result: Dict[str, Any]
    requirements: Dict[str, Any]
    compliance: Dict[str, Any]
    audit: Dict[str, Any]

# ----------------------------
# Public pipeline
# ----------------------------
def run_pipeline(payload: Dict[str, Any]) -> PipelineResult:
    """
    payload:
      caseId: str
      traceId: str (optional)
      promptVersion: str (optional) -> e.g. "v1"
      input: dict (business input)
    """
    llm = build_llm()
    prompt_version = payload.get("promptVersion", "v1")

    # Agents (LLM is shared)
    requirements_analyst = Agent(
        role="Requirements Analyst",
        goal="Extraer requerimientos empresariales de forma estructurada",
        backstory="Analista senior con enfoque en trazabilidad y especificación.",
        llm=llm,
        verbose=False,
    )
    solution_architect = Agent(
        role="Solution Architect",
        goal="Diseñar solución técnica enterprise basada en requerimientos",
        backstory="Arquitecto senior Java/Spring/Angular con enfoque en operabilidad.",
        llm=llm,
        verbose=False,
    )
    policy_guard = Agent(
        role="Policy & Compliance Agent",
        goal="Validar cumplimiento, riesgos y restricciones. No propone soluciones nuevas.",
        backstory="Experto en seguridad, privacidad y compliance.",
        llm=llm,
        verbose=False,
    )


    verifier = Agent(
        role="Verifier",
        goal="Detectar alucinaciones y afirmaciones no verificadas",
        backstory=(
            "Eres un auditor estricto. No generas contenido nuevo. "
            "Solo verificas si las afirmaciones están soportadas por el CONTEXTO."
        ),
        llm=llm,
        verbose=False,
    )

    # Tasks (JSON-only via prompt templates)
    req_prompt = load_prompt(f"requirements_{prompt_version}.md")
    arch_prompt = load_prompt(f"architecture_{prompt_version}.md")
    comp_prompt = load_prompt(f"compliance_{prompt_version}.md")

    business_input = payload.get("input", {})

    # ----------------------------
    # REQUIREMENTS (GROUNDING + RAG + SELF-CHECK)
    # ----------------------------
    rag_chunks = retrieve_context(json.dumps(business_input, ensure_ascii=False))

    context_blocks = [
        json.dumps(business_input, ensure_ascii=False),
        *[c.get("text", "") for c in rag_chunks],
    ]

    grounded_req_prompt = build_grounded_prompt(
        system_rules=DEFAULT_SYSTEM_RULES,
        context_blocks=context_blocks,
        task_prompt=req_prompt,
        output_contract=json.dumps(REQUIREMENTS_SCHEMA, ensure_ascii=False),
    )

    req_task = Task(
        description=grounded_req_prompt,
        agent=requirements_analyst,
        expected_output="JSON",
    )

    req_crew = Crew(agents=[requirements_analyst], tasks=[req_task], process=Process.sequential)
    requirements = _run_task_with_retry(req_crew, REQUIREMENTS_SCHEMA)

    # Self-check (blocking): verify groundedness of requirements output
    verify_task = Task(
        description=(
            "Verifica que el JSON de REQUIREMENTS solo contiene afirmaciones soportadas por CONTEXT. "
            "Si algo no está soportado, marca pass=false y añade fix_instructions.\n\n"
            f"REQUIREMENTS_OUTPUT:\n{json.dumps(requirements, ensure_ascii=False)}\n\n"
            f"CONTEXT:\n{json.dumps(context_blocks, ensure_ascii=False)}"
        ),
        agent=verifier,
        expected_output="JSON",
    )

    verify_crew = Crew(agents=[verifier], tasks=[verify_task], process=Process.sequential)
    verification = _run_task_with_retry(
        verify_crew,
        {
            "type": "object",
            "required": ["pass", "unverified_claims", "issues", "fix_instructions"],
            "properties": {
                "pass": {"type": "boolean"},
                "unverified_claims": {"type": "array", "items": {"type": "string"}},
                "issues": {"type": "array", "items": {"type": "string"}},
                "fix_instructions": {"type": "array", "items": {"type": "string"}},
            },
            "additionalProperties": True,
        },
    )

    if not verification.get("pass", False):
        raise RuntimeError(f"Requirements verification failed: {verification}")

    arch_task = Task(
        description=arch_prompt + "\n\nREQUIREMENTS (JSON):\n" + json.dumps(requirements, ensure_ascii=False),
        agent=solution_architect,
        expected_output="JSON",
    )
    arch_crew = Crew(agents=[solution_architect], tasks=[arch_task], process=Process.sequential)
    architecture = _run_task_with_retry(arch_crew, ARCHITECTURE_SCHEMA)

    comp_task = Task(
        description=comp_prompt
        + "\n\nREQUIREMENTS (JSON):\n"
        + json.dumps(requirements, ensure_ascii=False)
        + "\n\nSOLUTION (JSON):\n"
        + json.dumps(architecture, ensure_ascii=False),
        agent=policy_guard,
        expected_output="JSON",
    )
    comp_crew = Crew(agents=[policy_guard], tasks=[comp_task], process=Process.sequential)
    compliance = _run_task_with_retry(comp_crew, COMPLIANCE_SCHEMA)

    approved = bool(compliance.get("approved", False))
    needs_human = bool(compliance.get("needsHumanApproval", False))
    risk_score = float(compliance.get("riskScore", 0.0))

    # Enforce human approval if feature flag says so and risk score high
    if FEATURE_REQUIRE_HUMAN_APPROVAL and risk_score >= 7:
        needs_human = True

    audit = {
        "model": os.getenv("AI_MODEL", "deepseek-chat"),
        "temperature": float(os.getenv("AI_TEMPERATURE", "0.1")),
        "promptVersion": prompt_version,
        "traceId": payload.get("traceId"),
        "caseId": payload.get("caseId"),
    }

    return PipelineResult(
        status="OK",
        approved=approved,
        needsHumanApproval=needs_human,
        riskScore=risk_score,
        result=architecture,
        requirements=requirements,
        compliance=compliance,
        audit=audit,
    )

def normalize_crew_output(result):
    """
    Convierte la salida de CrewAI en algo parseable (str o dict).
    Esta versión es robusta frente a cambios internos de CrewAI.
    """
    # Caso 1: ya es dict
    if isinstance(result, dict):
        return result

    # Caso 2: texto plano
    if isinstance(result, str):
        return result

    # Caso 3: objetos CrewAI con raw_output
    if hasattr(result, "raw_output") and result.raw_output:
        return result.raw_output

    # Caso 4: objetos CrewAI con tasks_output
    if hasattr(result, "tasks_output") and result.tasks_output:
        for t in reversed(result.tasks_output):
            if hasattr(t, "raw_output") and t.raw_output:
                return t.raw_output

    # 🔴 CASO CLAVE: fallback universal
    try:
        text = str(result)
        if text:
            return text
    except Exception:
        pass

    raise ValueError(f"Unsupported CrewAI output type: {type(result)}")