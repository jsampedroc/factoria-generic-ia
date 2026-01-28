package com.industrialprofile.ai.repository;

import com.industrialprofile.ai.domain.AiCase;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface AiCaseRepository extends JpaRepository<AiCase, UUID> {

    Optional<AiCase> findByCaseId(String caseId);

    boolean existsByCaseId(String caseId);
}