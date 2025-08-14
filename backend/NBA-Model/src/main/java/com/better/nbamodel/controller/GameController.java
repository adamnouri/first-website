package com.better.nbamodel.controller;

import com.better.nbamodel.entity.Game;
import com.better.nbamodel.entity.Team;
import com.better.nbamodel.service.GameService;
import com.better.nbamodel.service.TeamService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/v1/games")
public class GameController {

    @Autowired
    private GameService gameService;

    @Autowired
    private TeamService teamService;

    @GetMapping
    public ResponseEntity<List<Game>> getAllGames() {
        List<Game> games = gameService.getAllGames();
        return ResponseEntity.ok(games);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Game> getGameById(@PathVariable Long id) {
        Optional<Game> game = gameService.getGameById(id);
        return game.map(ResponseEntity::ok)
                  .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/season/{season}")
    public ResponseEntity<List<Game>> getGamesBySeason(@PathVariable String season) {
        List<Game> games = gameService.getGamesBySeason(season);
        return ResponseEntity.ok(games);
    }

    @GetMapping("/date-range")
    public ResponseEntity<List<Game>> getGamesByDateRange(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate) {
        List<Game> games = gameService.getGamesByDateRange(startDate, endDate);
        return ResponseEntity.ok(games);
    }

    @GetMapping("/team/{teamId}")
    public ResponseEntity<List<Game>> getGamesByTeam(@PathVariable Long teamId) {
        Optional<Team> team = teamService.getTeamById(teamId);
        if (team.isPresent()) {
            List<Game> games = gameService.getGamesByTeam(team.get());
            return ResponseEntity.ok(games);
        }
        return ResponseEntity.notFound().build();
    }

    @GetMapping("/status/{status}")
    public ResponseEntity<List<Game>> getGamesByStatus(@PathVariable Game.GameStatus status) {
        List<Game> games = gameService.getGamesByStatus(status);
        return ResponseEntity.ok(games);
    }

    @PostMapping
    public ResponseEntity<Game> createGame(@RequestBody Game game) {
        Game savedGame = gameService.saveGame(game);
        return ResponseEntity.status(HttpStatus.CREATED).body(savedGame);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Game> updateGame(@PathVariable Long id, @RequestBody Game game) {
        Optional<Game> existingGame = gameService.getGameById(id);
        if (existingGame.isPresent()) {
            game.setId(id);
            Game updatedGame = gameService.saveGame(game);
            return ResponseEntity.ok(updatedGame);
        }
        return ResponseEntity.notFound().build();
    }

    @PutMapping("/{id}/score")
    public ResponseEntity<Game> updateGameScore(
            @PathVariable Long id,
            @RequestParam Integer homeScore,
            @RequestParam Integer awayScore) {
        Game updatedGame = gameService.updateGameScore(id, homeScore, awayScore);
        if (updatedGame != null) {
            return ResponseEntity.ok(updatedGame);
        }
        return ResponseEntity.notFound().build();
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteGame(@PathVariable Long id) {
        Optional<Game> game = gameService.getGameById(id);
        if (game.isPresent()) {
            gameService.deleteGame(id);
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.notFound().build();
    }
}