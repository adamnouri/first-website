package com.better.nbamodel.dto;

import com.better.nbamodel.entity.Team;

/**
 * Basic team DTO for dropdown selections and simple displays
 */
public class TeamBasicDto {
    private Long nbaApiId;
    private String name;
    private String city;
    private String abbreviation;
    private String displayName;
    private String primaryColor;
    
    public TeamBasicDto() {}
    
    public TeamBasicDto(Long nbaApiId, String name, String city, String abbreviation, String primaryColor) {
        this.nbaApiId = nbaApiId;
        this.name = name;
        this.city = city;
        this.abbreviation = abbreviation;
        this.displayName = city + " " + name;
        this.primaryColor = primaryColor;
    }
    
    // Factory method to create from Team entity
    public static TeamBasicDto fromTeam(Team team) {
        return new TeamBasicDto(
            team.getNbaApiId(),
            team.getName(),
            team.getCity(),
            team.getAbbreviation(),
            team.getPrimaryColor()
        );
    }
    
    // Getters and setters
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
    
    public String getDisplayName() {
        return displayName;
    }
    
    public void setDisplayName(String displayName) {
        this.displayName = displayName;
    }
    
    public String getPrimaryColor() {
        return primaryColor;
    }
    
    public void setPrimaryColor(String primaryColor) {
        this.primaryColor = primaryColor;
    }
}