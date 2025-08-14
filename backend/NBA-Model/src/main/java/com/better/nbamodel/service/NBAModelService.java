package com.better.nbamodel.service;

import com.better.nbamodel.entity.Game;
import com.better.nbamodel.entity.Team;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.Map;

@Service
public class NBAModelService {
    
    @Autowired
    private GameService gameService;
    
    @Autowired
    private TeamService teamService;
    
    public Map<String, Object> predictGame(Long gameId) {
        Game game = gameService.getGameById(gameId).orElse(null);
        if (game == null) {
            return null;
        }
        
        Team homeTeam = game.getHomeTeam();
        Team awayTeam = game.getAwayTeam();
        
        // Call Python prediction function
        Map<String, Object> prediction = callPythonPrediction(gameId, homeTeam.getTeamCode(), awayTeam.getTeamCode());
        
        if (prediction == null) {
            // Fallback response if Python call fails
            prediction = new HashMap<>();
            prediction.put("gameId", gameId);
            prediction.put("homeTeam", homeTeam.getName());
            prediction.put("awayTeam", awayTeam.getName());
            prediction.put("error", "Prediction service temporarily unavailable");
        }
        
        return prediction;
    }
    
    private Map<String, Object> callPythonPrediction(Long gameId, String homeTeamCode, String awayTeamCode) {
        try {
            // TODO: Uncomment and modify this section when Python script is ready
            /*
            ProcessBuilder pb = new ProcessBuilder(
                "python3", 
                "/path/to/your/nba_predictor.py",
                "--game-id", gameId.toString(),
                "--home-team", homeTeamCode,
                "--away-team", awayTeamCode
            );
            
            Process process = pb.start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder result = new StringBuilder();
            String line;
            
            while ((line = reader.readLine()) != null) {
                result.append(line);
            }
            
            int exitCode = process.waitFor();
            if (exitCode == 0) {
                // Parse JSON response from Python script
                // ObjectMapper mapper = new ObjectMapper();
                // return mapper.readValue(result.toString(), Map.class);
                return parseJsonResponse(result.toString());
            }
            */
            
            // For now, return null to indicate Python service is not available
            return null;
            
        } catch (Exception e) {
            System.err.println("Error calling Python prediction: " + e.getMessage());
            return null;
        }
    }
    
    // Helper method to parse JSON response from Python
    private Map<String, Object> parseJsonResponse(String jsonResponse) {
        // TODO: Implement JSON parsing or use ObjectMapper
        // This is a placeholder for when you implement the Python integration
        Map<String, Object> response = new HashMap<>();
        response.put("message", "Python prediction received: " + jsonResponse);
        return response;
    }
}