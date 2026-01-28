package com.industrialprofile.ai.service;

import java.util.Optional;

import org.springframework.stereotype.Service;

import com.industrialprofile.ai.domain.AiResult;
import com.industrialprofile.ai.repository.AiResultRepository;

import jakarta.transaction.Transactional;

@Service
public class AiResultService {

    private final AiResultRepository repository;

    public AiResultService(AiResultRepository repository) {
        this.repository = repository;
    }

    public Optional<AiResult> getLatest(String caseId) {
        return repository.findTopByCaseIdOrderByCreatedAtDesc(caseId);
    }
    
    @Transactional
    public void saveResult(
            String caseId,
            boolean approved,
            boolean needsHumanApproval,
            int riskScore
    ) {
        AiResult result = AiResult.create(
                caseId,
                approved,
                needsHumanApproval,
                riskScore
        );

        repository.save(result);
    }
}
