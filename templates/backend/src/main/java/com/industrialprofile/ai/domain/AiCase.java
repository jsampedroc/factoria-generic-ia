package com.industrialprofile.ai.domain;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "ai_cases", schema = "shared")
public class AiCase {

    @Id
    @GeneratedValue
    private UUID id;

    @Column(nullable = false, unique = true)
    private String caseId;

    @Column(nullable = false)
    private String status;

    @Column(nullable = false)
    private boolean approved;

    @Column(nullable = false)
    private boolean needsHumanApproval;

    @Column(nullable = false)
    private int riskScore;

    @Column(nullable = false, updatable = false)
    private Instant createdAt;

    protected AiCase() {
        // JPA
    }

    public AiCase(String caseId) {
        this.caseId = caseId;
        this.status = "CREATED";
        this.createdAt = Instant.now();
    }

    @PrePersist
    void onCreate() {
        if (createdAt == null) {
            createdAt = Instant.now();
        }
    }

    // getters y setters (puedes usar Lombok si quieres luego)
    public UUID getId() { return id; }
    public String getCaseId() { return caseId; }
    public String getStatus() { return status; }
    public boolean isApproved() { return approved; }
    public boolean isNeedsHumanApproval() { return needsHumanApproval; }
    public int getRiskScore() { return riskScore; }
    public Instant getCreatedAt() { return createdAt; }

    public void updateResult(boolean approved, boolean needsHumanApproval, int riskScore) {
        this.approved = approved;
        this.needsHumanApproval = needsHumanApproval;
        this.riskScore = riskScore;
        this.status = "COMPLETED";
    }
}