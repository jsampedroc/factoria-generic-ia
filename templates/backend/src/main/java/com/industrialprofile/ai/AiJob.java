package com.industrialprofile.ai;

import java.util.Map;

public class AiJob {
    private String caseId;
    private String traceId;
    private String task;
    private String promptVersion;
    private Map<String, Object> input;

    public String getCaseId() { return caseId; }
    public void setCaseId(String caseId) { this.caseId = caseId; }

    public String getTraceId() { return traceId; }
    public void setTraceId(String traceId) { this.traceId = traceId; }

    public String getTask() { return task; }
    public void setTask(String task) { this.task = task; }

    public String getPromptVersion() { return promptVersion; }
    public void setPromptVersion(String promptVersion) { this.promptVersion = promptVersion; }

    public Map<String, Object> getInput() { return input; }
    public void setInput(Map<String, Object> input) { this.input = input; }
}
