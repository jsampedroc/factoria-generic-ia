package com.industrialprofile.ai.domain;

import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.UUID;

import jakarta.persistence.Column;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Table(name = "ai_result")
@Data
@AllArgsConstructor
public class AiResult {

    @Id
    @GeneratedValue
    private UUID id;

    @Column(name = "run_id", nullable = false)
    private UUID runId;

    @Column(nullable = false)
    private String caseId;

    private boolean approved;

    private boolean needsHumanApproval;

    private int riskScore;

    private OffsetDateTime createdAt;

    protected AiResult() {
        // JPA
    }

    public static AiResult create(
            String caseId,
            boolean approved,
            boolean needsHumanApproval,
            int riskScore
    ) {
        AiResult r = new AiResult();
        r.runId = UUID.randomUUID();   
        r.caseId = caseId;
        r.approved = approved;
        r.needsHumanApproval = needsHumanApproval;
        r.riskScore = riskScore;
        r.createdAt = OffsetDateTime.now();
        return r;
    }

    // getters/setters si los usas
}