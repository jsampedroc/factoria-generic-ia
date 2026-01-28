package com.industrialprofile.ai;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

/**
 * Cliente HTTP sencillo para invocar el ai-api (FastAPI) desde el backend.
 *
 * Evitamos WebClient (spring-webflux) para mantener el stack MVC (spring-boot-starter-web)
 * y reducir dependencias/reactividad.
 */
@Component
public class CrewAiHttpClient {

    private final RestClient rest;
    private final Duration timeout;

    public CrewAiHttpClient(
            RestClient.Builder builder,
            @Value("${ai.api.base-url:http://factoria-ai-api:8000}") String baseUrl,
            @Value("${ai.api.timeout-seconds:120}") long timeoutSeconds
    ) {
        this.rest = builder.baseUrl(baseUrl).build();
        this.timeout = Duration.ofSeconds(timeoutSeconds);
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> runPipeline(Map<String, Object> request) {
        // RestClient usa el mismo ObjectMapper que Spring MVC.
        return rest
                .post()
                .uri("/ai/run")
                .contentType(MediaType.APPLICATION_JSON)
                .body(request)
                .retrieve()
                .body(Map.class);
    }

    /**
     * Alias de compatibilidad: algunas clases esperan un método run(AiJob).
     * Construye el payload esperado por el ai-api.
     */
    public Map<String, Object> run(AiJob job) {
        Map<String, Object> payload = new HashMap<>();
        payload.put("caseId", job.getCaseId());
        if (job.getTask() != null) payload.put("task", job.getTask());
        if (job.getPromptVersion() != null) payload.put("promptVersion", job.getPromptVersion());
        if (job.getInput() != null) payload.put("input", job.getInput());
        return runPipeline(payload);
    }
}
