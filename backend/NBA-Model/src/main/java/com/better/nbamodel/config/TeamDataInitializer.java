package com.better.nbamodel.config;

import com.better.nbamodel.entity.Team;
import com.better.nbamodel.service.TeamService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.util.Arrays;
import java.util.List;

@Component
public class TeamDataInitializer implements CommandLineRunner {
    
    private static final Logger logger = LoggerFactory.getLogger(TeamDataInitializer.class);
    
    @Autowired
    private TeamService teamService;
    
    @Override
    public void run(String... args) {
        initializeNBATeams();
    }
    
    private void initializeNBATeams() {
        logger.info("Checking if NBA teams need to be initialized...");
        
        // Check if teams already exist
        if (teamService.getAllTeams().size() >= 30) {
            logger.info("NBA teams already exist in database, skipping initialization");
            return;
        }
        
        logger.info("Initializing NBA teams data...");
        
        List<TeamData> teamsData = Arrays.asList(
            // Eastern Conference - Atlantic Division
            new TeamData("ATL", 1610612737L, "Hawks", "Atlanta", "ATL", "Eastern", "Southeast", "#E03A3E", "#C1D32F"),
            new TeamData("BOS", 1610612738L, "Celtics", "Boston", "BOS", "Eastern", "Atlantic", "#007A33", "#BA9653"),
            new TeamData("BKN", 1610612751L, "Nets", "Brooklyn", "BKN", "Eastern", "Atlantic", "#000000", "#FFFFFF"),
            new TeamData("NYK", 1610612752L, "Knicks", "New York", "NYK", "Eastern", "Atlantic", "#006BB6", "#F58426"),
            new TeamData("PHI", 1610612755L, "76ers", "Philadelphia", "PHI", "Eastern", "Atlantic", "#006BB6", "#ED174C"),
            
            // Eastern Conference - Central Division
            new TeamData("CHI", 1610612741L, "Bulls", "Chicago", "CHI", "Eastern", "Central", "#CE1141", "#000000"),
            new TeamData("CLE", 1610612739L, "Cavaliers", "Cleveland", "CLE", "Eastern", "Central", "#860038", "#041E42"),
            new TeamData("DET", 1610612765L, "Pistons", "Detroit", "DET", "Eastern", "Central", "#C8102E", "#1D42BA"),
            new TeamData("IND", 1610612754L, "Pacers", "Indiana", "IND", "Eastern", "Central", "#002D62", "#FDBB30"),
            new TeamData("MIL", 1610612749L, "Bucks", "Milwaukee", "MIL", "Eastern", "Central", "#00471B", "#EEE1C6"),
            
            // Eastern Conference - Southeast Division
            new TeamData("CHA", 1610612766L, "Hornets", "Charlotte", "CHA", "Eastern", "Southeast", "#1D1160", "#00788C"),
            new TeamData("MIA", 1610612748L, "Heat", "Miami", "MIA", "Eastern", "Southeast", "#98002E", "#F9A01B"),
            new TeamData("ORL", 1610612753L, "Magic", "Orlando", "ORL", "Eastern", "Southeast", "#0077C0", "#C4CED4"),
            new TeamData("WAS", 1610612764L, "Wizards", "Washington", "WAS", "Eastern", "Southeast", "#002B5C", "#E31837"),
            new TeamData("TOR", 1610612761L, "Raptors", "Toronto", "TOR", "Eastern", "Atlantic", "#CE1141", "#000000"),
            
            // Western Conference - Northwest Division
            new TeamData("DEN", 1610612743L, "Nuggets", "Denver", "DEN", "Western", "Northwest", "#0E2240", "#FEC524"),
            new TeamData("MIN", 1610612750L, "Timberwolves", "Minnesota", "MIN", "Western", "Northwest", "#0C2340", "#236192"),
            new TeamData("OKC", 1610612760L, "Thunder", "Oklahoma City", "OKC", "Western", "Northwest", "#007AC1", "#EF3B24"),
            new TeamData("POR", 1610612757L, "Trail Blazers", "Portland", "POR", "Western", "Northwest", "#E03A3E", "#000000"),
            new TeamData("UTA", 1610612762L, "Jazz", "Utah", "UTA", "Western", "Northwest", "#002B5C", "#00471B"),
            
            // Western Conference - Pacific Division
            new TeamData("GSW", 1610612744L, "Warriors", "Golden State", "GSW", "Western", "Pacific", "#1D428A", "#FFC72C"),
            new TeamData("LAC", 1610612746L, "Clippers", "LA", "LAC", "Western", "Pacific", "#C8102E", "#1D428A"),
            new TeamData("LAL", 1610612747L, "Lakers", "Los Angeles", "LAL", "Western", "Pacific", "#552583", "#FDB927"),
            new TeamData("PHX", 1610612756L, "Suns", "Phoenix", "PHX", "Western", "Pacific", "#1D1160", "#E56020"),
            new TeamData("SAC", 1610612758L, "Kings", "Sacramento", "SAC", "Western", "Pacific", "#5A2D81", "#63727A"),
            
            // Western Conference - Southwest Division
            new TeamData("DAL", 1610612742L, "Mavericks", "Dallas", "DAL", "Western", "Southwest", "#00538C", "#002B5E"),
            new TeamData("HOU", 1610612745L, "Rockets", "Houston", "HOU", "Western", "Southwest", "#CE1141", "#000000"),
            new TeamData("MEM", 1610612763L, "Grizzlies", "Memphis", "MEM", "Western", "Southwest", "#5D76A9", "#12173F"),
            new TeamData("NOP", 1610612740L, "Pelicans", "New Orleans", "NOP", "Western", "Southwest", "#0C2340", "#C8102E"),
            new TeamData("SAS", 1610612759L, "Spurs", "San Antonio", "SAS", "Western", "Southwest", "#C4CED4", "#000000")
        );
        
        int savedCount = 0;
        for (TeamData teamData : teamsData) {
            try {
                // Check if team already exists by NBA API ID
                if (!teamService.existsByNbaApiId(teamData.nbaApiId)) {
                    Team team = new Team(
                        teamData.teamCode,
                        teamData.nbaApiId,
                        teamData.name,
                        teamData.city,
                        teamData.abbreviation,
                        teamData.conference,
                        teamData.division,
                        teamData.primaryColor,
                        teamData.secondaryColor
                    );
                    
                    teamService.saveTeam(team);
                    savedCount++;
                    logger.debug("Saved team: {} {}", teamData.city, teamData.name);
                } else {
                    logger.debug("Team already exists: {} {}", teamData.city, teamData.name);
                }
            } catch (Exception e) {
                logger.error("Error saving team {} {}: {}", teamData.city, teamData.name, e.getMessage());
            }
        }
        
        logger.info("NBA teams initialization completed. Saved {} new teams", savedCount);
        logger.info("Total teams in database: {}", teamService.getAllTeams().size());
    }
    
    private static class TeamData {
        final String teamCode;
        final Long nbaApiId;
        final String name;
        final String city;
        final String abbreviation;
        final String conference;
        final String division;
        final String primaryColor;
        final String secondaryColor;
        
        TeamData(String teamCode, Long nbaApiId, String name, String city, String abbreviation,
                String conference, String division, String primaryColor, String secondaryColor) {
            this.teamCode = teamCode;
            this.nbaApiId = nbaApiId;
            this.name = name;
            this.city = city;
            this.abbreviation = abbreviation;
            this.conference = conference;
            this.division = division;
            this.primaryColor = primaryColor;
            this.secondaryColor = secondaryColor;
        }
    }
}