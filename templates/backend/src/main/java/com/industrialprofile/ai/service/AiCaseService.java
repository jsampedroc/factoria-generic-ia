package com.industrialprofile.ai.service;

import com.industrialprofile.ai.domain.AiCase;
import com.industrialprofile.ai.repository.AiCaseRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AiCaseService {

    private final AiCaseRepository repository;

    public AiCaseService(AiCaseRepository repository) {
        this.repository = repository;
    }

    @Transactional
    public AiCase createCaseIfNotExists(String caseId) {
        return repository.findByCaseId(caseId)
                .orElseGet(() -> repository.save(new AiCase(caseId)));
    }

    @Transactional
    public void updateResult(
            String caseId,
            boolean approved,
            boolean needsHumanApproval,
            int riskScore
    ) {
        AiCase aiCase = repository.findByCaseId(caseId)
                .orElseThrow(() -> new IllegalStateException("Case not found: " + caseId));

        aiCase.updateResult(approved, needsHumanApproval, riskScore);
    }

    /**
     * Compatibilidad con versiones previas del Consumer.
     */
    public void applyResult(String caseId, boolean approved, boolean needsHumanApproval, int riskScore) {
        updateResult(caseId, approved, needsHumanApproval, riskScore);
    }
}