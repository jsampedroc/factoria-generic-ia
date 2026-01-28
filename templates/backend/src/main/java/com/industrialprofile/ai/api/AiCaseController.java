package com.industrialprofile.ai.api;

import com.industrialprofile.ai.domain.AiCase;
import com.industrialprofile.ai.service.AiCaseService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/ai/cases")
public class AiCaseController {

    private final AiCaseService service;

    public AiCaseController(AiCaseService service) {
        this.service = service;
    }

    @PostMapping("/{caseId}")
    public AiCase create(@PathVariable String caseId) {
        return service.createCaseIfNotExists(caseId);
    }
}