package com.industrialprofile.ai.api;

import com.industrialprofile.ai.domain.AiResult;
import com.industrialprofile.ai.service.AiResultService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/ai/results")
public class AiResultController {

    private final AiResultService service;

    public AiResultController(AiResultService service) {
        this.service = service;
    }

    @GetMapping("/{caseId}/latest")
    public ResponseEntity<AiResult> latest(@PathVariable String caseId) {
        return service.getLatest(caseId)
                .map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }
}
