package com.better.nbamodel.controller;

import com.better.nbamodel.entity.Team;
import com.better.nbamodel.service.TeamService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
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
}