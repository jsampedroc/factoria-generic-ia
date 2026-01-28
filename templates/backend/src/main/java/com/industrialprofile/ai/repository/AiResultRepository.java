package com.industrialprofile.ai.repository;

import com.industrialprofile.ai.domain.AiResult;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.List;
import java.util.UUID;

public interface AiResultRepository extends JpaRepository<AiResult, UUID> {

    List<AiResult> findByCaseId(String caseId);

    Optional<AiResult> findTopByCaseIdOrderByCreatedAtDesc(String caseId);
}