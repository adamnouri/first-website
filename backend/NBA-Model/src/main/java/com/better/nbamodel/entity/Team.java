package com.better.nbamodel.entity;

import jakarta.persistence.*;
import java.util.List;

@Entity
@Table(name = "teams")
public class Team {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(unique = true, nullable = false)
    private String teamCode;
    
    @Column(nullable = false)
    private String name;
    
    @Column(nullable = false)
    private String city;
    
    @Column(nullable = false)
    private String conference;
    
    @Column(nullable = false)
    private String division;
    
    @OneToMany(mappedBy = "team", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Player> players;
    
    public Team() {}
    
    public Team(String teamCode, String name, String city, String conference, String division) {
        this.teamCode = teamCode;
        this.name = name;
        this.city = city;
        this.conference = conference;
        this.division = division;
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
    
    public List<Player> getPlayers() {
        return players;
    }
    
    public void setPlayers(List<Player> players) {
        this.players = players;
    }
}