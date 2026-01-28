# Factoria IA (HTTP + Kafka) – Prueba rápida y guía de producción

Este repo incluye:
- **Backend Spring Boot** (control del negocio / seguridad / auditoría)
- **Servicio IA (Python)** con **CrewAI + DeepSeek**
- **Kafka (Redpanda en local)** para ejecución asíncrona + DLQ
- Modo **dual**: **HTTP** (sync) y **Kafka** (async) usando el **mismo pipeline** IA

---

## Requisitos

### Local (prueba rápida)
- Docker + Docker Compose
- Clave API de DeepSeek

### Producción (recomendado)
- Kubernetes (o similar) + registry de contenedores
- Kafka gestionado (Redpanda/Confluent/MSK/…)
- Observabilidad (OTLP collector, Grafana/Tempo/Jaeger opcional)

---

## Variables de entorno (mínimas)

Crea un `.env` (o exporta variables):

- `DEEPSEEK_API_KEY=...`
- `ENV=local`  (en prod debe ser `prod`)
- (Opcional) `OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317`

Kafka (defaults razonables):
- `KAFKA_BOOTSTRAP=redpanda:9092`
- `KAFKA_TOPIC_JOBS=ai.jobs`
- `KAFKA_TOPIC_RESULTS=ai.results`
- `KAFKA_TOPIC_DLQ=ai.dlq`

---

## Arranque en local (HTTP + Kafka)

Arranca todo (DB + backend + frontend + redpanda + ai-api + ai-worker):

```bash
docker compose -f docker-compose.yml -f docker-compose.ai.yml up -d --build
```

Comprueba salud:
- Servicio IA: `GET http://localhost:8000/health`

> En `ENV=local` el worker **crea automáticamente** los topics si faltan.

---

## Probar por HTTP (directo contra el servicio IA)

```bash
curl -X POST http://localhost:8000/ai/run \
  -H "Content-Type: application/json" \
  -d '{
    "caseId":"CASE-1",
    "task":"pipeline",
    "promptVersion":"v1",
    "input":{"domain":"industrial","constraints":["ISO 27001","multi-tenant"]}
  }'
```

Respuesta típica:
- `approved`
- `needsHumanApproval`
- `riskScore`
- `requirements`, `result`, `compliance`
- `audit`

---

## Probar por Kafka (async)

1) Publica un job en `ai.jobs`.
2) El worker consume y publica el resultado en `ai.results` o el error en `ai.dlq`.

Si usas Redpanda, lo más cómodo es entrar al contenedor y usar `rpk` (si lo habilitas),
o usar cualquier cliente Kafka (kcat, kafkacat, librerías).

---

## Backend Spring Boot: cómo usar HTTP vs Kafka

El backend debe elegir el modo con feature flag:
- `features.ai.mode=http`  → llama al servicio IA por HTTP y devuelve respuesta sincrónica
- `features.ai.mode=kafka` → publica el job en Kafka y devuelve `202 Accepted`

### Propiedades sugeridas (application.properties)
- `features.ai.mode=kafka`
- `features.ai.requireHumanApproval=true`
- `ai.http.baseUrl=http://ai-api:8000`
- `spring.kafka.bootstrap-servers=redpanda:9092`

---

# Puesta en producción (checklist)

## 1) Separación de responsabilidades
- **Spring Boot** manda (RBAC, reglas, auditoría).
- **Servicio IA** propone/valida, devuelve JSON.
- **Nunca** permitas que el LLM ejecute acciones críticas directamente.

## 2) Kafka topics (PROD)
En `ENV=prod` el worker **NO crea topics**. Solo valida y si faltan -> **no arranca** (fail fast).
Crea los topics mediante infraestructura (Terraform/Helm/scripts) con parámetros explícitos:
- `ai.jobs` (p.ej. 6 particiones, RF=3)
- `ai.results` (6, RF=3)
- `ai.dlq` (3, RF=3)

## 3) Secretos
- `DEEPSEEK_API_KEY` en Secret Manager (K8s Secret / Vault).
- Nunca en imagen ni en repo.

## 4) Observabilidad
- Propaga `traceId` y `caseId` en logs y mensajes Kafka.
- Exporta OTLP a un collector si lo tienes.

## 5) Seguridad
- Egress controlado (solo DeepSeek endpoint).
- Rate limiting por tenant/usuario en Spring.
- Sanitización: PII fuera del prompt; usa IDs.

## 6) Deploy
- Construye imágenes y empuja a registry.
- Despliega `ai-api` y `ai-worker` como deployments separados.
- Configura autoscaling del worker por lag/CPU.

---

## Estructura del servicio IA

- `ai_service/pipeline.py` → pipeline único
- `ai_service/api.py` → HTTP
- `ai_service/kafka_worker.py` → Kafka consumer/producer
- `ai_service/kafka_bootstrap.py` → create topics (solo local/dev/test) o validar (prod)
- `ai_service/prompts/` → prompts versionados
# factoria-generic-ia
