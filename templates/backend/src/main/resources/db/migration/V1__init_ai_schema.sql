-- Extensiones útiles
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1) CASO
CREATE TABLE IF NOT EXISTS ai_case (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    text NULL,
  case_key     text NOT NULL,                -- tu "caseId" externo
  title        text NULL,
  domain       text NULL,
  constraints  jsonb NOT NULL DEFAULT '[]'::jsonb,
  context      jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_by   text NULL,
  created_at   timestamptz NOT NULL DEFAULT now(),
  updated_at   timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, case_key)
);

CREATE INDEX IF NOT EXISTS idx_ai_case_tenant ON ai_case (tenant_id);
CREATE INDEX IF NOT EXISTS idx_ai_case_domain ON ai_case (domain);

-- 2) RUN (una ejecución del pipeline)
CREATE TABLE IF NOT EXISTS ai_run (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id        text NULL,
  case_id          uuid NOT NULL REFERENCES ai_case(id) ON DELETE CASCADE,

  run_key          text NOT NULL,             -- id externo o correlación
  mode             text NOT NULL DEFAULT 'thorough',   -- fast|thorough
  prompt_version   text NOT NULL DEFAULT 'v1',

  status           text NOT NULL DEFAULT 'CREATED',
  risk_threshold   numeric NOT NULL DEFAULT 7.0,

  trace_id         text NULL,                 -- de audit/otel
  model            text NULL,
  temperature      numeric NULL,

  queued_at        timestamptz NULL,
  started_at       timestamptz NULL,
  finished_at      timestamptz NULL,

  latency_ms       bigint NULL,
  error_code       text NULL,
  error_message    text NULL,

  created_at       timestamptz NOT NULL DEFAULT now(),
  updated_at       timestamptz NOT NULL DEFAULT now(),

  UNIQUE (tenant_id, run_key)
);

CREATE INDEX IF NOT EXISTS idx_ai_run_case ON ai_run (case_id);
CREATE INDEX IF NOT EXISTS idx_ai_run_status ON ai_run (status);
CREATE INDEX IF NOT EXISTS idx_ai_run_tenant ON ai_run (tenant_id);

-- 3) RESULT (payloads grandes en JSONB)
CREATE TABLE IF NOT EXISTS ai_result (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       text NULL,
  run_id          uuid NOT NULL UNIQUE REFERENCES ai_run(id) ON DELETE CASCADE,

  approved        boolean NOT NULL DEFAULT false,
  needs_review    boolean NOT NULL DEFAULT false,
  risk_score      numeric NOT NULL DEFAULT 0,

  requirements    jsonb NOT NULL DEFAULT '{}'::jsonb,
  architecture    jsonb NOT NULL DEFAULT '{}'::jsonb,
  compliance      jsonb NOT NULL DEFAULT '{}'::jsonb,
  audit           jsonb NOT NULL DEFAULT '{}'::jsonb,

  created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ai_result_risk ON ai_result (risk_score);
CREATE INDEX IF NOT EXISTS idx_ai_result_tenant ON ai_result (tenant_id);

-- 4) APPROVAL (human-in-the-loop)
CREATE TABLE IF NOT EXISTS ai_approval (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       text NULL,
  run_id          uuid NOT NULL REFERENCES ai_run(id) ON DELETE CASCADE,

  decision       text NOT NULL,               -- APPROVE|REJECT
  decided_by     text NOT NULL,
  comment        text NULL,

  decided_at     timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ai_approval_run ON ai_approval (run_id);
CREATE INDEX IF NOT EXISTS idx_ai_approval_tenant ON ai_approval (tenant_id);