package com.better.nbamodel.controller;

import com.better.nbamodel.service.PlayoffPredictionService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(PlayoffController.class)
@ActiveProfiles("test")
class PlayoffControllerWorkingTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    @SuppressWarnings("deprecation")
    private PlayoffPredictionService playoffPredictionService;

    @Autowired
    private ObjectMapper objectMapper;

    private Map<String, Object> mockConferenceStandings;
    private Map<String, Object> mockPlayoffBracket;
    private Map<String, Object> mockChampionshipOdds;

    @BeforeEach
    void setUp() {
        setupMockData();
    }

    @Test
    void testGetConferenceStandings_Success() throws Exception {
        when(playoffPredictionService.getConferenceStandings(anyString(), anyInt()))
                .thenReturn(mockConferenceStandings);

        mockMvc.perform(get("/api/playoff/conference-standings")
                        .param("conference", "both")
                        .param("simulations", "1000")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.Eastern").exists())
                .andExpect(jsonPath("$.Western").exists());
    }

    @Test
    void testGetConferenceStandings_WithDefaultParams() throws Exception {
        when(playoffPredictionService.getConferenceStandings("both", 1000))
                .thenReturn(mockConferenceStandings);

        mockMvc.perform(get("/api/playoff/conference-standings")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON));
    }

    @Test
    void testGetConferenceStandings_ServiceError() throws Exception {
        when(playoffPredictionService.getConferenceStandings(anyString(), anyInt()))
                .thenThrow(new RuntimeException("Service unavailable"));

        mockMvc.perform(get("/api/playoff/conference-standings")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isInternalServerError())
                .andExpect(jsonPath("$.error").exists());
    }

    @Test
    void testGeneratePlayoffBracket_Success() throws Exception {
        when(playoffPredictionService.generatePlayoffBracket(any(Boolean.class)))
                .thenReturn(mockPlayoffBracket);

        mockMvc.perform(get("/api/playoff/bracket")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.generated_at").exists());
    }

    @Test
    void testGetChampionshipOdds_Success() throws Exception {
        when(playoffPredictionService.getChampionshipOdds(anyInt()))
                .thenReturn(mockChampionshipOdds);

        mockMvc.perform(get("/api/playoff/championship-odds")
                        .param("simulations", "5000")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.championship_odds").isArray());
    }

    @Test
    void testPredictSeries_Success() throws Exception {
        Map<String, Object> mockSeriesPrediction = new HashMap<>();
        mockSeriesPrediction.put("team1_series_probability", 0.65);
        mockSeriesPrediction.put("team2_series_probability", 0.35);
        mockSeriesPrediction.put("predicted_winner", "Boston Celtics");

        when(playoffPredictionService.predictPlayoffSeries(anyLong(), anyLong(), anyString(), anyInt()))
                .thenReturn(mockSeriesPrediction);

        mockMvc.perform(get("/api/playoff/predict-series")
                        .param("team1_id", "1610612738")
                        .param("team2_id", "1610612747")
                        .param("series_type", "first_round")
                        .param("series_length", "7")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.team1_series_probability").value(0.65));
    }

    @Test
    void testGetConferenceStandings_EasternConference() throws Exception {
        Map<String, Object> easternOnlyResponse = new HashMap<>();
        easternOnlyResponse.put("Eastern", mockConferenceStandings.get("Eastern"));

        when(playoffPredictionService.getConferenceStandings("eastern", 2000))
                .thenReturn(easternOnlyResponse);

        mockMvc.perform(get("/api/playoff/conference-standings")
                        .param("conference", "eastern")
                        .param("simulations", "2000")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.Eastern").exists());
    }

    @Test
    void testGetChampionshipOdds_HighSimulations() throws Exception {
        when(playoffPredictionService.getChampionshipOdds(10000))
                .thenReturn(mockChampionshipOdds);

        mockMvc.perform(get("/api/playoff/championship-odds")
                        .param("simulations", "10000")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.championship_odds").isArray())
                .andExpect(jsonPath("$.last_updated").exists());
    }

    private void setupMockData() {
        // Mock conference standings
        mockConferenceStandings = new HashMap<>();
        
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

        mockConferenceStandings.put("Eastern", List.of(easternTeam));
        mockConferenceStandings.put("Western", List.of(westernTeam));

        // Mock playoff bracket
        mockPlayoffBracket = new HashMap<>();
        mockPlayoffBracket.put("generated_at", "2024-01-15T10:00:00");
        mockPlayoffBracket.put("first_round", new HashMap<>());
        mockPlayoffBracket.put("conference_semifinals", new HashMap<>());
        mockPlayoffBracket.put("conference_finals", new HashMap<>());
        mockPlayoffBracket.put("nba_finals", new HashMap<>());

        // Mock championship odds
        mockChampionshipOdds = new HashMap<>();
        
        Map<String, Object> topTeam = new HashMap<>();
        topTeam.put("team_name", "Boston Celtics");
        topTeam.put("team_abbreviation", "BOS");
        topTeam.put("championship_probability", 0.18);
        topTeam.put("conference", "Eastern");
        topTeam.put("rank", 1);

        mockChampionshipOdds.put("championship_odds", List.of(topTeam));
        mockChampionshipOdds.put("last_updated", "2024-01-15T10:00:00");
        mockChampionshipOdds.put("simulations_run", 5000);
    }
}