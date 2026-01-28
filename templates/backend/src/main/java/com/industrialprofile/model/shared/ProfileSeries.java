package com.industrialprofile.model.shared;

import jakarta.persistence.*;
import lombok.Data;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "profile_series", schema = "shared")
@Data
public class ProfileSeries {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "series_id")
    private UUID seriesId;

    @Column(name = "series_code", unique = true, nullable = false, length = 20)
    private String seriesCode;

    @Column(name = "series_name", nullable = false, length = 100)
    private String seriesName;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Column(name = "system_type", nullable = false, length = 50)
    private String systemType;

    @Column(name = "standard_length", precision = 5, scale = 2, nullable = false)
    private BigDecimal standardLength = new BigDecimal("6.00");

    @Column(name = "special_length", precision = 5, scale = 2)
    private BigDecimal specialLength = new BigDecimal("7.00");

    @Column(name = "special_length_surcharge", precision = 5, scale = 2)
    private BigDecimal specialLengthSurcharge = new BigDecimal("8.00");

    @Column(name = "cutting_tolerance_standard", precision = 5, scale = 4)
    private BigDecimal cuttingToleranceStandard = new BigDecimal("0.0015");

    @Column(name = "cutting_tolerance_special", precision = 5, scale = 4)
    private BigDecimal cuttingToleranceSpecial = new BigDecimal("0.0005");

    @Column(name = "cutting_loss_percentage", precision = 5, scale = 2)
    private BigDecimal cuttingLossPercentage = new BigDecimal("2.00");

    @Column(name = "is_active")
    private Boolean isActive = true;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "technical_specifications", columnDefinition = "jsonb")
    private String technicalSpecifications;

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();
}
