package com.better.nbamodel.repository;

import com.better.nbamodel.entity.Game;
import com.better.nbamodel.entity.Team;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface GameRepository extends JpaRepository<Game, Long> {
    
    List<Game> findBySeason(String season);
    
    List<Game> findByGameDateBetween(LocalDateTime startDate, LocalDateTime endDate);
    
    @Query("SELECT g FROM Game g WHERE g.homeTeam = :team OR g.awayTeam = :team")
    List<Game> findByTeam(@Param("team") Team team);
    
    @Query("SELECT g FROM Game g WHERE (g.homeTeam = :team1 AND g.awayTeam = :team2) OR (g.homeTeam = :team2 AND g.awayTeam = :team1)")
    List<Game> findByTeams(@Param("team1") Team team1, @Param("team2") Team team2);
    
    List<Game> findByStatus(Game.GameStatus status);
}