package com.better.nbamodel.service;

import com.better.nbamodel.S3.S3Service;
import com.better.nbamodel.entity.Prediction;
import com.better.nbamodel.entity.Team;
import com.better.nbamodel.repository.PredictionRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.IOException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;

@Service
@Transactional
public class PredictionService {
    
    private final PredictionRepository predictionRepository;
    private final TeamService teamService;
    private final S3Service s3Service;
    
    @Autowired
    public PredictionService(PredictionRepository predictionRepository, 
                           TeamService teamService, 
                           S3Service s3Service) {
        this.predictionRepository = predictionRepository;
        this.teamService = teamService;
        this.s3Service = s3Service;
    }
    
    public Optional<Prediction> findLatestPredictionForMatchup(Long team1Id, Long team2Id) {
        return predictionRepository.findLatestPredictionForMatchup(team1Id, team2Id);
    }
    
    public List<Prediction> getUpcomingPredictions() {
        return predictionRepository.findUpcomingPredictions(LocalDate.now());
    }
    
    public Page<Prediction> getPredictionHistory(Pageable pageable) {
        return predictionRepository.findAllByOrderByCreatedAtDesc(pageable);
    }
    
    public Page<Prediction> getCompletedPredictions(Pageable pageable) {
        return predictionRepository.findCompletedPredictions(pageable);
    }
    
    public Double getOverallModelAccuracy() {
        Double accuracy = predictionRepository.calculateOverallAccuracy();
        return accuracy != null ? accuracy : 0.0;
    }
    
    public List<Prediction> getStalePredictions(int staleDays) {
        LocalDateTime cutoffDate = LocalDateTime.now().minusDays(staleDays);
        return predictionRepository.findStalePredictions(cutoffDate);
    }
    
    public long getPendingPredictionsCount() {
        return predictionRepository.countPendingPredictions();
    }
    
    public Page<Prediction> getPredictionsByTeam(Long teamId, Pageable pageable) {
        return predictionRepository.findPredictionsByTeam(teamId, pageable);
    }
    
    public List<Prediction> getPredictionsInDateRange(LocalDate startDate, LocalDate endDate) {
        return predictionRepository.findPredictionsInDateRange(startDate, endDate);
    }
    
    public Page<Prediction> getPredictionsByModelVersion(String modelVersion, Pageable pageable) {
        return predictionRepository.findPredictionsByModelVersion(modelVersion, pageable);
    }
    
    @Transactional
    public Prediction savePrediction(Prediction prediction) {
        if (prediction.getS3PredictionPath() != null && prediction.getGameDate() != null) {
            prediction.setS3PredictionPath(s3Service.generatePredictionPath(
                prediction.getPredictionUuid(), prediction.getGameDate()));
        }
        if (prediction.getS3ChartPath() != null && prediction.getGameDate() != null) {
            prediction.setS3ChartPath(s3Service.generateChartPath(
                prediction.getPredictionUuid(), prediction.getGameDate()));
        }
        return predictionRepository.save(prediction);
    }
    
    @Transactional
    public void updatePredictionWithActualResults(String predictionUuid, 
                                                Long actualWinnerId, 
                                                Integer actualTeam1Score, 
                                                Integer actualTeam2Score) {
        Optional<Prediction> predictionOpt = predictionRepository.findByPredictionUuid(predictionUuid);
        if (predictionOpt.isPresent()) {
            Prediction prediction = predictionOpt.get();
            prediction.setActualWinnerId(actualWinnerId);
            prediction.setActualTeam1Score(actualTeam1Score);
            prediction.setActualTeam2Score(actualTeam2Score);
            prediction.setPredictionAccuracy(actualWinnerId.equals(prediction.getPredictedWinnerId()));
            predictionRepository.save(prediction);
        }
    }
    
    public Map<String, Object> getPredictionWithS3Data(String predictionUuid) throws IOException {
        Optional<Prediction> predictionOpt = predictionRepository.findByPredictionUuid(predictionUuid);
        if (predictionOpt.isEmpty()) {
            throw new RuntimeException("Prediction not found: " + predictionUuid);
        }
        
        Prediction prediction = predictionOpt.get();
        Map<String, Object> result = new HashMap<>();
        
        result.put("prediction", prediction);
        
        if (prediction.getS3PredictionPath() != null) {
            try {
                Map<String, Object> s3Data = s3Service.getPredictionData(prediction.getS3PredictionPath());
                result.put("s3Data", s3Data);
            } catch (IOException e) {
                result.put("s3DataError", "Failed to load prediction data from S3: " + e.getMessage());
            }
        }
        
        if (prediction.getS3ChartPath() != null) {
            String signedUrl = s3Service.generateSignedUrl(prediction.getS3ChartPath(), 60);
            result.put("chartUrl", signedUrl);
        }
        
        return result;
    }
    
    public Map<String, Object> getModelAccuracyStats() {
        Map<String, Object> stats = new HashMap<>();
        
        Double overallAccuracy = getOverallModelAccuracy();
        stats.put("overallAccuracy", overallAccuracy);
        
        long totalPredictions = predictionRepository.count();
        stats.put("totalPredictions", totalPredictions);
        
        long pendingPredictions = getPendingPredictionsCount();
        stats.put("pendingPredictions", pendingPredictions);
        
        long completedPredictions = totalPredictions - pendingPredictions;
        stats.put("completedPredictions", completedPredictions);
        
        List<Prediction> stalePredictions = getStalePredictions(7);
        stats.put("stalePredictionsCount", stalePredictions.size());
        
        return stats;
    }
    
    public Map<String, Object> createPredictionSummary(Prediction prediction) {
        Map<String, Object> summary = new HashMap<>();
        
        summary.put("predictionId", prediction.getPredictionUuid());
        summary.put("timestamp", prediction.getPredictionGeneratedAt());
        
        Map<String, Object> matchup = new HashMap<>();
        try {
            Optional<Team> team1Opt = teamService.getTeamByNbaApiId(prediction.getTeam1Id());
            Optional<Team> team2Opt = teamService.getTeamByNbaApiId(prediction.getTeam2Id());
            
            if (team1Opt.isPresent() && team2Opt.isPresent()) {
                Team team1 = team1Opt.get();
                Team team2 = team2Opt.get();
                
                Map<String, Object> team1Info = new HashMap<>();
                team1Info.put("id", team1.getNbaApiId());
                team1Info.put("name", team1.getFullName());
                
                Map<String, Object> team2Info = new HashMap<>();
                team2Info.put("id", team2.getNbaApiId());
                team2Info.put("name", team2.getFullName());
                
                matchup.put("team1", team1Info);
                matchup.put("team2", team2Info);
            } else {
                matchup.put("error", "One or both teams not found");
            }
        } catch (Exception e) {
            matchup.put("error", "Could not load team information");
        }
        
        summary.put("matchup", matchup);
        
        Map<String, Object> predictionData = new HashMap<>();
        try {
            Optional<Team> winnerOpt = teamService.getTeamByNbaApiId(prediction.getPredictedWinnerId());
            if (winnerOpt.isPresent()) {
                predictionData.put("winner", winnerOpt.get().getFullName());
            } else {
                predictionData.put("winner", "Team " + prediction.getPredictedWinnerId());
            }
        } catch (Exception e) {
            predictionData.put("winner", "Team " + prediction.getPredictedWinnerId());
        }
        
        predictionData.put("team1_score", prediction.getTeam1PredictedScore());
        predictionData.put("team2_score", prediction.getTeam2PredictedScore());
        predictionData.put("confidence", prediction.getConfidencePercentage());
        
        summary.put("prediction", predictionData);
        
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("model_version", prediction.getModelVersion());
        metadata.put("game_date", prediction.getGameDate());
        
        summary.put("model_metadata", metadata);
        
        if (prediction.getS3ChartPath() != null) {
            summary.put("chart_s3_path", prediction.getS3ChartPath());
        }
        
        return summary;
    }
    
    public boolean isPredictionFresh(String predictionUuid, int maxAgeDays) {
        Optional<Prediction> predictionOpt = predictionRepository.findByPredictionUuid(predictionUuid);
        if (predictionOpt.isEmpty()) {
            return false;
        }
        
        Prediction prediction = predictionOpt.get();
        return !prediction.isPredictionStale(maxAgeDays);
    }
}