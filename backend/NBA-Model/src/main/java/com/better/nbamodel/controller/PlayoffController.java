package com.better.nbamodel.controller;

import com.better.nbamodel.service.PlayoffPredictionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * REST Controller for NBA Playoff Prediction endpoints
 * Serves as a bridge between React frontend and Python ML service
 */
@RestController
@RequestMapping("/api/v1/playoffs")
@CrossOrigin(origins = {"http://localhost:3000", "http://localhost:5173"})
public class PlayoffController {
    
    private final PlayoffPredictionService playoffPredictionService;
    
    @Autowired
    public PlayoffController(PlayoffPredictionService playoffPredictionService) {
        this.playoffPredictionService = playoffPredictionService;
    }
    
    /**
     * Get predicted conference standings
     * GET /api/v1/playoffs/conference-standings?conference=eastern&simulations=1000
     */
    @GetMapping("/conference-standings")
    public ResponseEntity<Map<String, Object>> getConferenceStandings(
            @RequestParam(defaultValue = "both") String conference,
            @RequestParam(defaultValue = "1000") Integer simulations) {
        
        try {
            Map<String, Object> standings = playoffPredictionService.getConferenceStandings(conference, simulations);
            
            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("standings", standings.get("standings"));
            response.put("simulations", standings.get("simulations"));
            response.put("generated_at", standings.get("generated_at"));
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("status", "error");
            errorResponse.put("message", "Failed to get conference standings: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
    
    /**
     * Generate playoff bracket
     * GET /api/v1/playoffs/bracket?use_cached=false
     */
    @GetMapping("/bracket")
    public ResponseEntity<Map<String, Object>> generatePlayoffBracket(
            @RequestParam(defaultValue = "false") Boolean useCached) {
        
        try {
            Map<String, Object> bracket = playoffPredictionService.generatePlayoffBracket(useCached);
            
            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("bracket", bracket.get("bracket"));
            response.put("note", "Complete playoff bracket with predictions");
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("status", "error");
            errorResponse.put("message", "Failed to generate playoff bracket: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
    
    /**
     * Get championship odds
     * GET /api/v1/playoffs/championship-odds?simulations=5000
     */
    @GetMapping("/championship-odds")
    public ResponseEntity<Map<String, Object>> getChampionshipOdds(
            @RequestParam(defaultValue = "5000") Integer simulations) {
        
        try {
            Map<String, Object> odds = playoffPredictionService.getChampionshipOdds(simulations);
            
            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("odds", odds.get("odds"));
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("status", "error");
            errorResponse.put("message", "Failed to calculate championship odds: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
    
    /**
     * Predict playoff series
     * POST /api/v1/playoffs/series-prediction
     */
    @PostMapping("/series-prediction")
    public ResponseEntity<Map<String, Object>> predictPlayoffSeries(
            @RequestBody Map<String, Object> requestBody) {
        
        try {
            // Validate required fields
            if (!requestBody.containsKey("team1_id") || !requestBody.containsKey("team2_id")) {
                Map<String, Object> errorResponse = new HashMap<>();
                errorResponse.put("status", "error");
                errorResponse.put("message", "Missing required fields: team1_id, team2_id");
                return ResponseEntity.badRequest().body(errorResponse);
            }
            
            Long team1Id = Long.valueOf(requestBody.get("team1_id").toString());
            Long team2Id = Long.valueOf(requestBody.get("team2_id").toString());
            String round = requestBody.getOrDefault("round", "first_round").toString();
            Integer seriesLength = Integer.valueOf(requestBody.getOrDefault("series_length", 7).toString());
            
            Map<String, Object> seriesPrediction = playoffPredictionService.predictPlayoffSeries(
                team1Id, team2Id, round, seriesLength);
            
            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("series_prediction", seriesPrediction.get("series_prediction"));
            response.put("game_breakdown", seriesPrediction.get("game_breakdown"));
            response.put("round", seriesPrediction.get("round"));
            response.put("series_length", seriesPrediction.get("series_length"));
            response.put("generated_at", seriesPrediction.get("generated_at"));
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("status", "error");
            errorResponse.put("message", "Failed to predict series: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
    
    /**
     * Simulate playoff tournament
     * POST /api/v1/playoffs/simulate-tournament
     */
    @PostMapping("/simulate-tournament")
    public ResponseEntity<Map<String, Object>> simulatePlayoffTournament(
            @RequestBody(required = false) Map<String, Object> requestBody) {
        
        try {
            if (requestBody == null) {
                requestBody = new HashMap<>();
            }
            
            Integer simulations = Integer.valueOf(requestBody.getOrDefault("simulations", 1000).toString());
            Boolean includePlayIn = Boolean.valueOf(requestBody.getOrDefault("include_play_in", true).toString());
            Map<String, Object> standings = (Map<String, Object>) requestBody.get("standings");
            
            Map<String, Object> tournamentResult = playoffPredictionService.simulatePlayoffTournament(
                simulations, standings, includePlayIn);
            
            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("tournament_simulation", tournamentResult.get("tournament_simulation"));
            response.put("generated_at", tournamentResult.get("generated_at"));
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("status", "error");
            errorResponse.put("message", "Failed to simulate tournament: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
    
    /**
     * Get detailed playoff odds for specific team
     * GET /api/v1/playoffs/team-odds/{teamId}
     */
    @GetMapping("/team-odds/{teamId}")
    public ResponseEntity<Map<String, Object>> getTeamPlayoffOdds(@PathVariable Long teamId) {
        
        try {
            Map<String, Object> teamOdds = playoffPredictionService.getTeamPlayoffOdds(teamId);
            
            if (teamOdds.containsKey("error")) {
                Map<String, Object> errorResponse = new HashMap<>();
                errorResponse.put("status", "not_found");
                errorResponse.put("message", teamOdds.get("error"));
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(errorResponse);
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("team_odds", teamOdds.get("team_odds"));
            response.put("round_probabilities", teamOdds.get("round_probabilities"));
            response.put("team_id", teamOdds.get("team_id"));
            response.put("calculated_at", teamOdds.get("calculated_at"));
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("status", "error");
            errorResponse.put("message", "Failed to get team odds: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
    
    /**
     * Health check endpoint for playoff services
     * GET /api/v1/playoffs/health
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> healthCheck() {
        try {
            boolean mlServiceHealthy = playoffPredictionService.checkMLServiceHealth();
            
            Map<String, Object> response = new HashMap<>();
            response.put("status", mlServiceHealthy ? "healthy" : "degraded");
            response.put("service", "NBA Playoff Prediction API");
            response.put("timestamp", java.time.LocalDateTime.now());
            response.put("ml_service_status", mlServiceHealthy ? "healthy" : "unhealthy");
            response.put("endpoints", java.util.List.of(
                "/conference-standings", "/bracket", "/championship-odds", 
                "/series-prediction", "/simulate-tournament", "/team-odds/{teamId}"
            ));
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("status", "error");
            errorResponse.put("message", "Health check failed: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
}