package com.better.nbamodel.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * Entity for storing playoff bracket data
 */
@Entity
@Table(name = "playoff_brackets")
public class PlayoffBracket {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(unique = true, nullable = false)
    private String bracketId;
    
    @Column(nullable = false)
    private String season;
    
    @Column(name = "eastern_teams", columnDefinition = "TEXT")
    private String easternTeams; // JSON string of Eastern Conference teams
    
    @Column(name = "western_teams", columnDefinition = "TEXT")
    private String westernTeams; // JSON string of Western Conference teams
    
    @Column(name = "bracket_data", columnDefinition = "TEXT")
    private String bracketData; // JSON string of complete bracket structure
    
    @Column(name = "championship_odds", columnDefinition = "TEXT")
    private String championshipOdds; // JSON string of championship probabilities
    
    @Column(name = "simulations_used")
    private Integer simulationsUsed;
    
    @Column(name = "generated_at")
    private LocalDateTime generatedAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @Column(name = "is_active")
    private Boolean isActive = true;
    
    // Constructors
    public PlayoffBracket() {}
    
    public PlayoffBracket(String bracketId, String season, String easternTeams, String westernTeams, 
                         String bracketData, String championshipOdds, Integer simulationsUsed) {
        this.bracketId = bracketId;
        this.season = season;
        this.easternTeams = easternTeams;
        this.westernTeams = westernTeams;
        this.bracketData = bracketData;
        this.championshipOdds = championshipOdds;
        this.simulationsUsed = simulationsUsed;
        this.generatedAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        this.isActive = true;
    }
    
    // Getters and Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public String getBracketId() {
        return bracketId;
    }
    
    public void setBracketId(String bracketId) {
        this.bracketId = bracketId;
    }
    
    public String getSeason() {
        return season;
    }
    
    public void setSeason(String season) {
        this.season = season;
    }
    
    public String getEasternTeams() {
        return easternTeams;
    }
    
    public void setEasternTeams(String easternTeams) {
        this.easternTeams = easternTeams;
    }
    
    public String getWesternTeams() {
        return westernTeams;
    }
    
    public void setWesternTeams(String westernTeams) {
        this.westernTeams = westernTeams;
    }
    
    public String getBracketData() {
        return bracketData;
    }
    
    public void setBracketData(String bracketData) {
        this.bracketData = bracketData;
    }
    
    public String getChampionshipOdds() {
        return championshipOdds;
    }
    
    public void setChampionshipOdds(String championshipOdds) {
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
    
    public Boolean getIsActive() {
        return isActive;
    }
    
    public void setIsActive(Boolean isActive) {
        this.isActive = isActive;
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