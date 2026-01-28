package com.industrialprofile.model.tenant;

import com.industrialprofile.model.shared.Profile;
import jakarta.persistence.*;
import lombok.Data;
import java.math.BigDecimal;
import java.util.UUID;

@Entity
@Table(name = "stock_remnants")
@Data
public class StockRemnant {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "remnant_id")
    private UUID remnantId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "profile_id", referencedColumnName = "profile_id")
    private Profile profile;

    @Column(name = "original_bar_id")
    private UUID originalBarId;

    @Column(name = "remnant_length", precision = 5, scale = 3, nullable = false)
    private BigDecimal remnantLength;

    @Column(name = "width", precision = 5, scale = 3)
    private BigDecimal width;

    @Column(name = "height", precision = 5, scale = 3)
    private BigDecimal height;

    @Column(name = "usable_for_min_length", precision = 5, scale = 3)
    private BigDecimal usableForMinLength;

    @Column(name = "is_allocated")
    private Boolean isAllocated = false;

    @Column(name = "allocation_order_item_id")
    private UUID allocationOrderItemId;

    @Column(name = "warehouse_location", length = 100)
    private String warehouseLocation;

    @Column(name = "quality_status", length = 20)
    private String qualityStatus = "GOOD";

    @Column(name = "notes", columnDefinition = "TEXT")
    private String notes;

    @Column(name = "created_at")
    private java.time.LocalDateTime createdAt = java.time.LocalDateTime.now();
}
