package com.better.nbamodel.repository;

import com.better.nbamodel.entity.ConferenceStanding;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Repository for ConferenceStanding entity
 */
@Repository
public interface ConferenceStandingRepository extends JpaRepository<ConferenceStanding, Long> {
    
    /**
     * Find latest standings by season and conference, ordered by rank
     */
    @Query("SELECT cs FROM ConferenceStanding cs WHERE cs.season = :season AND cs.conference = :conference " +
           "AND cs.standingId = (SELECT MAX(cs2.standingId) FROM ConferenceStanding cs2 WHERE cs2.season = :season AND cs2.conference = :conference) " +
           "ORDER BY cs.rank ASC")
    List<ConferenceStanding> findLatestStandingsBySeasonAndConference(@Param("season") String season, 
                                                                     @Param("conference") String conference);
    
    /**
     * Find all latest standings for a season (both conferences)
     */
    @Query("SELECT cs FROM ConferenceStanding cs WHERE cs.season = :season " +
           "AND cs.standingId IN (SELECT MAX(cs2.standingId) FROM ConferenceStanding cs2 WHERE cs2.season = :season GROUP BY cs2.conference) " +
           "ORDER BY cs.conference ASC, cs.rank ASC")
    List<ConferenceStanding> findLatestStandingsBySeason(@Param("season") String season);
    
    /**
     * Find standings by standing ID
     */
    @Query("SELECT cs FROM ConferenceStanding cs WHERE cs.standingId = :standingId ORDER BY cs.conference ASC, cs.rank ASC")
    List<ConferenceStanding> findByStandingId(@Param("standingId") String standingId);
    
    /**
     * Find team's latest standing in a season
     */
    @Query("SELECT cs FROM ConferenceStanding cs WHERE cs.season = :season AND cs.teamId = :teamId " +
           "ORDER BY cs.generatedAt DESC LIMIT 1")
    Optional<ConferenceStanding> findLatestStandingForTeam(@Param("season") String season, @Param("teamId") Long teamId);
    
    /**
     * Find top N teams by playoff probability in a conference
     */
    @Query("SELECT cs FROM ConferenceStanding cs WHERE cs.season = :season AND cs.conference = :conference " +
           "AND cs.standingId = (SELECT MAX(cs2.standingId) FROM ConferenceStanding cs2 WHERE cs2.season = :season AND cs2.conference = :conference) " +
           "ORDER BY cs.playoffProbability DESC LIMIT :topN")
    List<ConferenceStanding> findTopTeamsByPlayoffProbability(@Param("season") String season, 
                                                             @Param("conference") String conference, 
                                                             @Param("topN") int topN);
    
    /**
     * Find teams with championship odds above threshold
     */
    @Query("SELECT cs FROM ConferenceStanding cs WHERE cs.season = :season " +
           "AND cs.championshipOdds >= :threshold " +
           "AND cs.standingId IN (SELECT MAX(cs2.standingId) FROM ConferenceStanding cs2 WHERE cs2.season = :season GROUP BY cs2.conference) " +
           "ORDER BY cs.championshipOdds DESC")
    List<ConferenceStanding> findTeamsWithChampionshipOddsAbove(@Param("season") String season, 
                                                               @Param("threshold") Double threshold);
    
    /**
     * Find standings generated after a certain date
     */
    @Query("SELECT cs FROM ConferenceStanding cs WHERE cs.generatedAt >= :afterDate " +
           "ORDER BY cs.generatedAt DESC, cs.conference ASC, cs.rank ASC")
    List<ConferenceStanding> findStandingsGeneratedAfter(@Param("afterDate") LocalDateTime afterDate);
    
    /**
     * Get conference statistics for a season
     */
    @Query("SELECT cs.conference, AVG(cs.projectedWins), AVG(cs.playoffProbability), MAX(cs.championshipOdds) " +
           "FROM ConferenceStanding cs WHERE cs.season = :season " +
           "AND cs.standingId IN (SELECT MAX(cs2.standingId) FROM ConferenceStanding cs2 WHERE cs2.season = :season GROUP BY cs2.conference) " +
           "GROUP BY cs.conference")
    List<Object[]> getConferenceStatistics(@Param("season") String season);
    
    /**
     * Delete old standings (keep only latest N per conference per season)
     */
    @Query("DELETE FROM ConferenceStanding cs WHERE cs.season = :season AND cs.conference = :conference " +
           "AND cs.standingId NOT IN (SELECT cs2.standingId FROM ConferenceStanding cs2 WHERE cs2.season = :season AND cs2.conference = :conference " +
           "ORDER BY cs2.generatedAt DESC LIMIT :keepCount)")
    void deleteOldStandings(@Param("season") String season, @Param("conference") String conference, @Param("keepCount") int keepCount);
}