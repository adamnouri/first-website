package com.better.nbamodel.repository;

import com.better.nbamodel.entity.Team;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;
import java.util.List;

@Repository
public interface TeamRepository extends JpaRepository<Team, Long> {
    Optional<Team> findByTeamCode(String teamCode);
    List<Team> findByConference(String conference);
    List<Team> findByDivision(String division);
}