package com.better.nbamodel.repository;

import com.better.nbamodel.entity.PlayoffBracket;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Repository for PlayoffBracket entity
 */
@Repository
public interface PlayoffBracketRepository extends JpaRepository<PlayoffBracket, Long> {
    
    /**
     * Find the most recent active bracket for a season
     */
    @Query("SELECT pb FROM PlayoffBracket pb WHERE pb.season = :season AND pb.isActive = true " +
           "ORDER BY pb.generatedAt DESC")
    Optional<PlayoffBracket> findLatestBracketBySeason(@Param("season") String season);
    
    /**
     * Find bracket by bracket ID
     */
    Optional<PlayoffBracket> findByBracketId(String bracketId);
    
    /**
     * Find all active brackets for a season
     */
    @Query("SELECT pb FROM PlayoffBracket pb WHERE pb.season = :season AND pb.isActive = true " +
           "ORDER BY pb.generatedAt DESC")
    List<PlayoffBracket> findActiveBracketsBySeason(@Param("season") String season);
    
    /**
     * Find brackets generated after a certain date
     */
    @Query("SELECT pb FROM PlayoffBracket pb WHERE pb.generatedAt >= :afterDate AND pb.isActive = true " +
           "ORDER BY pb.generatedAt DESC")
    List<PlayoffBracket> findBracketsGeneratedAfter(@Param("afterDate") LocalDateTime afterDate);
    
    /**
     * Count active brackets for a season
     */
    @Query("SELECT COUNT(pb) FROM PlayoffBracket pb WHERE pb.season = :season AND pb.isActive = true")
    Long countActiveBracketsBySeason(@Param("season") String season);
    
    /**
     * Find all brackets ordered by generation date
     */
    @Query("SELECT pb FROM PlayoffBracket pb WHERE pb.isActive = true ORDER BY pb.generatedAt DESC")
    List<PlayoffBracket> findAllActiveBracketsOrderByDate();
    
    /**
     * Deactivate old brackets for a season (keep only the latest N)
     */
    @Query("UPDATE PlayoffBracket pb SET pb.isActive = false WHERE pb.season = :season AND pb.id NOT IN " +
           "(SELECT pb2.id FROM PlayoffBracket pb2 WHERE pb2.season = :season AND pb2.isActive = true " +
           "ORDER BY pb2.generatedAt DESC LIMIT :keepCount)")
    void deactivateOldBrackets(@Param("season") String season, @Param("keepCount") int keepCount);
}