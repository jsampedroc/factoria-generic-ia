package com.industrialprofile.ai;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "features.ai")
public class AiProperties {
    /**
     * http | kafka
     */
    private String mode = "kafka";
    private boolean requireHumanApproval = true;

    public AiMode getModeEnum() {
        return "http".equalsIgnoreCase(mode) ? AiMode.HTTP : AiMode.KAFKA;
    }

    public String getMode() { return mode; }
    public void setMode(String mode) { this.mode = mode; }

    public boolean isRequireHumanApproval() { return requireHumanApproval; }
    public void setRequireHumanApproval(boolean requireHumanApproval) { this.requireHumanApproval = requireHumanApproval; }
}
