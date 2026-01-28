package com.industrialprofile.service;

import com.industrialprofile.model.tenant.StockBar;
import com.industrialprofile.model.shared.Profile;
import com.industrialprofile.repository.StockBarRepository;
import com.industrialprofile.repository.ProfileRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class StockService {
    
    private final StockBarRepository stockBarRepository;
    private final ProfileRepository profileRepository;
    
    public List<StockBar> getAvailableBarsByProfile(UUID profileId) {
        return stockBarRepository.findByProfile_ProfileId(profileId)
                .stream()
                .filter(bar -> !bar.getIsAllocated())
                .collect(Collectors.toList());
    }
    
    public BigDecimal getAvailableLengthByProfile(UUID profileId) {
        return stockBarRepository.sumAvailableLengthByProfile(profileId);
    }
    
    public List<StockBar> getAvailableBarsBySeries(UUID seriesId) {
        return stockBarRepository.findByProfile_Series_SeriesId(seriesId)
                .stream()
                .filter(bar -> !bar.getIsAllocated())
                .collect(Collectors.toList());
    }
    
    public List<StockBar> findBarsForCutting(UUID profileId, BigDecimal requiredLength) {
        return stockBarRepository.findAvailableByProfileAndMinLength(profileId, requiredLength);
    }
    
    public Map<UUID, StockSummary> getAvailableStockSummary() {
        List<Object[]> results = stockBarRepository.findAvailableStockSummary();
        Map<UUID, StockSummary> summaryMap = new HashMap<>();
        
        for (Object[] row : results) {
            UUID profileId = (UUID) row[0];
            BigDecimal totalLength = (BigDecimal) row[1];
            Long barCount = (Long) row[2];
            
            Profile profile = profileRepository.findById(profileId).orElse(null);
            String profileName = profile != null ? profile.getProfileName() : "Unknown";
            String profileCode = profile != null ? profile.getProfileCode() : "N/A";
            
            summaryMap.put(profileId, new StockSummary(profileId, profileCode, profileName, totalLength, barCount));
        }
        
        return summaryMap;
    }
    
    public List<StockSummary> getAvailableStockSummaryList() {
        return new ArrayList<>(getAvailableStockSummary().values());
    }
    
    @lombok.Data
    @lombok.AllArgsConstructor
    public static class StockSummary {
        private UUID profileId;
        private String profileCode;
        private String profileName;
        private BigDecimal totalAvailableLength;
        private Long barCount;
    }
}
