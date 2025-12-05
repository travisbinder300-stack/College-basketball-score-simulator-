#!/usr/bin/env python3
"""
NHL Spread and Total Analytics System
Provides predictions with 70%+ confidence using real NHL data
"""

import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from scipy import stats
from bs4 import BeautifulSoup
import numpy as np


class NHLDataFetcher:
    """Fetches real NHL data from the NHL API, MoneyPuck, and StatMuse"""
    
    def __init__(self):
        self.base_url = "https://api-web.nhle.com/v1"
        self.standings_url = f"{self.base_url}/standings/now"
        self.moneypuck_url = "https://moneypuck.com/power.htm"
        self.statmuse_url = "https://www.statmuse.com/nhl/ask/nhl-team-stats-last-10-games"
        self._moneypuck_cache = None
        self._statmuse_cache = None
        
    def get_standings(self) -> Dict:
        """Fetch current NHL standings"""
        try:
            response = requests.get(self.standings_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching standings: {e}")
            return {}
    
    def get_team_stats(self, team_abbr: str) -> Dict:
        """Fetch team statistics"""
        try:
            url = f"{self.base_url}/club-stats/{team_abbr}/now"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching team stats for {team_abbr}: {e}")
            return {}
    
    def get_schedule(self, date: str = None) -> Dict:
        """Fetch schedule for a specific date (YYYY-MM-DD format)"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        try:
            url = f"{self.base_url}/schedule/{date}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching schedule: {e}")
            return {}
    
    def get_moneypuck_rankings(self) -> Dict[str, float]:
        """
        Fetch MoneyPuck power rankings
        Returns dict mapping team abbreviations to power ranking scores
        """
        if self._moneypuck_cache is not None:
            return self._moneypuck_cache
            
        try:
            response = requests.get(self.moneypuck_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find the power rankings table
            rankings = {}
            table = soup.find('table')
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        # Extract team name and power ranking score
                        team_cell = cells[1].text.strip() if len(cells) > 1 else ''
                        score_cell = cells[2].text.strip() if len(cells) > 2 else '0'
                        
                        # Map full team names to abbreviations
                        team_abbr = self._map_moneypuck_team_to_abbr(team_cell)
                        if team_abbr:
                            try:
                                score = float(score_cell)
                                rankings[team_abbr] = score
                            except ValueError:
                                continue
            
            self._moneypuck_cache = rankings
            return rankings
            
        except Exception as e:
            print(f"Error fetching MoneyPuck rankings: {e}")
            return {}
    
    def _map_moneypuck_team_to_abbr(self, team_name: str) -> Optional[str]:
        """Map MoneyPuck team names to NHL abbreviations"""
        team_mapping = {
            'Anaheim Ducks': 'ANA', 'Arizona Coyotes': 'ARI', 'Boston Bruins': 'BOS',
            'Buffalo Sabres': 'BUF', 'Calgary Flames': 'CGY', 'Carolina Hurricanes': 'CAR',
            'Chicago Blackhawks': 'CHI', 'Colorado Avalanche': 'COL', 'Columbus Blue Jackets': 'CBJ',
            'Dallas Stars': 'DAL', 'Detroit Red Wings': 'DET', 'Edmonton Oilers': 'EDM',
            'Florida Panthers': 'FLA', 'Los Angeles Kings': 'LAK', 'Minnesota Wild': 'MIN',
            'Montréal Canadiens': 'MTL', 'Montreal Canadiens': 'MTL', 'Nashville Predators': 'NSH',
            'New Jersey Devils': 'NJD', 'New York Islanders': 'NYI', 'New York Rangers': 'NYR',
            'Ottawa Senators': 'OTT', 'Philadelphia Flyers': 'PHI', 'Pittsburgh Penguins': 'PIT',
            'San Jose Sharks': 'SJS', 'Seattle Kraken': 'SEA', 'St. Louis Blues': 'STL',
            'Tampa Bay Lightning': 'TBL', 'Toronto Maple Leafs': 'TOR', 'Vancouver Canucks': 'VAN',
            'Vegas Golden Knights': 'VGK', 'Washington Capitals': 'WSH', 'Winnipeg Jets': 'WPG',
            'Utah Hockey Club': 'UTA'
        }
        return team_mapping.get(team_name)
    
    def get_recent_form(self, team_abbr: str) -> Dict[str, float]:
        """
        Fetch recent form data (last 10 games) from StatMuse or NHL API
        Returns dict with recent performance metrics
        """
        if self._statmuse_cache and team_abbr in self._statmuse_cache:
            return self._statmuse_cache.get(team_abbr, {})
        
        try:
            # Try to fetch from NHL API game log (last 10 games)
            # Note: This uses team game log endpoint which may have different structure
            url = f"{self.base_url}/club-schedule-season/{team_abbr}/now"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract last 10 games
            games = data.get('games', [])
            recent_games = [g for g in games if g.get('gameState') in ['OFF', 'FINAL']][-10:]
            
            if not recent_games:
                return {}
            
            # Calculate recent form metrics
            wins = 0
            goals_for = 0
            goals_against = 0
            
            for game in recent_games:
                team_score = 0
                opp_score = 0
                
                # Determine if home or away
                if game.get('homeTeam', {}).get('abbrev') == team_abbr:
                    team_score = game.get('homeTeam', {}).get('score', 0)
                    opp_score = game.get('awayTeam', {}).get('score', 0)
                else:
                    team_score = game.get('awayTeam', {}).get('score', 0)
                    opp_score = game.get('homeTeam', {}).get('score', 0)
                
                goals_for += team_score
                goals_against += opp_score
                
                if team_score > opp_score:
                    wins += 1
            
            recent_form = {
                'games_played': len(recent_games),
                'wins': wins,
                'win_pct': wins / len(recent_games) if recent_games else 0,
                'goals_for': goals_for,
                'goals_against': goals_against,
                'goal_diff': goals_for - goals_against,
                'goals_per_game': goals_for / len(recent_games) if recent_games else 0,
                'goals_allowed_per_game': goals_against / len(recent_games) if recent_games else 0
            }
            
            # Cache the result
            if self._statmuse_cache is None:
                self._statmuse_cache = {}
            self._statmuse_cache[team_abbr] = recent_form
            
            return recent_form
            
        except Exception as e:
            print(f"Error fetching recent form for {team_abbr}: {e}")
            return {}


class NHLAnalytics:
    """Analyzes NHL data and provides spread and total predictions"""
    
    def __init__(self, use_moneypuck: bool = False, use_recent_form: bool = False):
        """
        Initialize NHL Analytics
        
        Args:
            use_moneypuck: If True, incorporates MoneyPuck power rankings into team strength
            use_recent_form: If True, incorporates last 10 games performance into team strength
        """
        self.data_fetcher = NHLDataFetcher()
        self.confidence_level = 0.70  # 70% confidence target
        self.use_moneypuck = use_moneypuck
        self.use_recent_form = use_recent_form
        self._moneypuck_rankings = None
        
    def calculate_team_strength(self, team_data: Dict, team_abbr: str = None) -> float:
        """
        Calculate team strength rating based on multiple factors
        Returns a normalized strength score (0-100)
        
        Args:
            team_data: Team statistics from NHL API
            team_abbr: Team abbreviation (required if use_moneypuck or use_recent_form is True)
        """
        if not team_data:
            return 50.0  # neutral rating
        
        # Extract key metrics
        wins = team_data.get('wins', 0)
        losses = team_data.get('losses', 0)
        ot_losses = team_data.get('otLosses', 0)
        goals_for = team_data.get('goalFor', 0)
        goals_against = team_data.get('goalAgainst', 0)
        
        # Calculate win percentage (OT losses count as half win)
        total_games = wins + losses + ot_losses
        if total_games == 0:
            return 50.0
        
        win_pct = (wins + 0.5 * ot_losses) / total_games
        
        # Calculate goal differential per game
        goal_diff_per_game = (goals_for - goals_against) / total_games if total_games > 0 else 0
        
        # Normalize goal differential (typical range -2 to +2)
        goal_diff_normalized = 50 + (goal_diff_per_game * 10)
        goal_diff_normalized = max(0, min(100, goal_diff_normalized))
        
        # Base strength: 60% win percentage, 40% goal differential
        base_strength = (win_pct * 60) + (goal_diff_normalized * 0.4)
        
        # Calculate recent form strength if enabled
        recent_form_strength = None
        if self.use_recent_form and team_abbr:
            recent_form = self.data_fetcher.get_recent_form(team_abbr)
            if recent_form and recent_form.get('games_played', 0) >= 5:
                # Calculate recent form strength
                recent_win_pct = recent_form.get('win_pct', 0.5)
                recent_goal_diff = recent_form.get('goal_diff', 0)
                recent_gpg = recent_form.get('goals_per_game', 0)
                
                # Normalize recent goal differential (typical range -10 to +10 over 10 games)
                recent_goal_diff_normalized = 50 + (recent_goal_diff * 2.5)
                recent_goal_diff_normalized = max(0, min(100, recent_goal_diff_normalized))
                
                # Recent form strength: 70% recent win%, 30% recent goal differential
                recent_form_strength = (recent_win_pct * 70) + (recent_goal_diff_normalized * 0.3)
        
        # Blend season stats with recent form if available
        if recent_form_strength is not None:
            # 60% season data, 40% last 10 games (captures momentum)
            base_strength = (base_strength * 0.6) + (recent_form_strength * 0.4)
        
        # Optionally incorporate MoneyPuck rankings
        if self.use_moneypuck and team_abbr:
            if self._moneypuck_rankings is None:
                self._moneypuck_rankings = self.data_fetcher.get_moneypuck_rankings()
            
            if team_abbr in self._moneypuck_rankings:
                # MoneyPuck rankings are typically 0-1 scale, convert to 0-100
                moneypuck_strength = self._moneypuck_rankings[team_abbr] * 100
                # Blend: 70% our calculation, 30% MoneyPuck
                strength = (base_strength * 0.7) + (moneypuck_strength * 0.3)
                return strength
        
        return base_strength
    
    def predict_spread(self, home_team: str, away_team: str) -> Dict:
        """
        Predict the spread for a matchup
        Returns spread with confidence interval
        """
        # Fetch team data
        home_data = self._get_team_record(home_team)
        away_data = self._get_team_record(away_team)
        
        # Calculate team strengths (pass team abbreviations for MoneyPuck integration)
        home_strength = self.calculate_team_strength(home_data, home_team)
        away_strength = self.calculate_team_strength(away_data, away_team)
        
        # Home ice advantage (approximately 0.3 goals in NHL)
        home_advantage = 3.0
        
        # Calculate expected spread
        spread = (home_strength - away_strength) / 10 + home_advantage
        
        # Calculate confidence interval (70% confidence)
        # Standard deviation for NHL spreads is approximately 1.5 goals
        std_dev = 1.5
        z_score = stats.norm.ppf((1 + self.confidence_level) / 2)  # ~1.04 for 70%
        margin_of_error = z_score * std_dev
        
        confidence_lower = spread - margin_of_error
        confidence_upper = spread + margin_of_error
        
        return {
            "home_team": home_team,
            "away_team": away_team,
            "predicted_spread": round(spread, 2),
            "home_team_strength": round(home_strength, 2),
            "away_team_strength": round(away_strength, 2),
            "confidence_interval": {
                "lower": round(confidence_lower, 2),
                "upper": round(confidence_upper, 2),
                "confidence_level": f"{int(self.confidence_level * 100)}%"
            },
            "interpretation": self._interpret_spread(spread, home_team, away_team)
        }
    
    def predict_total(self, home_team: str, away_team: str) -> Dict:
        """
        Predict the total (over/under) for a matchup
        Returns total with confidence interval
        """
        # Fetch team data
        home_data = self._get_team_record(home_team)
        away_data = self._get_team_record(away_team)
        
        # Calculate average goals per game for each team
        home_gpg = self._get_goals_per_game(home_data)
        away_gpg = self._get_goals_per_game(away_data)
        
        # Calculate average goals allowed per game
        home_gapg = self._get_goals_allowed_per_game(home_data)
        away_gapg = self._get_goals_allowed_per_game(away_data)
        
        # Predict total using offensive and defensive metrics
        # Expected goals = (Team A offense vs Team B defense + Team B offense vs Team A defense)
        expected_home_goals = (home_gpg + away_gapg) / 2
        expected_away_goals = (away_gpg + home_gapg) / 2
        predicted_total = expected_home_goals + expected_away_goals
        
        # Calculate confidence interval
        # Standard deviation for NHL totals is approximately 1.8 goals
        std_dev = 1.8
        z_score = stats.norm.ppf((1 + self.confidence_level) / 2)
        margin_of_error = z_score * std_dev
        
        confidence_lower = predicted_total - margin_of_error
        confidence_upper = predicted_total + margin_of_error
        
        return {
            "home_team": home_team,
            "away_team": away_team,
            "predicted_total": round(predicted_total, 2),
            "home_expected_goals": round(expected_home_goals, 2),
            "away_expected_goals": round(expected_away_goals, 2),
            "confidence_interval": {
                "lower": round(confidence_lower, 2),
                "upper": round(confidence_upper, 2),
                "confidence_level": f"{int(self.confidence_level * 100)}%"
            },
            "interpretation": self._interpret_total(predicted_total)
        }
    
    def find_spread_value(self, home_team: str, away_team: str, market_spread: float) -> Dict:
        """
        Analyze matchup and recommend bet based on score prediction (who we predict will cover)
        
        Args:
            home_team: Home team abbreviation
            away_team: Away team abbreviation
            market_spread: Current betting line spread (positive = home favored, negative = away favored)
        
        Returns:
            Dictionary with prediction-based recommendation (not value-based)
        """
        prediction = self.predict_spread(home_team, away_team)
        predicted_spread = prediction['predicted_spread']
        
        # Calculate spread difference (predicted - market)
        spread_difference = predicted_spread - market_spread
        
        # Determine underdog based on market line
        if market_spread < 0:
            underdog = home_team
            favorite = away_team
            underdog_getting = abs(market_spread)
        else:
            underdog = away_team
            favorite = home_team
            underdog_getting = market_spread
        
        # NEW: Recommend based on our PREDICTION, not value
        # If we predict home team covers the market spread, recommend home team
        # If we predict away team covers the market spread, recommend away team
        
        # Our prediction says home team wins by predicted_spread
        # Market line is market_spread
        
        if predicted_spread > market_spread:
            # We predict home team wins by MORE than the market line
            # Recommend home team to cover
            prediction_assessment = f"Model predicts {home_team} wins by {abs(predicted_spread):.1f} goals (exceeds market line of {abs(market_spread):.1f})"
            recommended_bet = f"Bet {home_team} to cover {market_spread:+.1f}"
            predicted_winner = home_team
        elif predicted_spread < market_spread:
            # We predict home team wins by LESS than the market line (or loses)
            # Recommend away team to cover
            prediction_assessment = f"Model predicts {home_team} wins by only {abs(predicted_spread):.1f} goals (below market line of {abs(market_spread):.1f})"
            recommended_bet = f"Bet {away_team} to cover {-market_spread:+.1f}"
            predicted_winner = away_team
        else:
            # Exact match - pass or bet based on confidence
            prediction_assessment = "Model prediction matches market line exactly"
            recommended_bet = "Pass - prediction matches market"
            predicted_winner = "Push"
        
        return {
            "home_team": home_team,
            "away_team": away_team,
            "predicted_spread": round(predicted_spread, 2),
            "market_spread": round(market_spread, 2),
            "spread_difference": round(spread_difference, 2),
            "prediction_assessment": prediction_assessment,
            "recommended_bet": recommended_bet,
            "predicted_winner": predicted_winner,
            "underdog": underdog,
            "favorite": favorite,
            "underdog_points": round(underdog_getting, 2),
            "confidence_interval": prediction['confidence_interval']
        }
    
    def simulate_score(self, home_team: str, away_team: str, num_simulations: int = 10000) -> Dict:
        """
        Simulate final score using Poisson distribution based on expected goals
        
        Args:
            home_team: Home team abbreviation
            away_team: Away team abbreviation
            num_simulations: Number of Monte Carlo simulations to run
        
        Returns:
            Dictionary with most likely score, score probabilities, and win probabilities
        """
        # Get expected goals from total prediction
        total_prediction = self.predict_total(home_team, away_team)
        home_expected = total_prediction['home_expected_goals']
        away_expected = total_prediction['away_expected_goals']
        
        # Run Monte Carlo simulations using Poisson distribution
        # Poisson distribution is standard for modeling hockey goals
        np.random.seed(42)  # For reproducibility
        
        home_scores = np.random.poisson(home_expected, num_simulations)
        away_scores = np.random.poisson(away_expected, num_simulations)
        
        # Calculate win probabilities
        home_wins = np.sum(home_scores > away_scores)
        away_wins = np.sum(away_scores > home_scores)
        ties = np.sum(home_scores == away_scores)
        
        home_win_prob = home_wins / num_simulations
        away_win_prob = away_wins / num_simulations
        tie_prob = ties / num_simulations
        
        # Find most likely score
        score_combinations = {}
        for h, a in zip(home_scores, away_scores):
            key = (int(h), int(a))
            score_combinations[key] = score_combinations.get(key, 0) + 1
        
        most_likely_score = max(score_combinations.items(), key=lambda x: x[1])
        most_likely_home, most_likely_away = most_likely_score[0]
        most_likely_prob = most_likely_score[1] / num_simulations
        
        # Get top 10 most likely scores
        top_scores = sorted(score_combinations.items(), key=lambda x: x[1], reverse=True)[:10]
        top_scores_formatted = [
            {
                "score": f"{home_team} {h} - {a} {away_team}",
                "probability": f"{(count/num_simulations)*100:.2f}%"
            }
            for (h, a), count in top_scores
        ]
        
        # Calculate score distribution statistics
        avg_home_score = np.mean(home_scores)
        avg_away_score = np.mean(away_scores)
        median_home_score = np.median(home_scores)
        median_away_score = np.median(away_scores)
        
        # Determine recommended final score prediction
        predicted_final_score = f"{home_team} {most_likely_home} - {most_likely_away} {away_team}"
        
        return {
            "matchup": f"{away_team} @ {home_team}",
            "predicted_final_score": predicted_final_score,
            "most_likely_score": {
                "home_goals": most_likely_home,
                "away_goals": most_likely_away,
                "probability": f"{most_likely_prob*100:.2f}%"
            },
            "expected_goals": {
                "home": round(home_expected, 2),
                "away": round(away_expected, 2)
            },
            "simulation_stats": {
                "average_home_score": round(avg_home_score, 2),
                "average_away_score": round(avg_away_score, 2),
                "median_home_score": int(median_home_score),
                "median_away_score": int(median_away_score),
                "simulations_run": num_simulations
            },
            "win_probabilities": {
                f"{home_team}_win": f"{home_win_prob*100:.1f}%",
                f"{away_team}_win": f"{away_win_prob*100:.1f}%",
                "tie_regulation": f"{tie_prob*100:.1f}%"
            },
            "top_10_likely_scores": top_scores_formatted,
            "interpretation": self._interpret_score_simulation(
                home_team, away_team, most_likely_home, most_likely_away, home_win_prob
            )
        }
    
    def get_full_analysis(self, home_team: str, away_team: str, include_score_sim: bool = False) -> Dict:
        """
        Get complete analysis including spread and total predictions
        
        Args:
            home_team: Home team abbreviation
            away_team: Away team abbreviation
            include_score_sim: Whether to include score simulation (adds processing time)
        """
        spread_prediction = self.predict_spread(home_team, away_team)
        total_prediction = self.predict_total(home_team, away_team)
        
        result = {
            "matchup": f"{away_team} @ {home_team}",
            "timestamp": datetime.now().isoformat(),
            "spread_analysis": spread_prediction,
            "total_analysis": total_prediction,
            "confidence_level": f"{int(self.confidence_level * 100)}%"
        }
        
        if include_score_sim:
            result["score_simulation"] = self.simulate_score(home_team, away_team)
        
        return result
    
    def _get_team_record(self, team_abbr: str) -> Dict:
        """Helper to get team record from standings"""
        standings = self.data_fetcher.get_standings()
        
        if not standings or 'standings' not in standings:
            return self._get_default_team_data()
        
        # Search through all divisions
        for standing in standings.get('standings', []):
            if standing.get('teamAbbrev', {}).get('default') == team_abbr:
                return standing
        
        return self._get_default_team_data()
    
    def _get_default_team_data(self) -> Dict:
        """Return default team data for fallback"""
        return {
            'wins': 20,
            'losses': 20,
            'otLosses': 5,
            'goalFor': 135,
            'goalAgainst': 135,
            'gamesPlayed': 45
        }
    
    def _get_goals_per_game(self, team_data: Dict) -> float:
        """Calculate goals per game for a team"""
        goals_for = team_data.get('goalFor', 135)
        games_played = team_data.get('gamesPlayed', 45)
        return goals_for / games_played if games_played > 0 else 3.0
    
    def _get_goals_allowed_per_game(self, team_data: Dict) -> float:
        """Calculate goals allowed per game for a team"""
        goals_against = team_data.get('goalAgainst', 135)
        games_played = team_data.get('gamesPlayed', 45)
        return goals_against / games_played if games_played > 0 else 3.0
    
    def _interpret_spread(self, spread: float, home_team: str, away_team: str) -> str:
        """Interpret the spread prediction"""
        if spread > 1.0:
            return f"{home_team} favored by {abs(spread):.1f} goals (underdog: {away_team})"
        elif spread < -1.0:
            return f"{away_team} favored by {abs(spread):.1f} goals (underdog: {home_team})"
        else:
            return "Evenly matched game (pick 'em)"
    
    def _interpret_total(self, total: float) -> str:
        """Interpret the total prediction"""
        if total < 5.5:
            return "Low-scoring game expected"
        elif total > 6.5:
            return "High-scoring game expected"
        else:
            return "Average-scoring game expected"
    
    def _interpret_score_simulation(self, home_team: str, away_team: str, 
                                     home_score: int, away_score: int, home_win_prob: float) -> str:
        """Interpret the score simulation results"""
        winner = home_team if home_score > away_score else away_team if away_score > home_score else "Tie"
        
        if winner == "Tie":
            return f"Most likely to be tied {home_score}-{away_score} in regulation (OT/SO likely)"
        else:
            margin = abs(home_score - away_score)
            confidence = "high" if home_win_prob > 0.65 or home_win_prob < 0.35 else "moderate"
            
            if margin == 1:
                return f"{winner} predicted to win by 1 goal ({confidence} confidence)"
            else:
                return f"{winner} predicted to win by {margin} goals ({confidence} confidence)"


def main():
    """Main function to demonstrate the NHL analytics system"""
    print("=" * 60)
    print("NHL Spread and Total Analytics System")
    print("70% Confidence Level Predictions")
    print("=" * 60)
    print()
    
    # Initialize analytics
    analytics = NHLAnalytics()
    
    # Example matchups (using common NHL team abbreviations)
    matchups = [
        ("TOR", "MTL"),  # Toronto vs Montreal
        ("NYR", "NYI"),  # Rangers vs Islanders
        ("BOS", "TBL"),  # Boston vs Tampa Bay
    ]
    
    for home, away in matchups:
        print(f"\n{'='*60}")
        print(f"Analyzing: {away} @ {home}")
        print('='*60)
        
        # Get full analysis
        analysis = analytics.get_full_analysis(home, away)
        
        # Display spread prediction
        spread = analysis['spread_analysis']
        print(f"\n📊 SPREAD PREDICTION:")
        print(f"   Predicted Spread: {spread['predicted_spread']}")
        print(f"   {spread['interpretation']}")
        print(f"   70% Confidence Interval: [{spread['confidence_interval']['lower']}, {spread['confidence_interval']['upper']}]")
        print(f"   {home} Strength: {spread['home_team_strength']}")
        print(f"   {away} Strength: {spread['away_team_strength']}")
        
        # Display total prediction
        total = analysis['total_analysis']
        print(f"\n🎯 TOTAL PREDICTION:")
        print(f"   Predicted Total: {total['predicted_total']}")
        print(f"   {total['interpretation']}")
        print(f"   70% Confidence Interval: [{total['confidence_interval']['lower']}, {total['confidence_interval']['upper']}]")
        print(f"   Expected {home} Goals: {total['home_expected_goals']}")
        print(f"   Expected {away} Goals: {total['away_expected_goals']}")
        
        print()
    
    # Demonstrate value finding with example market spreads
    print("\n" + "=" * 60)
    print("VALUE ANALYSIS - Finding Underdog & Overvalued Spreads")
    print("=" * 60)
    print("\nComparing predicted spreads vs hypothetical market lines:")
    
    # Example market spreads (home team perspective: positive = home favored)
    market_examples = [
        ("TOR", "MTL", 1.5),   # Market has TOR -1.5
        ("NYR", "NYI", 2.5),   # Market has NYR -2.5
        ("BOS", "TBL", -0.5),  # Market has BOS as slight underdog
    ]
    
    for home, away, market_spread in market_examples:
        print(f"\n{away} @ {home} (Market spread: {market_spread:+.1f})")
        value = analytics.find_spread_value(home, away, market_spread)
        print(f"   Predicted: {value['predicted_spread']:+.1f}")
        print(f"   Difference: {value['spread_difference']:+.2f} goals")
        print(f"   Underdog: {value['underdog']} (+{value['underdog_points']:.1f})")
        print(f"   Assessment: {value['value_assessment']}")
        print(f"   💡 {value['recommended_bet']}")
    
    print()
    print("=" * 60)
    print("Analysis Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
