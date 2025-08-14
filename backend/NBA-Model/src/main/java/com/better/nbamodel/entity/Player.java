package com.better.nbamodel.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "players")
public class Player {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String name;
    
    @Column(nullable = false)
    private String position;
    
    @Column(nullable = false)
    private Integer jerseyNumber;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "team_id")
    private Team team;
    
    private Double pointsPerGame;
    private Double reboundsPerGame;
    private Double assistsPerGame;
    
    public Player() {}
    
    public Player(String name, String position, Integer jerseyNumber) {
        this.name = name;
        this.position = position;
        this.jerseyNumber = jerseyNumber;
    }
    
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getPosition() {
        return position;
    }
    
    public void setPosition(String position) {
        this.position = position;
    }
    
    public Integer getJerseyNumber() {
        return jerseyNumber;
    }
    
    public void setJerseyNumber(Integer jerseyNumber) {
        this.jerseyNumber = jerseyNumber;
    }
    
    public Team getTeam() {
        return team;
    }
    
    public void setTeam(Team team) {
        this.team = team;
    }
    
    public Double getPointsPerGame() {
        return pointsPerGame;
    }
    
    public void setPointsPerGame(Double pointsPerGame) {
        this.pointsPerGame = pointsPerGame;
    }
    
    public Double getReboundsPerGame() {
        return reboundsPerGame;
    }
    
    public void setReboundsPerGame(Double reboundsPerGame) {
        this.reboundsPerGame = reboundsPerGame;
    }
    
    public Double getAssistsPerGame() {
        return assistsPerGame;
    }
    
    public void setAssistsPerGame(Double assistsPerGame) {
        this.assistsPerGame = assistsPerGame;
    }
}