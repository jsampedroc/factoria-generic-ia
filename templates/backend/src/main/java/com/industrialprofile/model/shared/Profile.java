package com.industrialprofile.model.shared;

import jakarta.persistence.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "profiles", schema = "shared")
@Data
public class Profile {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "profile_id")
    private UUID profileId;

    @Column(name = "profile_code", unique = true, nullable = false, length = 20)
    private String profileCode;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "series_id", referencedColumnName = "series_id")
    private ProfileSeries series;

    @Column(name = "profile_name", nullable = false, length = 150)
    private String profileName;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Column(name = "profile_type", nullable = false, length = 30)
    private String profileType;

    @Column(name = "weight_per_meter", precision = 8, scale = 4)
    private BigDecimal weightPerMeter;

    @Column(name = "price_per_meter_base", precision = 10, scale = 2)
    private BigDecimal pricePerMeterBase;

    @Column(name = "color_ral", length = 10)
    private String colorRal = "9016";

    @Column(name = "color_surcharge", precision = 5, scale = 2)
    private BigDecimal colorSurcharge = new BigDecimal("12.00");

    @Column(name = "is_active")
    private Boolean isActive = true;

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();
}
