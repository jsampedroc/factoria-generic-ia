package com.industrialprofile.ai.infrastructure.kafka;

import com.industrialprofile.ai.messaging.dto.AiResultMessage;
import com.industrialprofile.ai.service.AiResultService;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class AiResultKafkaConsumer {

    private final AiResultService service;

    public AiResultKafkaConsumer(AiResultService service) {
        this.service = service;
    }

    @KafkaListener(topics = "ai.results", groupId = "ai-backend")
    public void consume(AiResultMessage msg) {
        service.saveResult(
                msg.getCaseId(),
                msg.isApproved(),
                msg.isNeedsHumanApproval(),
                msg.getRiskScore()
        );
    }
}