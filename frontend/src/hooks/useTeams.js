import { useState, useEffect } from 'react';
import { teamService } from '../services/teamService';

export const useTeams = () => {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTeams = async () => {
    try {
      setLoading(true);
      setError(null);
      const teamsData = await teamService.getAllTeams();
      setTeams(teamsData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTeams();
  }, []);

  const refetch = () => {
    fetchTeams();
  };

  return {
    teams,
    loading,
    error,
    refetch
  };
};