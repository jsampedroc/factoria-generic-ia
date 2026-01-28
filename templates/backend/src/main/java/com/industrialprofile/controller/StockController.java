package com.industrialprofile.controller;

import com.industrialprofile.model.tenant.StockBar;
import com.industrialprofile.service.StockService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/stock")
@RequiredArgsConstructor
public class StockController {
    
    private final StockService stockService;
    
    @GetMapping("/profile/{profileId}/available")
    public ResponseEntity<List<StockBar>> getAvailableBarsByProfile(@PathVariable UUID profileId) {
        List<StockBar> bars = stockService.getAvailableBarsByProfile(profileId);
        return ResponseEntity.ok(bars);
    }
    
    @GetMapping("/profile/{profileId}/available-length")
    public ResponseEntity<Map<String, Object>> getAvailableLengthByProfile(@PathVariable UUID profileId) {
        BigDecimal availableLength = stockService.getAvailableLengthByProfile(profileId);
        return ResponseEntity.ok(Map.of(
            "profileId", profileId,
            "availableLength", availableLength,
            "unit", "meters"
        ));
    }
    
    @GetMapping("/series/{seriesId}/available")
    public ResponseEntity<List<StockBar>> getAvailableBarsBySeries(@PathVariable UUID seriesId) {
        List<StockBar> bars = stockService.getAvailableBarsBySeries(seriesId);
        return ResponseEntity.ok(bars);
    }
    
    @GetMapping("/profile/{profileId}/find-for-cutting")
    public ResponseEntity<List<StockBar>> findBarsForCutting(
            @PathVariable UUID profileId,
            @RequestParam BigDecimal requiredLength) {
        List<StockBar> bars = stockService.findBarsForCutting(profileId, requiredLength);
        return ResponseEntity.ok(bars);
    }
    
    @GetMapping("/summary")
    public ResponseEntity<List<StockService.StockSummary>> getStockSummary() {
        List<StockService.StockSummary> summary = stockService.getAvailableStockSummaryList();
        return ResponseEntity.ok(summary);
    }
    
    @GetMapping("/summary-map")
    public ResponseEntity<Map<UUID, StockService.StockSummary>> getStockSummaryMap() {
        Map<UUID, StockService.StockSummary> summary = stockService.getAvailableStockSummary();
        return ResponseEntity.ok(summary);
    }
}
