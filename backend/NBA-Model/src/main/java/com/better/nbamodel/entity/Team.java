package com.better.nbamodel.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "teams")
public class Team {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(unique = true, nullable = false)
    private String teamCode;
    
    @Column(unique = true, nullable = false, name = "nba_api_id")
    private Long nbaApiId;
    
    @Column(nullable = false)
    private String name;
    
    @Column(nullable = false)
    private String city;
    
    @Column(nullable = false, length = 3)
    private String abbreviation;
    
    @Column(nullable = false)
    private String conference;
    
    @Column(nullable = false)
    private String division;
    
    @Column(name = "primary_color", length = 7)
    private String primaryColor;
    
    @Column(name = "secondary_color", length = 7)
    private String secondaryColor;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @OneToMany(mappedBy = "team", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Player> players;
    
    public Team() {}
    
    public Team(String teamCode, Long nbaApiId, String name, String city, String abbreviation, String conference, String division) {
        this.teamCode = teamCode;
        this.nbaApiId = nbaApiId;
        this.name = name;
        this.city = city;
        this.abbreviation = abbreviation;
        this.conference = conference;
        this.division = division;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }
    
    public Team(String teamCode, Long nbaApiId, String name, String city, String abbreviation, String conference, String division, String primaryColor, String secondaryColor) {
        this(teamCode, nbaApiId, name, city, abbreviation, conference, division);
        this.primaryColor = primaryColor;
        this.secondaryColor = secondaryColor;
    }
    
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public String getTeamCode() {
        return teamCode;
    }
    
    public void setTeamCode(String teamCode) {
        this.teamCode = teamCode;
    }
    
    public Long getNbaApiId() {
        return nbaApiId;
    }
    
    public void setNbaApiId(Long nbaApiId) {
        this.nbaApiId = nbaApiId;
    }
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getCity() {
        return city;
    }
    
    public void setCity(String city) {
        this.city = city;
    }
    
    public String getAbbreviation() {
        return abbreviation;
    }
    
    public void setAbbreviation(String abbreviation) {
        this.abbreviation = abbreviation;
    }
    
    public String getConference() {
        return conference;
    }
    
    public void setConference(String conference) {
        this.conference = conference;
    }
    
    public String getDivision() {
        return division;
    }
    
    public void setDivision(String division) {
        this.division = division;
    }
    
    public String getPrimaryColor() {
        return primaryColor;
    }
    
    public void setPrimaryColor(String primaryColor) {
        this.primaryColor = primaryColor;
    }
    
    public String getSecondaryColor() {
        return secondaryColor;
    }
    
    public void setSecondaryColor(String secondaryColor) {
        this.secondaryColor = secondaryColor;
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
    
    public List<Player> getPlayers() {
        return players;
    }
    
    public void setPlayers(List<Player> players) {
        this.players = players;
    }
    
    // Utility methods
    public String getFullName() {
        return city + " " + name;
    }
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}