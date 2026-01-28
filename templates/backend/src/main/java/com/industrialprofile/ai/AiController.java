package com.industrialprofile.ai;

import com.industrialprofile.ai.service.AiOrchestrationService;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/api/ai")
public class AiController {

    private final AiOrchestrationService service;

    public AiController(AiOrchestrationService service) {
        this.service = service;
    }

    @PostMapping("/run")
    public ResponseEntity<?> run(@RequestBody AiJob job) {
        if (job.getCaseId() == null || job.getCaseId().isBlank()) {
            job.setCaseId("CASE-" + UUID.randomUUID());
        }
        if (job.getTraceId() == null || job.getTraceId().isBlank()) {
            job.setTraceId(UUID.randomUUID().toString());
        }
        if (job.getTask() == null || job.getTask().isBlank()) {
            job.setTask("pipeline");
        }
        if (job.getPromptVersion() == null || job.getPromptVersion().isBlank()) {
            job.setPromptVersion("v1");
        }
        return ResponseEntity.ok(service.run(job));
    }
}
