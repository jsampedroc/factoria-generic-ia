# Factoria AI Service (CrewAI + DeepSeek) - HTTP + Kafka

## Arranque (solo HTTP)
1. Crea `.env` en la raíz (o exporta variables). Ejemplo: `ai_service/.env.example`
2. Levanta el servicio API:
   - `docker compose -f docker-compose.yml -f docker-compose.ai.yml up -d ai-api`

Prueba:
- `GET http://localhost:8000/health`
- `POST http://localhost:8000/ai/run`

## Arranque con Kafka (Redpanda) + Worker
- `docker compose -f docker-compose.yml -f docker-compose.ai.yml up -d redpanda ai-worker ai-api`

Publica un job (ejemplo con kcat):
- `echo '{"caseId":"CASE-1","task":"pipeline","promptVersion":"v1","input":{"domain":"industrial","constraints":["ISO 27001"]}}' | kcat -b localhost:9092 -t ai.jobs -P`

Consume resultados:
- `kcat -b localhost:9092 -t ai.results -C`

## Nota
- El pipeline devuelve siempre JSON validado (con retries configurables).
- `needsHumanApproval` se activa por riesgo alto o violaciones críticas.
