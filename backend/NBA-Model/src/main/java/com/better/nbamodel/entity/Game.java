package com.better.nbamodel.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "games")
public class Game {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "home_team_id")
    private Team homeTeam;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "away_team_id")
    private Team awayTeam;
    
    @Column(nullable = false)
    private LocalDateTime gameDate;
    
    private Integer homeScore;
    private Integer awayScore;
    
    @Enumerated(EnumType.STRING)
    private GameStatus status;
    
    private String season;
    
    public Game() {}
    
    public Game(Team homeTeam, Team awayTeam, LocalDateTime gameDate, String season) {
        this.homeTeam = homeTeam;
        this.awayTeam = awayTeam;
        this.gameDate = gameDate;
        this.season = season;
        this.status = GameStatus.SCHEDULED;
    }
    
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public Team getHomeTeam() {
        return homeTeam;
    }
    
    public void setHomeTeam(Team homeTeam) {
        this.homeTeam = homeTeam;
    }
    
    public Team getAwayTeam() {
        return awayTeam;
    }
    
    public void setAwayTeam(Team awayTeam) {
        this.awayTeam = awayTeam;
    }
    
    public LocalDateTime getGameDate() {
        return gameDate;
    }
    
    public void setGameDate(LocalDateTime gameDate) {
        this.gameDate = gameDate;
    }
    
    public Integer getHomeScore() {
        return homeScore;
    }
    
    public void setHomeScore(Integer homeScore) {
        this.homeScore = homeScore;
    }
    
    public Integer getAwayScore() {
        return awayScore;
    }
    
    public void setAwayScore(Integer awayScore) {
        this.awayScore = awayScore;
    }
    
    public GameStatus getStatus() {
        return status;
    }
    
    public void setStatus(GameStatus status) {
        this.status = status;
    }
    
    public String getSeason() {
        return season;
    }
    
    public void setSeason(String season) {
        this.season = season;
    }
    
    public enum GameStatus {
        SCHEDULED, IN_PROGRESS, COMPLETED, POSTPONED, CANCELLED
    }
}