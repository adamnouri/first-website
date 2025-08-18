package com.better.nbamodel.repository;

import com.better.nbamodel.entity.Team;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.Optional;
import java.util.List;

@Repository
public interface TeamRepository extends JpaRepository<Team, Long> {
    Optional<Team> findByTeamCode(String teamCode);
    Optional<Team> findByNbaApiId(Long nbaApiId);
    Optional<Team> findByAbbreviation(String abbreviation);
    List<Team> findByConference(String conference);
    List<Team> findByDivision(String division);
    
    @Query("SELECT t FROM Team t WHERE LOWER(t.name) LIKE LOWER(CONCAT('%', :name, '%')) OR LOWER(t.city) LIKE LOWER(CONCAT('%', :name, '%'))")
    List<Team> findByNameContainingIgnoreCase(@Param("name") String name);
    
    @Query("SELECT t FROM Team t ORDER BY t.conference, t.division, t.name")
    List<Team> findAllOrderedByConferenceAndDivision();
    
    @Query("SELECT t.nbaApiId as nbaApiId, t.name as name, t.city as city, t.abbreviation as abbreviation FROM Team t")
    List<TeamMapping> findAllTeamMappings();
    
    boolean existsByNbaApiId(Long nbaApiId);
    boolean existsByAbbreviation(String abbreviation);
    
    // Interface for projection
    interface TeamMapping {
        Long getNbaApiId();
        String getName();
        String getCity();
        String getAbbreviation();
        
        default String getFullName() {
            return getCity() + " " + getName();
        }
    }
}