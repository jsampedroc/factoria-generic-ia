package com.industrialprofile.ai.service;

import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import com.industrialprofile.ai.AiJob;
import com.industrialprofile.ai.AiMode;
import com.industrialprofile.ai.AiProperties;
import com.industrialprofile.ai.CrewAiHttpClient;

@Service
public class AiOrchestrationService {

    private final AiProperties props;
    private final CrewAiHttpClient httpClient;
    private final KafkaTemplate<String, AiJob> kafka;

    public AiOrchestrationService(AiProperties props, CrewAiHttpClient httpClient, KafkaTemplate<String, AiJob> kafka) {
        this.props = props;
        this.httpClient = httpClient;
        this.kafka = kafka;
    }

    public Object run(AiJob job) {
        if (props.getModeEnum() == AiMode.KAFKA) {
            kafka.send("ai.jobs", job.getCaseId(), job);
            return java.util.Map.of("status", "ACCEPTED", "caseId", job.getCaseId());
        }
        return httpClient.run(job);
    }
}
