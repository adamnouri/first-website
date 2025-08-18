package com.better.nbamodel.service;

import com.better.nbamodel.entity.Team;
import com.better.nbamodel.repository.TeamRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class TeamService {
    
    @Autowired
    private TeamRepository teamRepository;
    
    public List<Team> getAllTeams() {
        return teamRepository.findAll();
    }
    
    public Optional<Team> getTeamById(Long id) {
        return teamRepository.findById(id);
    }
    
    public Optional<Team> getTeamByCode(String teamCode) {
        return teamRepository.findByTeamCode(teamCode);
    }
    
    public List<Team> getTeamsByConference(String conference) {
        return teamRepository.findByConference(conference);
    }
    
    public List<Team> getTeamsByDivision(String division) {
        return teamRepository.findByDivision(division);
    }
    
    public Team saveTeam(Team team) {
        return teamRepository.save(team);
    }
    
    public void deleteTeam(Long id) {
        teamRepository.deleteById(id);
    }
    
    public boolean existsByTeamCode(String teamCode) {
        return teamRepository.findByTeamCode(teamCode).isPresent();
    }
    
    // NBA API specific methods
    public Optional<Team> getTeamByNbaApiId(Long nbaApiId) {
        return teamRepository.findByNbaApiId(nbaApiId);
    }
    
    public Optional<Team> getTeamByAbbreviation(String abbreviation) {
        return teamRepository.findByAbbreviation(abbreviation);
    }
    
    public List<Team> getAllTeamsOrderedByConferenceAndDivision() {
        return teamRepository.findAllOrderedByConferenceAndDivision();
    }
    
    public List<Team> searchTeamsByName(String name) {
        return teamRepository.findByNameContainingIgnoreCase(name);
    }
    
    public List<TeamRepository.TeamMapping> getAllTeamMappings() {
        return teamRepository.findAllTeamMappings();
    }
    
    public Map<Long, String> getTeamNamesMap() {
        return teamRepository.findAllTeamMappings()
                .stream()
                .collect(Collectors.toMap(
                    TeamRepository.TeamMapping::getNbaApiId,
                    TeamRepository.TeamMapping::getFullName
                ));
    }
    
    public Map<Long, Team> getTeamsMapByNbaApiId() {
        return teamRepository.findAll()
                .stream()
                .collect(Collectors.toMap(Team::getNbaApiId, team -> team));
    }
    
    public boolean existsByNbaApiId(Long nbaApiId) {
        return teamRepository.existsByNbaApiId(nbaApiId);
    }
    
    public boolean existsByAbbreviation(String abbreviation) {
        return teamRepository.existsByAbbreviation(abbreviation);
    }
    
    // Utility method for ML service integration
    public String getTeamNameByNbaApiId(Long nbaApiId) {
        return getTeamByNbaApiId(nbaApiId)
                .map(Team::getFullName)
                .orElse("Unknown Team");
    }
    
    public String getTeamAbbreviationByNbaApiId(Long nbaApiId) {
        return getTeamByNbaApiId(nbaApiId)
                .map(Team::getAbbreviation)
                .orElse("UNK");
    }
}