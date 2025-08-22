package com.better.nbamodel.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.client.ResourceAccessException;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@ActiveProfiles("test")
class PlayoffPredictionServiceWorkingTest {

    @Mock
    private RestTemplate restTemplate;

    private PlayoffPredictionService playoffPredictionService;

    private Map<String, Object> mockPythonResponse;

    @BeforeEach
    void setUp() {
        setupMockData();
        playoffPredictionService = new PlayoffPredictionService();
        // Use reflection to set the RestTemplate mock
        try {
            java.lang.reflect.Field restTemplateField = PlayoffPredictionService.class.getDeclaredField("restTemplate");
            restTemplateField.setAccessible(true);
            restTemplateField.set(playoffPredictionService, restTemplate);
        } catch (Exception e) {
            throw new RuntimeException("Failed to inject mock RestTemplate", e);
        }
    }

    @Test
    void testGetConferenceStandings_Success() {
        when(restTemplate.getForObject(anyString(), eq(Map.class)))
                .thenReturn(mockPythonResponse);

        Map<String, Object> result = playoffPredictionService.getConferenceStandings("both", 1000);

        assertNotNull(result);
        assertTrue(result.containsKey("Eastern"));
        assertTrue(result.containsKey("Western"));
        
        // Verify the URL was called correctly
        verify(restTemplate).getForObject(contains("/playoffs/conference-standings"), eq(Map.class));
    }

    @Test
    void testGetConferenceStandings_EasternOnly() {
        Map<String, Object> easternResponse = new HashMap<>();
        easternResponse.put("Eastern", mockPythonResponse.get("Eastern"));

        when(restTemplate.getForObject(anyString(), eq(Map.class)))
                .thenReturn(easternResponse);

        Map<String, Object> result = playoffPredictionService.getConferenceStandings("eastern", 2000);

        assertNotNull(result);
        assertTrue(result.containsKey("Eastern"));
        assertFalse(result.containsKey("Western"));
    }

    @Test
    void testGetConferenceStandings_ServiceUnavailable() {
        when(restTemplate.getForObject(anyString(), eq(Map.class)))
                .thenThrow(new ResourceAccessException("Connection refused"));

        Exception exception = assertThrows(RuntimeException.class, () -> {
            playoffPredictionService.getConferenceStandings("both", 1000);
        });

        assertTrue(exception.getMessage().contains("Failed to get conference standings"));
    }

    @Test
    void testGeneratePlayoffBracket_Success() {
        Map<String, Object> mockBracketResponse = new HashMap<>();
        mockBracketResponse.put("generated_at", "2024-01-15T10:00:00");
        mockBracketResponse.put("first_round", new HashMap<>());
        mockBracketResponse.put("conference_semifinals", new HashMap<>());
        mockBracketResponse.put("conference_finals", new HashMap<>());
        mockBracketResponse.put("nba_finals", new HashMap<>());

        when(restTemplate.getForObject(anyString(), eq(Map.class)))
                .thenReturn(mockBracketResponse);

        Map<String, Object> result = playoffPredictionService.generatePlayoffBracket(false);

        assertNotNull(result);
        assertTrue(result.containsKey("generated_at"));
        assertTrue(result.containsKey("first_round"));
        
        verify(restTemplate).getForObject(contains("/playoffs/bracket"), eq(Map.class));
    }

    @Test
    void testGeneratePlayoffBracket_WithCache() {
        Map<String, Object> cachedBracketResponse = new HashMap<>();
        cachedBracketResponse.put("generated_at", "2024-01-15T09:00:00");
        cachedBracketResponse.put("cached", true);

        when(restTemplate.getForObject(anyString(), eq(Map.class)))
                .thenReturn(cachedBracketResponse);

        Map<String, Object> result = playoffPredictionService.generatePlayoffBracket(true);

        assertNotNull(result);
        assertTrue(result.containsKey("generated_at"));
    }

    @Test
    void testGetChampionshipOdds_Success() {
        Map<String, Object> mockOddsResponse = new HashMap<>();
        mockOddsResponse.put("championship_odds", List.of());
        mockOddsResponse.put("simulations_run", 5000);
        mockOddsResponse.put("last_updated", "2024-01-15T10:00:00");

        when(restTemplate.getForObject(anyString(), eq(Map.class)))
                .thenReturn(mockOddsResponse);

        Map<String, Object> result = playoffPredictionService.getChampionshipOdds(5000);

        assertNotNull(result);
        assertTrue(result.containsKey("championship_odds"));
        assertTrue(result.containsKey("simulations_run"));
        assertEquals(5000, result.get("simulations_run"));
        
        verify(restTemplate).getForObject(contains("/playoffs/championship-odds"), eq(Map.class));
    }

    @Test
    void testPredictPlayoffSeries_Success() {
        Map<String, Object> mockSeriesResponse = new HashMap<>();
        mockSeriesResponse.put("team1_series_probability", 0.65);
        mockSeriesResponse.put("team2_series_probability", 0.35);
        mockSeriesResponse.put("predicted_winner", "Boston Celtics");
        mockSeriesResponse.put("confidence", 0.65);
        mockSeriesResponse.put("predicted_games", 6);

        when(restTemplate.getForObject(anyString(), eq(Map.class)))
                .thenReturn(mockSeriesResponse);

        Map<String, Object> result = playoffPredictionService.predictPlayoffSeries(
                1610612738L, 1610612747L, "first_round", 7);

        assertNotNull(result);
        assertTrue(result.containsKey("team1_series_probability"));
        assertTrue(result.containsKey("predicted_winner"));
        assertEquals(0.65, result.get("team1_series_probability"));
        assertEquals("Boston Celtics", result.get("predicted_winner"));
        
        verify(restTemplate).getForObject(contains("/playoffs/predict-series"), eq(Map.class));
    }

    @Test
    void testSimulatePlayoffTournament_Success() {
        Map<String, Object> mockSimResponse = new HashMap<>();
        mockSimResponse.put("champion", "Boston Celtics");
        mockSimResponse.put("finals_teams", List.of("Boston Celtics", "Denver Nuggets"));
        mockSimResponse.put("simulation_id", "test-123");
        mockSimResponse.put("bracket_results", new HashMap<>());

        when(restTemplate.postForObject(anyString(), any(), eq(Map.class)))
                .thenReturn(mockSimResponse);

        Map<String, Object> standings = new HashMap<>();
        Map<String, Object> result = playoffPredictionService.simulatePlayoffTournament(1000, standings, true);

        assertNotNull(result);
        assertTrue(result.containsKey("champion"));
        assertTrue(result.containsKey("finals_teams"));
        assertEquals("Boston Celtics", result.get("champion"));
        
        verify(restTemplate).postForObject(contains("/playoffs/simulate"), any(), eq(Map.class));
    }

    @Test
    void testServiceResilience() {
        // Test that service handles temporary failures gracefully
        when(restTemplate.getForObject(anyString(), eq(Map.class)))
                .thenThrow(new ResourceAccessException("Temporary timeout"))
                .thenReturn(mockPythonResponse); // Second call succeeds

        Exception exception = assertThrows(RuntimeException.class, () -> {
            playoffPredictionService.getConferenceStandings("both", 1000);
        });

        assertTrue(exception.getMessage().contains("Failed to get conference standings"));
        verify(restTemplate, times(1)).getForObject(anyString(), eq(Map.class));
    }

    @Test
    void testMultipleServiceCalls() {
        when(restTemplate.getForObject(anyString(), eq(Map.class)))
                .thenReturn(mockPythonResponse);

        // Make multiple calls
        Map<String, Object> result1 = playoffPredictionService.getConferenceStandings("both", 1000);
        Map<String, Object> result2 = playoffPredictionService.getConferenceStandings("eastern", 2000);

        assertNotNull(result1);
        assertNotNull(result2);
        
        // Verify both calls were made
        verify(restTemplate, times(2)).getForObject(anyString(), eq(Map.class));
    }

    @Test
    void testDifferentSimulationCounts() {
        when(restTemplate.getForObject(anyString(), eq(Map.class)))
                .thenReturn(mockPythonResponse);

        // Test different simulation counts
        playoffPredictionService.getConferenceStandings("both", 100);
        playoffPredictionService.getConferenceStandings("both", 5000);
        playoffPredictionService.getConferenceStandings("both", 10000);

        verify(restTemplate, times(3)).getForObject(anyString(), eq(Map.class));
    }

    private void setupMockData() {
        mockPythonResponse = new HashMap<>();
        
        Map<String, Object> easternTeam = new HashMap<>();
        easternTeam.put("rank", 1);
        easternTeam.put("team_name", "Boston Celtics");
        easternTeam.put("team_abbreviation", "BOS");
        easternTeam.put("projected_wins", 58.5);
        easternTeam.put("projected_losses", 23.5);
        easternTeam.put("win_percentage", 0.717);
        easternTeam.put("playoff_probability", 0.95);
        easternTeam.put("championship_odds", 0.18);

        Map<String, Object> westernTeam = new HashMap<>();
        westernTeam.put("rank", 1);
        westernTeam.put("team_name", "Denver Nuggets");
        westernTeam.put("team_abbreviation", "DEN");
        westernTeam.put("projected_wins", 56.2);
        westernTeam.put("projected_losses", 25.8);
        westernTeam.put("win_percentage", 0.685);
        westernTeam.put("playoff_probability", 0.92);
        westernTeam.put("championship_odds", 0.15);

        mockPythonResponse.put("Eastern", List.of(easternTeam));
        mockPythonResponse.put("Western", List.of(westernTeam));
    }
}