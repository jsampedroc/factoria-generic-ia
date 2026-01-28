package com.industrialprofile.model.tenant;

import com.industrialprofile.model.shared.Profile;
import jakarta.persistence.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

@Entity
@Table(name = "stock_bars")
@Data
public class StockBar {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "stock_bar_id")
    private UUID stockBarId;

    @Column(name = "bar_code", nullable = false, length = 100)
    private String barCode;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "profile_id", referencedColumnName = "profile_id")
    private Profile profile;

    @Column(name = "original_length", precision = 5, scale = 2, nullable = false)
    private BigDecimal originalLength;

    @Column(name = "current_length", precision = 5, scale = 2, nullable = false)
    private BigDecimal currentLength;

    @Column(name = "length_unit", length = 5)
    private String lengthUnit = "M";

    @Column(name = "purchase_cost", precision = 10, scale = 2)
    private BigDecimal purchaseCost;

    @Column(name = "purchase_date")
    private LocalDate purchaseDate;

    @Column(name = "supplier_id")
    private UUID supplierId;

    @Column(name = "warehouse_location", length = 100)
    private String warehouseLocation;

    @Column(name = "rack_position", length = 50)
    private String rackPosition;

    @Column(name = "is_allocated")
    private Boolean isAllocated = false;

    @Column(name = "allocation_order_id")
    private UUID allocationOrderId;

    @Column(name = "quality_status", length = 20)
    private String qualityStatus = "GOOD";

    @Column(name = "notes", columnDefinition = "TEXT")
    private String notes;

    @Column(name = "created_at")
    private java.time.LocalDateTime createdAt = java.time.LocalDateTime.now();
}
