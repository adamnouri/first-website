package com.better.nbamodel.repository;

import com.better.nbamodel.entity.Player;
import com.better.nbamodel.entity.Team;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface  PlayerRepository extends JpaRepository<Player, Long> {
    List<Player> findByTeam(Team team);
    List<Player> findByPosition(String position);
    List<Player> findByNameContainingIgnoreCase(String name);
}