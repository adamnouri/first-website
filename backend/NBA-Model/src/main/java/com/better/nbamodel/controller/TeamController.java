package com.better.nbamodel.controller;

import com.better.nbamodel.entity.Team;
import com.better.nbamodel.repository.TeamRepository;
import com.better.nbamodel.service.TeamService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/v1/teams")
public class TeamController {

    @Autowired
    private TeamService teamService;

    @GetMapping
    public ResponseEntity<List<Team>> getAllTeams() {
        List<Team> teams = teamService.getAllTeams();
        return ResponseEntity.ok(teams);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Team> getTeamById(@PathVariable Long id) {
        Optional<Team> team = teamService.getTeamById(id);
        return team.map(ResponseEntity::ok)
                  .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/code/{teamCode}")
    public ResponseEntity<Team> getTeamByCode(@PathVariable String teamCode) {
        Optional<Team> team = teamService.getTeamByCode(teamCode);
        return team.map(ResponseEntity::ok)
                  .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/conference/{conference}")
    public ResponseEntity<List<Team>> getTeamsByConference(@PathVariable String conference) {
        List<Team> teams = teamService.getTeamsByConference(conference);
        return ResponseEntity.ok(teams);
    }

    @GetMapping("/division/{division}")
    public ResponseEntity<List<Team>> getTeamsByDivision(@PathVariable String division) {
        List<Team> teams = teamService.getTeamsByDivision(division);
        return ResponseEntity.ok(teams);
    }

    @PostMapping
    public ResponseEntity<Team> createTeam(@RequestBody Team team) {
        if (teamService.existsByTeamCode(team.getTeamCode())) {
            return ResponseEntity.status(HttpStatus.CONFLICT).build();
        }
        Team savedTeam = teamService.saveTeam(team);
        return ResponseEntity.status(HttpStatus.CREATED).body(savedTeam);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Team> updateTeam(@PathVariable Long id, @RequestBody Team team) {
        Optional<Team> existingTeam = teamService.getTeamById(id);
        if (existingTeam.isPresent()) {
            team.setId(id);
            Team updatedTeam = teamService.saveTeam(team);
            return ResponseEntity.ok(updatedTeam);
        }
        return ResponseEntity.notFound().build();
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTeam(@PathVariable Long id) {
        Optional<Team> team = teamService.getTeamById(id);
        if (team.isPresent()) {
            teamService.deleteTeam(id);
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.notFound().build();
    }
    
    // NBA API specific endpoints
    @GetMapping("/nba/{nbaApiId}")
    public ResponseEntity<Team> getTeamByNbaApiId(@PathVariable Long nbaApiId) {
        Optional<Team> team = teamService.getTeamByNbaApiId(nbaApiId);
        return team.map(ResponseEntity::ok)
                  .orElse(ResponseEntity.notFound().build());
    }
    
    @GetMapping("/abbreviation/{abbreviation}")
    public ResponseEntity<Team> getTeamByAbbreviation(@PathVariable String abbreviation) {
        Optional<Team> team = teamService.getTeamByAbbreviation(abbreviation);
        return team.map(ResponseEntity::ok)
                  .orElse(ResponseEntity.notFound().build());
    }
    
    @GetMapping("/search")
    public ResponseEntity<List<Team>> searchTeams(@RequestParam String name) {
        List<Team> teams = teamService.searchTeamsByName(name);
        return ResponseEntity.ok(teams);
    }
    
    @GetMapping("/ordered")
    public ResponseEntity<List<Team>> getTeamsOrderedByConferenceAndDivision() {
        List<Team> teams = teamService.getAllTeamsOrderedByConferenceAndDivision();
        return ResponseEntity.ok(teams);
    }
    
    @GetMapping("/mappings")
    public ResponseEntity<List<TeamRepository.TeamMapping>> getTeamMappings() {
        List<TeamRepository.TeamMapping> mappings = teamService.getAllTeamMappings();
        return ResponseEntity.ok(mappings);
    }
    
    @GetMapping("/names-map")
    public ResponseEntity<Map<Long, String>> getTeamNamesMap() {
        Map<Long, String> namesMap = teamService.getTeamNamesMap();
        return ResponseEntity.ok(namesMap);
    }
    
    @GetMapping("/dropdown")
    public ResponseEntity<List<TeamRepository.TeamMapping>> getTeamsForDropdown() {
        List<TeamRepository.TeamMapping> teams = teamService.getAllTeamMappings();
        return ResponseEntity.ok(teams);
    }
    
    // Utility endpoints for ML service
    @GetMapping("/nba/{nbaApiId}/name")
    public ResponseEntity<String> getTeamNameByNbaApiId(@PathVariable Long nbaApiId) {
        String teamName = teamService.getTeamNameByNbaApiId(nbaApiId);
        if (!"Unknown Team".equals(teamName)) {
            return ResponseEntity.ok(teamName);
        }
        return ResponseEntity.notFound().build();
    }
    
    @GetMapping("/nba/{nbaApiId}/abbreviation")
    public ResponseEntity<String> getTeamAbbreviationByNbaApiId(@PathVariable Long nbaApiId) {
        String abbreviation = teamService.getTeamAbbreviationByNbaApiId(nbaApiId);
        if (!"UNK".equals(abbreviation)) {
            return ResponseEntity.ok(abbreviation);
        }
        return ResponseEntity.notFound().build();
    }
}