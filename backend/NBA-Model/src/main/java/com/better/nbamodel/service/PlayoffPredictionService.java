package com.better.nbamodel.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.logging.Logger;

/**
 * Service for handling playoff predictions by communicating with Python ML service
 */
@Service
public class PlayoffPredictionService {
    
    private static final Logger logger = Logger.getLogger(PlayoffPredictionService.class.getName());
    
    @Value("${ml.service.url:http://localhost:5000}")
    private String mlServiceUrl;
    
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    
    public PlayoffPredictionService() {
        this.restTemplate = new RestTemplate();
        this.objectMapper = new ObjectMapper();
        
        // Configure timeout settings
        restTemplate.getInterceptors().add((request, body, execution) -> {
            request.getHeaders().add(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE);
            return execution.execute(request, body);
        });
    }
    
    /**
     * Get conference standings from ML service
     */
    public Map<String, Object> getConferenceStandings(String conference, Integer simulations) {
        try {
            String url = UriComponentsBuilder.fromHttpUrl(mlServiceUrl)
                    .path("/playoffs/conference-standings")
                    .queryParam("conference", conference)
                    .queryParam("simulations", simulations)
                    .toUriString();
            
            logger.info("Calling ML service for conference standings: " + url);
            
            ResponseEntity<String> response = restTemplate.exchange(
                url, 
                HttpMethod.GET, 
                null, 
                String.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK) {
                return objectMapper.readValue(response.getBody(), new TypeReference<Map<String, Object>>() {});
            } else {
                throw new RuntimeException("ML service returned status: " + response.getStatusCode());
            }
            
        } catch (Exception e) {
            logger.severe("Error getting conference standings: " + e.getMessage());
            throw new RuntimeException("Failed to get conference standings from ML service", e);
        }
    }
    
    /**
     * Generate playoff bracket from ML service
     */
    public Map<String, Object> generatePlayoffBracket(Boolean useCached) {
        try {
            String url = UriComponentsBuilder.fromHttpUrl(mlServiceUrl)
                    .path("/playoffs/bracket")
                    .queryParam("use_cached", useCached)
                    .toUriString();
            
            logger.info("Calling ML service for playoff bracket: " + url);
            
            ResponseEntity<String> response = restTemplate.exchange(
                url, 
                HttpMethod.GET, 
                null, 
                String.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK) {
                return objectMapper.readValue(response.getBody(), new TypeReference<Map<String, Object>>() {});
            } else {
                throw new RuntimeException("ML service returned status: " + response.getStatusCode());
            }
            
        } catch (Exception e) {
            logger.severe("Error generating playoff bracket: " + e.getMessage());
            throw new RuntimeException("Failed to generate playoff bracket from ML service", e);
        }
    }
    
    /**
     * Get championship odds from ML service
     */
    public Map<String, Object> getChampionshipOdds(Integer simulations) {
        try {
            String url = UriComponentsBuilder.fromHttpUrl(mlServiceUrl)
                    .path("/playoffs/championship-odds")
                    .queryParam("simulations", simulations)
                    .toUriString();
            
            logger.info("Calling ML service for championship odds: " + url);
            
            ResponseEntity<String> response = restTemplate.exchange(
                url, 
                HttpMethod.GET, 
                null, 
                String.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK) {
                return objectMapper.readValue(response.getBody(), new TypeReference<Map<String, Object>>() {});
            } else {
                throw new RuntimeException("ML service returned status: " + response.getStatusCode());
            }
            
        } catch (Exception e) {
            logger.severe("Error getting championship odds: " + e.getMessage());
            throw new RuntimeException("Failed to get championship odds from ML service", e);
        }
    }
    
    /**
     * Predict playoff series from ML service
     */
    public Map<String, Object> predictPlayoffSeries(Long team1Id, Long team2Id, String round, Integer seriesLength) {
        try {
            String url = mlServiceUrl + "/playoffs/series-prediction";
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("team1_id", team1Id);
            requestBody.put("team2_id", team2Id);
            requestBody.put("round", round);
            requestBody.put("series_length", seriesLength);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);
            
            logger.info("Calling ML service for series prediction: " + url);
            
            ResponseEntity<String> response = restTemplate.exchange(
                url, 
                HttpMethod.POST, 
                entity, 
                String.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK) {
                return objectMapper.readValue(response.getBody(), new TypeReference<Map<String, Object>>() {});
            } else {
                throw new RuntimeException("ML service returned status: " + response.getStatusCode());
            }
            
        } catch (Exception e) {
            logger.severe("Error predicting playoff series: " + e.getMessage());
            throw new RuntimeException("Failed to predict playoff series from ML service", e);
        }
    }
    
    /**
     * Simulate playoff tournament from ML service
     */
    public Map<String, Object> simulatePlayoffTournament(Integer simulations, Map<String, Object> standings, Boolean includePlayIn) {
        try {
            String url = mlServiceUrl + "/playoffs/simulate-tournament";
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("simulations", simulations);
            requestBody.put("include_play_in", includePlayIn);
            
            if (standings != null) {
                requestBody.put("standings", standings);
            }
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);
            
            logger.info("Calling ML service for tournament simulation: " + url);
            
            ResponseEntity<String> response = restTemplate.exchange(
                url, 
                HttpMethod.POST, 
                entity, 
                String.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK) {
                return objectMapper.readValue(response.getBody(), new TypeReference<Map<String, Object>>() {});
            } else {
                throw new RuntimeException("ML service returned status: " + response.getStatusCode());
            }
            
        } catch (Exception e) {
            logger.severe("Error simulating playoff tournament: " + e.getMessage());
            throw new RuntimeException("Failed to simulate playoff tournament from ML service", e);
        }
    }
    
    /**
     * Get team playoff odds from ML service
     */
    public Map<String, Object> getTeamPlayoffOdds(Long teamId) {
        try {
            String url = mlServiceUrl + "/playoffs/team-odds/" + teamId;
            
            logger.info("Calling ML service for team odds: " + url);
            
            ResponseEntity<String> response = restTemplate.exchange(
                url, 
                HttpMethod.GET, 
                null, 
                String.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK) {
                return objectMapper.readValue(response.getBody(), new TypeReference<Map<String, Object>>() {});
            } else if (response.getStatusCode() == HttpStatus.NOT_FOUND) {
                Map<String, Object> errorResponse = new HashMap<>();
                errorResponse.put("error", "Team not found in odds calculation");
                return errorResponse;
            } else {
                throw new RuntimeException("ML service returned status: " + response.getStatusCode());
            }
            
        } catch (Exception e) {
            logger.severe("Error getting team playoff odds: " + e.getMessage());
            throw new RuntimeException("Failed to get team playoff odds from ML service", e);
        }
    }
    
    /**
     * Check ML service health
     */
    public boolean checkMLServiceHealth() {
        try {
            String url = mlServiceUrl + "/health";
            
            ResponseEntity<String> response = restTemplate.exchange(
                url, 
                HttpMethod.GET, 
                null, 
                String.class
            );
            
            return response.getStatusCode() == HttpStatus.OK;
            
        } catch (Exception e) {
            logger.warning("ML service health check failed: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Get ML service configuration
     */
    public Map<String, Object> getMLServiceInfo() {
        try {
            String url = mlServiceUrl + "/model/info";
            
            ResponseEntity<String> response = restTemplate.exchange(
                url, 
                HttpMethod.GET, 
                null, 
                String.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK) {
                return objectMapper.readValue(response.getBody(), new TypeReference<Map<String, Object>>() {});
            } else {
                throw new RuntimeException("ML service returned status: " + response.getStatusCode());
            }
            
        } catch (Exception e) {
            logger.warning("Error getting ML service info: " + e.getMessage());
            Map<String, Object> fallback = new HashMap<>();
            fallback.put("status", "unavailable");
            fallback.put("error", e.getMessage());
            return fallback;
        }
    }
}