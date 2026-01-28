package com.industrialprofile.ai.messaging.dto;

public class AiResultMessage {

    private String caseId;
    private boolean approved;
    private boolean needsHumanApproval;
    private int riskScore;

    public AiResultMessage() {
    }

    public String getCaseId() {
        return caseId;
    }

    public void setCaseId(String caseId) {
        this.caseId = caseId;
    }

    public boolean isApproved() {
        return approved;
    }

    public void setApproved(boolean approved) {
        this.approved = approved;
    }

    public boolean isNeedsHumanApproval() {
        return needsHumanApproval;
    }

    public void setNeedsHumanApproval(boolean needsHumanApproval) {
        this.needsHumanApproval = needsHumanApproval;
    }

    public int getRiskScore() {
        return riskScore;
    }

    public void setRiskScore(int riskScore) {
        this.riskScore = riskScore;
    }
}