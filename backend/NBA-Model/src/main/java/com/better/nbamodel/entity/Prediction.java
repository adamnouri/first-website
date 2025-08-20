package com.better.nbamodel.entity;

import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "predictions")
public class Prediction {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "prediction_uuid", unique = true, nullable = false, length = 50)
    private String predictionUuid;
    
    @Column(name = "team1_id", nullable = false)
    private Long team1Id;
    
    @Column(name = "team2_id", nullable = false)
    private Long team2Id;
    
    @Column(name = "predicted_winner_id", nullable = false)
    private Long predictedWinnerId;
    
    @Column(name = "team1_predicted_score")
    private Integer team1PredictedScore;
    
    @Column(name = "team2_predicted_score")
    private Integer team2PredictedScore;
    
    @Column(name = "confidence_percentage", precision = 5, scale = 2)
    private BigDecimal confidencePercentage;
    
    @Column(name = "s3_prediction_path", length = 500)
    private String s3PredictionPath;
    
    @Column(name = "s3_chart_path", length = 500)
    private String s3ChartPath;
    
    @Column(name = "model_version", length = 20)
    private String modelVersion;
    
    @Column(name = "game_date")
    private LocalDate gameDate;
    
    @Column(name = "prediction_generated_at")
    private LocalDateTime predictionGeneratedAt;
    
    @Column(name = "actual_winner_id")
    private Long actualWinnerId;
    
    @Column(name = "actual_team1_score")
    private Integer actualTeam1Score;
    
    @Column(name = "actual_team2_score")
    private Integer actualTeam2Score;
    
    @Column(name = "prediction_accuracy")
    private Boolean predictionAccuracy;
    
    @CreationTimestamp
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "team1_id", referencedColumnName = "nba_api_id", insertable = false, updatable = false)
    private Team team1;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "team2_id", referencedColumnName = "nba_api_id", insertable = false, updatable = false)
    private Team team2;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "predicted_winner_id", referencedColumnName = "nba_api_id", insertable = false, updatable = false)
    private Team predictedWinner;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "actual_winner_id", referencedColumnName = "nba_api_id", insertable = false, updatable = false)
    private Team actualWinner;
    
    public Prediction() {}
    
    public Prediction(String predictionUuid, Long team1Id, Long team2Id, Long predictedWinnerId) {
        this.predictionUuid = predictionUuid;
        this.team1Id = team1Id;
        this.team2Id = team2Id;
        this.predictedWinnerId = predictedWinnerId;
        this.predictionGeneratedAt = LocalDateTime.now();
    }
    
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public String getPredictionUuid() {
        return predictionUuid;
    }
    
    public void setPredictionUuid(String predictionUuid) {
        this.predictionUuid = predictionUuid;
    }
    
    public Long getTeam1Id() {
        return team1Id;
    }
    
    public void setTeam1Id(Long team1Id) {
        this.team1Id = team1Id;
    }
    
    public Long getTeam2Id() {
        return team2Id;
    }
    
    public void setTeam2Id(Long team2Id) {
        this.team2Id = team2Id;
    }
    
    public Long getPredictedWinnerId() {
        return predictedWinnerId;
    }
    
    public void setPredictedWinnerId(Long predictedWinnerId) {
        this.predictedWinnerId = predictedWinnerId;
    }
    
    public Integer getTeam1PredictedScore() {
        return team1PredictedScore;
    }
    
    public void setTeam1PredictedScore(Integer team1PredictedScore) {
        this.team1PredictedScore = team1PredictedScore;
    }
    
    public Integer getTeam2PredictedScore() {
        return team2PredictedScore;
    }
    
    public void setTeam2PredictedScore(Integer team2PredictedScore) {
        this.team2PredictedScore = team2PredictedScore;
    }
    
    public BigDecimal getConfidencePercentage() {
        return confidencePercentage;
    }
    
    public void setConfidencePercentage(BigDecimal confidencePercentage) {
        this.confidencePercentage = confidencePercentage;
    }
    
    public String getS3PredictionPath() {
        return s3PredictionPath;
    }
    
    public void setS3PredictionPath(String s3PredictionPath) {
        this.s3PredictionPath = s3PredictionPath;
    }
    
    public String getS3ChartPath() {
        return s3ChartPath;
    }
    
    public void setS3ChartPath(String s3ChartPath) {
        this.s3ChartPath = s3ChartPath;
    }
    
    public String getModelVersion() {
        return modelVersion;
    }
    
    public void setModelVersion(String modelVersion) {
        this.modelVersion = modelVersion;
    }
    
    public LocalDate getGameDate() {
        return gameDate;
    }
    
    public void setGameDate(LocalDate gameDate) {
        this.gameDate = gameDate;
    }
    
    public LocalDateTime getPredictionGeneratedAt() {
        return predictionGeneratedAt;
    }
    
    public void setPredictionGeneratedAt(LocalDateTime predictionGeneratedAt) {
        this.predictionGeneratedAt = predictionGeneratedAt;
    }
    
    public Long getActualWinnerId() {
        return actualWinnerId;
    }
    
    public void setActualWinnerId(Long actualWinnerId) {
        this.actualWinnerId = actualWinnerId;
    }
    
    public Integer getActualTeam1Score() {
        return actualTeam1Score;
    }
    
    public void setActualTeam1Score(Integer actualTeam1Score) {
        this.actualTeam1Score = actualTeam1Score;
    }
    
    public Integer getActualTeam2Score() {
        return actualTeam2Score;
    }
    
    public void setActualTeam2Score(Integer actualTeam2Score) {
        this.actualTeam2Score = actualTeam2Score;
    }
    
    public Boolean getPredictionAccuracy() {
        return predictionAccuracy;
    }
    
    public void setPredictionAccuracy(Boolean predictionAccuracy) {
        this.predictionAccuracy = predictionAccuracy;
    }
    
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    
    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }
    
    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
    
    public Team getTeam1() {
        return team1;
    }
    
    public void setTeam1(Team team1) {
        this.team1 = team1;
    }
    
    public Team getTeam2() {
        return team2;
    }
    
    public void setTeam2(Team team2) {
        this.team2 = team2;
    }
    
    public Team getPredictedWinner() {
        return predictedWinner;
    }
    
    public void setPredictedWinner(Team predictedWinner) {
        this.predictedWinner = predictedWinner;
    }
    
    public Team getActualWinner() {
        return actualWinner;
    }
    
    public void setActualWinner(Team actualWinner) {
        this.actualWinner = actualWinner;
    }
    
    @PrePersist
    protected void onCreate() {
        if (predictionGeneratedAt == null) {
            predictionGeneratedAt = LocalDateTime.now();
        }
    }
    
    @PreUpdate
    protected void onUpdate() {
        if (actualWinnerId != null && predictedWinnerId != null) {
            predictionAccuracy = actualWinnerId.equals(predictedWinnerId);
        }
    }
    
    public String getMatchupDescription() {
        if (team1 != null && team2 != null) {
            return team1.getFullName() + " vs " + team2.getFullName();
        }
        return "Team " + team1Id + " vs Team " + team2Id;
    }
    
    public boolean isPredictionStale(int staleDays) {
        return predictionGeneratedAt.isBefore(LocalDateTime.now().minusDays(staleDays));
    }
}