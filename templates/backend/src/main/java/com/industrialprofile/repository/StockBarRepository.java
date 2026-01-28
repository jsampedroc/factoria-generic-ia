package com.industrialprofile.repository;

import com.industrialprofile.model.tenant.StockBar;
import com.industrialprofile.model.shared.Profile;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

@Repository
public interface StockBarRepository extends JpaRepository<StockBar, UUID> {
    
    List<StockBar> findByProfile_ProfileId(UUID profileId);
    
    List<StockBar> findByProfile_Series_SeriesId(UUID seriesId);
    
    List<StockBar> findByIsAllocatedFalse();
    
    @Query("SELECT sb FROM StockBar sb WHERE sb.profile.profileId = :profileId AND sb.isAllocated = false AND sb.currentLength >= :minLength")
    List<StockBar> findAvailableByProfileAndMinLength(@Param("profileId") UUID profileId, @Param("minLength") BigDecimal minLength);
    
    @Query("SELECT COALESCE(SUM(sb.currentLength), 0) FROM StockBar sb WHERE sb.profile.profileId = :profileId AND sb.isAllocated = false")
    BigDecimal sumAvailableLengthByProfile(@Param("profileId") UUID profileId);
    
    @Query("SELECT sb.profile.profileId, COALESCE(SUM(sb.currentLength), 0) as totalLength, COUNT(sb) as barCount " +
           "FROM StockBar sb WHERE sb.isAllocated = false GROUP BY sb.profile.profileId")
    List<Object[]> findAvailableStockSummary();
}
