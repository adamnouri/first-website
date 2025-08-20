package com.better.nbamodel.controller;

import com.better.nbamodel.entity.Prediction;
import com.better.nbamodel.service.PredictionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.time.LocalDate;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/v1/predictions")
public class PredictionController {
    
    private final PredictionService predictionService;
    
    @Autowired
    public PredictionController(PredictionService predictionService) {
        this.predictionService = predictionService;
    }
    
    @GetMapping("/matchup")
    public ResponseEntity<Map<String, Object>> getPredictionForMatchup(
            @RequestParam("team1") Long team1Id,
            @RequestParam("team2") Long team2Id) {
        
        try {
            Optional<Prediction> predictionOpt = predictionService.findLatestPredictionForMatchup(team1Id, team2Id);
            
            if (predictionOpt.isEmpty()) {
                Map<String, Object> response = new HashMap<>();
                response.put("status", "no_prediction");
                response.put("message", "No prediction available for this matchup");
                response.put("team1Id", team1Id);
                response.put("team2Id", team2Id);
                return ResponseEntity.ok(response);
            }
            
            Prediction prediction = predictionOpt.get();
            Map<String, Object> response = predictionService.getPredictionWithS3Data(prediction.getPredictionUuid());
            response.put("status", "found");
            
            boolean isFresh = predictionService.isPredictionFresh(prediction.getPredictionUuid(), 3);
            response.put("isFresh", isFresh);
            response.put("staleDays", 3);
            
            return ResponseEntity.ok(response);
            
        } catch (IOException e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("status", "error");
            errorResponse.put("message", "Failed to retrieve prediction data: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("status", "error");
            errorResponse.put("message", "Unexpected error: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
    
    @GetMapping("/upcoming")
    public ResponseEntity<Map<String, Object>> getUpcomingPredictions() {
        try {
            List<Prediction> predictions = predictionService.getUpcomingPredictions();
            
            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("count", predictions.size());
            response.put("predictions", predictions);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("status", "error");
            errorResponse.put("message", "Failed to retrieve upcoming predictions: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
    
    @GetMapping("/history")
    public ResponseEntity<Map<String, Object>> getPredictionHistory(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        
        try {
            Pageable pageable = PageRequest.of(page, size);
            Page<Prediction> predictions = predictionService.getPredictionHistory(pageable);
            
            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("predictions", predictions.getContent());
            response.put("totalElements", predictions.getTotalElements());
            response.put("totalPages", predictions.getTotalPages());
            response.put("currentPage", page);
            response.put("pageSize", size);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("status", "error");
            errorResponse.put("message", "Failed to retrieve prediction history: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
    
    @GetMapping("/accuracy")
    public ResponseEntity<Map<String, Object>> getModelAccuracy() {
        try {
            Map<String, Object> accuracyStats = predictionService.getModelAccuracyStats();
            accuracyStats.put("status", "success");
            
            return ResponseEntity.ok(accuracyStats);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("status", "error");
            errorResponse.put("message", "Failed to calculate model accuracy: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
    
    @GetMapping("/team/{teamId}")
    public ResponseEntity<Map<String, Object>> getPredictionsByTeam(
            @PathVariable Long teamId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        
        try {
            Pageable pageable = PageRequest.of(page, size);
            Page<Prediction> predictions = predictionService.getPredictionsByTeam(teamId, pageable);
            
            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("teamId", teamId);
            response.put("predictions", predictions.getContent());
            response.put("totalElements", predictions.getTotalElements());
            response.put("totalPages", predictions.getTotalPages());
            response.put("currentPage", page);
            response.put("pageSize", size);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("status", "error");
            errorResponse.put("message", "Failed to retrieve team predictions: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
    
    @GetMapping("/date-range")
    public ResponseEntity<Map<String, Object>> getPredictionsInDateRange(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        
        try {
            List<Prediction> predictions = predictionService.getPredictionsInDateRange(startDate, endDate);
            
            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("startDate", startDate);
            response.put("endDate", endDate);
            response.put("count", predictions.size());
            response.put("predictions", predictions);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("status", "error");
            errorResponse.put("message", "Failed to retrieve predictions for date range: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
    
    @GetMapping("/{predictionUuid}")
    public ResponseEntity<Map<String, Object>> getPredictionById(@PathVariable String predictionUuid) {
        try {
            Map<String, Object> predictionData = predictionService.getPredictionWithS3Data(predictionUuid);
            predictionData.put("status", "success");
            
            return ResponseEntity.ok(predictionData);
        } catch (RuntimeException e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("status", "not_found");
            errorResponse.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(errorResponse);
        } catch (IOException e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("status", "error");
            errorResponse.put("message", "Failed to retrieve prediction data: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
    
    @PostMapping("/update-results")
    public ResponseEntity<Map<String, Object>> updatePredictionResults(
            @RequestBody Map<String, Object> updateRequest) {
        
        try {
            String predictionUuid = (String) updateRequest.get("predictionUuid");
            Long actualWinnerId = Long.valueOf(updateRequest.get("actualWinnerId").toString());
            Integer actualTeam1Score = Integer.valueOf(updateRequest.get("actualTeam1Score").toString());
            Integer actualTeam2Score = Integer.valueOf(updateRequest.get("actualTeam2Score").toString());
            
            predictionService.updatePredictionWithActualResults(
                predictionUuid, actualWinnerId, actualTeam1Score, actualTeam2Score);
            
            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("message", "Prediction results updated successfully");
            response.put("predictionUuid", predictionUuid);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("status", "error");
            errorResponse.put("message", "Failed to update prediction results: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errorResponse);
        }
    }
    
    @PostMapping("/trigger-retrain")
    public ResponseEntity<Map<String, Object>> triggerModelRetrain() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "accepted");
        response.put("message", "Model retraining request submitted. This may take several minutes to complete.");
        response.put("note", "Check upcoming predictions endpoint for newly generated predictions");
        
        return ResponseEntity.accepted().body(response);
    }
    
    @GetMapping("/stale")
    public ResponseEntity<Map<String, Object>> getStalePredictions(
            @RequestParam(defaultValue = "7") int staleDays) {
        
        try {
            List<Prediction> stalePredictions = predictionService.getStalePredictions(staleDays);
            
            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("staleDays", staleDays);
            response.put("count", stalePredictions.size());
            response.put("predictions", stalePredictions);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("status", "error");
            errorResponse.put("message", "Failed to retrieve stale predictions: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
    
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> healthCheck() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "healthy");
        response.put("service", "NBA Prediction API");
        response.put("timestamp", java.time.LocalDateTime.now());
        response.put("endpoints", List.of(
            "/matchup", "/upcoming", "/history", "/accuracy", 
            "/team/{teamId}", "/date-range", "/{predictionUuid}", 
            "/update-results", "/trigger-retrain", "/stale"
        ));
        
        return ResponseEntity.ok(response);
    }
}