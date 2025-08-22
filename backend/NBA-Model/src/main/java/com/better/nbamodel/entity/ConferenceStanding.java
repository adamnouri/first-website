package com.better.nbamodel.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * Entity for storing predicted conference standings
 */
@Entity
@Table(name = "conference_standings")
public class ConferenceStanding {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "standing_id", unique = true, nullable = false)
    private String standingId;
    
    @Column(nullable = false)
    private String season;
    
    @Column(nullable = false)
    private String conference;
    
    @Column(name = "team_id", nullable = false)
    private Long teamId;
    
    @Column(name = "team_name", nullable = false)
    private String teamName;
    
    @Column(name = "team_abbreviation")
    private String teamAbbreviation;
    
    @Column(nullable = false)
    private Integer rank;
    
    @Column(name = "projected_wins")
    private Double projectedWins;
    
    @Column(name = "projected_losses")
    private Double projectedLosses;
    
    @Column(name = "win_percentage")
    private Double winPercentage;
    
    @Column(name = "playoff_probability")
    private Double playoffProbability;
    
    @Column(name = "championship_odds")
    private Double championshipOdds;
    
    @Column(name = "simulations_used")
    private Integer simulationsUsed;
    
    @Column(name = "generated_at")
    private LocalDateTime generatedAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // Constructors
    public ConferenceStanding() {}
    
    public ConferenceStanding(String standingId, String season, String conference, Long teamId, 
                             String teamName, String teamAbbreviation, Integer rank, 
                             Double projectedWins, Double projectedLosses, Double winPercentage, 
                             Double playoffProbability, Double championshipOdds, Integer simulationsUsed) {
        this.standingId = standingId;
        this.season = season;
        this.conference = conference;
        this.teamId = teamId;
        this.teamName = teamName;
        this.teamAbbreviation = teamAbbreviation;
        this.rank = rank;
        this.projectedWins = projectedWins;
        this.projectedLosses = projectedLosses;
        this.winPercentage = winPercentage;
        this.playoffProbability = playoffProbability;
        this.championshipOdds = championshipOdds;
        this.simulationsUsed = simulationsUsed;
        this.generatedAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }
    
    // Getters and Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public String getStandingId() {
        return standingId;
    }
    
    public void setStandingId(String standingId) {
        this.standingId = standingId;
    }
    
    public String getSeason() {
        return season;
    }
    
    public void setSeason(String season) {
        this.season = season;
    }
    
    public String getConference() {
        return conference;
    }
    
    public void setConference(String conference) {
        this.conference = conference;
    }
    
    public Long getTeamId() {
        return teamId;
    }
    
    public void setTeamId(Long teamId) {
        this.teamId = teamId;
    }
    
    public String getTeamName() {
        return teamName;
    }
    
    public void setTeamName(String teamName) {
        this.teamName = teamName;
    }
    
    public String getTeamAbbreviation() {
        return teamAbbreviation;
    }
    
    public void setTeamAbbreviation(String teamAbbreviation) {
        this.teamAbbreviation = teamAbbreviation;
    }
    
    public Integer getRank() {
        return rank;
    }
    
    public void setRank(Integer rank) {
        this.rank = rank;
    }
    
    public Double getProjectedWins() {
        return projectedWins;
    }
    
    public void setProjectedWins(Double projectedWins) {
        this.projectedWins = projectedWins;
    }
    
    public Double getProjectedLosses() {
        return projectedLosses;
    }
    
    public void setProjectedLosses(Double projectedLosses) {
        this.projectedLosses = projectedLosses;
    }
    
    public Double getWinPercentage() {
        return winPercentage;
    }
    
    public void setWinPercentage(Double winPercentage) {
        this.winPercentage = winPercentage;
    }
    
    public Double getPlayoffProbability() {
        return playoffProbability;
    }
    
    public void setPlayoffProbability(Double playoffProbability) {
        this.playoffProbability = playoffProbability;
    }
    
    public Double getChampionshipOdds() {
        return championshipOdds;
    }
    
    public void setChampionshipOdds(Double championshipOdds) {
        this.championshipOdds = championshipOdds;
    }
    
    public Integer getSimulationsUsed() {
        return simulationsUsed;
    }
    
    public void setSimulationsUsed(Integer simulationsUsed) {
        this.simulationsUsed = simulationsUsed;
    }
    
    public LocalDateTime getGeneratedAt() {
        return generatedAt;
    }
    
    public void setGeneratedAt(LocalDateTime generatedAt) {
        this.generatedAt = generatedAt;
    }
    
    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }
    
    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
    
    @PrePersist
    protected void onCreate() {
        generatedAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}