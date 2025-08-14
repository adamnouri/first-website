package com.better.nbamodel.service;

import com.better.nbamodel.entity.Game;
import com.better.nbamodel.entity.Team;
import com.better.nbamodel.repository.GameRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class GameService {
    
    @Autowired
    private GameRepository gameRepository;
    
    public List<Game> getAllGames() {
        return gameRepository.findAll();
    }
    
    public Optional<Game> getGameById(Long id) {
        return gameRepository.findById(id);
    }
    
    public List<Game> getGamesBySeason(String season) {
        return gameRepository.findBySeason(season);
    }
    
    public List<Game> getGamesByDateRange(LocalDateTime startDate, LocalDateTime endDate) {
        return gameRepository.findByGameDateBetween(startDate, endDate);
    }
    
    public List<Game> getGamesByTeam(Team team) {
        return gameRepository.findByTeam(team);
    }
    
    public List<Game> getGamesBetweenTeams(Team team1, Team team2) {
        return gameRepository.findByTeams(team1, team2);
    }
    
    public List<Game> getGamesByStatus(Game.GameStatus status) {
        return gameRepository.findByStatus(status);
    }
    
    public Game saveGame(Game game) {
        return gameRepository.save(game);
    }
    
    public void deleteGame(Long id) {
        gameRepository.deleteById(id);
    }
    
    public Game updateGameScore(Long gameId, Integer homeScore, Integer awayScore) {
        Optional<Game> gameOpt = gameRepository.findById(gameId);
        if (gameOpt.isPresent()) {
            Game game = gameOpt.get();
            game.setHomeScore(homeScore);
            game.setAwayScore(awayScore);
            game.setStatus(Game.GameStatus.COMPLETED);
            return gameRepository.save(game);
        }
        return null;
    }
}