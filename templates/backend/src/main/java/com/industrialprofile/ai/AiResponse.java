package com.industrialprofile.ai;

import java.util.Map;

public class AiResponse {
    private String status;
    private boolean approved;
    private boolean needsHumanApproval;
    private int riskScore;
    private Map<String, Object> result;
    private Map<String, Object> requirements;
    private Map<String, Object> compliance;
    private Map<String, Object> audit;

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public boolean isApproved() { return approved; }
    public void setApproved(boolean approved) { this.approved = approved; }

    public boolean isNeedsHumanApproval() { return needsHumanApproval; }
    public void setNeedsHumanApproval(boolean needsHumanApproval) { this.needsHumanApproval = needsHumanApproval; }

    public int getRiskScore() { return riskScore; }
    public void setRiskScore(int riskScore) { this.riskScore = riskScore; }

    public Map<String, Object> getResult() { return result; }
    public void setResult(Map<String, Object> result) { this.result = result; }

    public Map<String, Object> getRequirements() { return requirements; }
    public void setRequirements(Map<String, Object> requirements) { this.requirements = requirements; }

    public Map<String, Object> getCompliance() { return compliance; }
    public void setCompliance(Map<String, Object> compliance) { this.compliance = compliance; }

    public Map<String, Object> getAudit() { return audit; }
    public void setAudit(Map<String, Object> audit) { this.audit = audit; }
}
