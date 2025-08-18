package com.better.nbamodel.dto;

import com.better.nbamodel.entity.Team;

/**
 * Team mapping DTO specifically for ML service integration
 */
public class TeamMappingDto {
    private Long nbaApiId;
    private String name;
    private String abbreviation;
    private String fullName;
    
    public TeamMappingDto() {}
    
    public TeamMappingDto(Long nbaApiId, String name, String city, String abbreviation) {
        this.nbaApiId = nbaApiId;
        this.name = name;
        this.abbreviation = abbreviation;
        this.fullName = city + " " + name;
    }
    
    // Factory method to create from Team entity
    public static TeamMappingDto fromTeam(Team team) {
        return new TeamMappingDto(
            team.getNbaApiId(),
            team.getName(),
            team.getCity(),
            team.getAbbreviation()
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
    
    public String getAbbreviation() {
        return abbreviation;
    }
    
    public void setAbbreviation(String abbreviation) {
        this.abbreviation = abbreviation;
    }
    
    public String getFullName() {
        return fullName;
    }
    
    public void setFullName(String fullName) {
        this.fullName = fullName;
    }
}