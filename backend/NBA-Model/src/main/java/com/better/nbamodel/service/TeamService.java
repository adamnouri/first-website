package com.better.nbamodel.service;

import com.better.nbamodel.entity.Team;
import com.better.nbamodel.repository.TeamRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

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
}