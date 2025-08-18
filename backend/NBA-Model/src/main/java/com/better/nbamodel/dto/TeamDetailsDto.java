package com.better.nbamodel.dto;

import com.better.nbamodel.entity.Team;

/**
 * Detailed team DTO with all team information
 */
public class TeamDetailsDto {
    private Long id;
    private Long nbaApiId;
    private String teamCode;
    private String name;
    private String city;
    private String abbreviation;
    private String conference;
    private String division;
    private String primaryColor;
    private String secondaryColor;
    private String displayName;
    private String fullName;
    
    public TeamDetailsDto() {}
    
    public TeamDetailsDto(Team team) {
        this.id = team.getId();
        this.nbaApiId = team.getNbaApiId();
        this.teamCode = team.getTeamCode();
        this.name = team.getName();
        this.city = team.getCity();
        this.abbreviation = team.getAbbreviation();
        this.conference = team.getConference();
        this.division = team.getDivision();
        this.primaryColor = team.getPrimaryColor();
        this.secondaryColor = team.getSecondaryColor();
        this.displayName = team.getFullName();
        this.fullName = team.getFullName();
    }
    
    // Factory method to create from Team entity
    public static TeamDetailsDto fromTeam(Team team) {
        return new TeamDetailsDto(team);
    }
    
    // Getters and setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public Long getNbaApiId() {
        return nbaApiId;
    }
    
    public void setNbaApiId(Long nbaApiId) {
        this.nbaApiId = nbaApiId;
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
    
    public String getDisplayName() {
        return displayName;
    }
    
    public void setDisplayName(String displayName) {
        this.displayName = displayName;
    }
    
    public String getFullName() {
        return fullName;
    }
    
    public void setFullName(String fullName) {
        this.fullName = fullName;
    }
}