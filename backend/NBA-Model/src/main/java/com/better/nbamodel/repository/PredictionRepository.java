package com.better.nbamodel.repository;

import com.better.nbamodel.entity.Prediction;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface PredictionRepository extends JpaRepository<Prediction, Long> {
    
    @Query("SELECT p FROM Prediction p WHERE " +
           "(p.team1Id = :team1Id AND p.team2Id = :team2Id) OR " +
           "(p.team1Id = :team2Id AND p.team2Id = :team1Id) " +
           "ORDER BY p.predictionGeneratedAt DESC")
    Optional<Prediction> findLatestPredictionForMatchup(@Param("team1Id") Long team1Id, 
                                                       @Param("team2Id") Long team2Id);
    
    @Query("SELECT p FROM Prediction p WHERE " +
           "p.gameDate >= :currentDate AND p.actualWinnerId IS NULL " +
           "ORDER BY p.gameDate ASC")
    List<Prediction> findUpcomingPredictions(@Param("currentDate") LocalDate currentDate);
    
    @Query("SELECT p FROM Prediction p WHERE " +
           "p.actualWinnerId IS NOT NULL " +
           "ORDER BY p.gameDate DESC")
    Page<Prediction> findCompletedPredictions(Pageable pageable);
    
    @Query("SELECT " +
           "(CAST(COUNT(p) AS DOUBLE) * 100.0 / " +
           "(SELECT CAST(COUNT(p2) AS DOUBLE) FROM Prediction p2 WHERE p2.actualWinnerId IS NOT NULL)) " +
           "FROM Prediction p WHERE p.predictionAccuracy = true")
    Double calculateOverallAccuracy();
    
    @Query("SELECT p FROM Prediction p WHERE " +
           "p.predictionGeneratedAt < :cutoffDate AND p.actualWinnerId IS NULL")
    List<Prediction> findStalePredictions(@Param("cutoffDate") LocalDateTime cutoffDate);
    
    Optional<Prediction> findByPredictionUuid(String predictionUuid);
    
    Page<Prediction> findAllByOrderByCreatedAtDesc(Pageable pageable);
    
    @Query("SELECT p FROM Prediction p WHERE " +
           "p.team1Id = :teamId OR p.team2Id = :teamId " +
           "ORDER BY p.predictionGeneratedAt DESC")
    Page<Prediction> findPredictionsByTeam(@Param("teamId") Long teamId, Pageable pageable);
    
    @Query("SELECT p FROM Prediction p WHERE " +
           "p.gameDate BETWEEN :startDate AND :endDate " +
           "ORDER BY p.gameDate ASC")
    List<Prediction> findPredictionsInDateRange(@Param("startDate") LocalDate startDate, 
                                              @Param("endDate") LocalDate endDate);
    
    @Query("SELECT COUNT(p) FROM Prediction p WHERE p.actualWinnerId IS NULL")
    long countPendingPredictions();
    
    @Query("SELECT p FROM Prediction p WHERE " +
           "p.modelVersion = :modelVersion " +
           "ORDER BY p.predictionGeneratedAt DESC")
    Page<Prediction> findPredictionsByModelVersion(@Param("modelVersion") String modelVersion, 
                                                 Pageable pageable);
}