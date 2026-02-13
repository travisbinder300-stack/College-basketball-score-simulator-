"""
Guide: Customizing and Extending the Billy Walters Framework

This guide shows how to adapt the system for your specific needs.
"""

from billy_walters_predictor import (
    PowerRatings, TeamStats, PredictionEngine,
    BankrollManagement, GameFactors
)


# ==============================================================================
# EXAMPLE 1: Creating Custom Power Ratings
# ==============================================================================

class CustomPowerRatings(PowerRatings):
    """
    Extend the base PowerRatings class with custom adjustments
    """
    
    def adjust_for_coaching(self, rating: float, coach_experience: int) -> float:
        """
        Add adjustment for coaching experience
        Elite coaches in tournament situations can add value
        """
        if coach_experience > 20:
            return rating + 1.0
        elif coach_experience > 10:
            return rating + 0.5
        return rating
    
    def adjust_for_venue(self, rating: float, venue_altitude: int) -> float:
        """
        Adjust for altitude (e.g., playing in Denver)
        Teams not used to altitude may struggle
        """
        if venue_altitude > 5000:  # High altitude
            return rating - 0.5
        return rating
    
    def calculate_power_rating(self, stats: TeamStats, 
                               coach_experience: int = 0,
                               venue_altitude: int = 0) -> float:
        """
        Enhanced power rating with custom factors
        """
        # Start with base calculation
        rating = super().calculate_power_rating(stats)
        
        # Add custom adjustments
        rating = self.adjust_for_coaching(rating, coach_experience)
        rating = self.adjust_for_venue(rating, venue_altitude)
        
        return rating


# ==============================================================================
# EXAMPLE 2: Custom Game Factors
# ==============================================================================

class TournamentGameFactors(GameFactors):
    """
    Special adjustments for tournament games
    """
    
    @staticmethod
    def calculate_tournament_pressure(
        seed: int,
        underdog: bool,
        previous_upset: bool
    ) -> float:
        """
        Tournament-specific factors
        
        - Lower seeds often outperform (nothing to lose)
        - Teams coming off upset may have letdown
        """
        adjustment = 0.0
        
        if underdog and seed >= 10:
            # Double-digit seeds play loose
            adjustment += 2.0
        
        if previous_upset:
            # Letdown game after big upset
            adjustment -= 1.5
        
        return adjustment
    
    @staticmethod
    def calculate_rest_advantage(days_rest_diff: int) -> float:
        """
        In tournaments, rest can be significant advantage
        """
        # Each day of extra rest worth ~0.5 points
        return days_rest_diff * 0.5


# ==============================================================================
# EXAMPLE 3: Custom Bankroll Strategy
# ==============================================================================

class AggressiveBankroll(BankrollManagement):
    """
    More aggressive bankroll management for experienced bettors
    Still controlled but allows up to 5% per bet
    """
    
    def __init__(self, total_bankroll: float):
        super().__init__(total_bankroll)
        self.max_bet_pct = 0.05  # 5% max instead of 3%
    
    def calculate_bet_size(self, edge: float, confidence: float) -> float:
        """
        Slightly more aggressive Kelly sizing
        """
        if edge <= 0:
            return 0.0
        
        # More aggressive multiplier
        bet_fraction = min(edge * confidence * 0.15, self.max_bet_pct)
        bet_fraction = max(bet_fraction, self.min_bet_pct)
        
        bet_size = self.current_bankroll * bet_fraction
        
        return round(bet_size, 2)


class ConservativeBankroll(BankrollManagement):
    """
    Very conservative bankroll for risk-averse bettors
    Maximum 1% per bet, requires higher edge threshold
    """
    
    def __init__(self, total_bankroll: float):
        super().__init__(total_bankroll)
        self.max_bet_pct = 0.01  # 1% max
    
    def should_bet(self, edge: float, min_edge: float = 0.05) -> bool:
        """
        Require 5% minimum edge instead of 3%
        """
        return edge >= min_edge


# ==============================================================================
# EXAMPLE 4: Integrating Real Data Sources
# ==============================================================================

def load_team_stats_from_kenpom(team_name: str) -> TeamStats:
    """
    Template for loading data from KenPom or similar service
    
    You would need to:
    1. Get API access or scrape data (following their terms)
    2. Parse the efficiency and tempo data
    3. Calculate recent form from game results
    """
    # Placeholder - replace with actual data fetch
    stats = TeamStats(
        name=team_name,
        offensive_efficiency=110.0,  # From KenPom AdjO
        defensive_efficiency=95.0,   # From KenPom AdjD
        tempo=68.0,                  # From KenPom Tempo
        recent_form=['W', 'W', 'L', 'W', 'W'],  # From game results
        strength_of_schedule=0.0,    # From KenPom SOS
        injuries=[]                  # From injury reports
    )
    
    return stats


def get_market_lines_from_sportsbook(game_id: str) -> dict:
    """
    Template for fetching market lines from sportsbook API
    
    Most sportsbooks have APIs (e.g., The Odds API)
    """
    # Placeholder - replace with actual API call
    lines = {
        'spread': 5.5,
        'favorite': 'Duke',
        'total': 150.0,
        'opening_spread': 6.0,
        'time_posted': '2026-02-10T10:00:00Z'
    }
    
    return lines


# ==============================================================================
# EXAMPLE 5: Tracking and Analysis
# ==============================================================================

class BettingTracker:
    """
    Track bets and analyze performance over time
    Critical for validating model accuracy
    """
    
    def __init__(self):
        self.bets = []
        self.starting_bankroll = 0
    
    def record_bet(
        self,
        game: str,
        bet_type: str,
        amount: float,
        odds: float,
        edge: float,
        result: str = 'pending'  # 'win', 'loss', 'push', 'pending'
    ):
        """Record a bet"""
        bet = {
            'game': game,
            'type': bet_type,
            'amount': amount,
            'odds': odds,
            'edge': edge,
            'result': result,
            'profit': 0.0
        }
        self.bets.append(bet)
    
    def update_result(self, bet_index: int, result: str, profit: float):
        """Update bet result"""
        self.bets[bet_index]['result'] = result
        self.bets[bet_index]['profit'] = profit
    
    def calculate_roi(self) -> float:
        """Calculate return on investment"""
        total_bet = sum(b['amount'] for b in self.bets if b['result'] != 'pending')
        total_profit = sum(b['profit'] for b in self.bets if b['result'] != 'pending')
        
        if total_bet == 0:
            return 0.0
        
        return (total_profit / total_bet) * 100
    
    def calculate_win_rate(self) -> float:
        """Calculate win percentage"""
        completed = [b for b in self.bets if b['result'] in ['win', 'loss']]
        if not completed:
            return 0.0
        
        wins = len([b for b in completed if b['result'] == 'win'])
        return (wins / len(completed)) * 100
    
    def analyze_by_edge(self):
        """
        Analyze performance by edge buckets
        Helps validate that higher edge bets actually perform better
        """
        buckets = {
            '3-5%': [],
            '5-7%': [],
            '7-10%': [],
            '10%+': []
        }
        
        for bet in self.bets:
            if bet['result'] in ['win', 'loss', 'push']:
                edge = bet['edge']
                if 0.03 <= edge < 0.05:
                    buckets['3-5%'].append(bet)
                elif 0.05 <= edge < 0.07:
                    buckets['5-7%'].append(bet)
                elif 0.07 <= edge < 0.10:
                    buckets['7-10%'].append(bet)
                elif edge >= 0.10:
                    buckets['10%+'].append(bet)
        
        print("Performance by Edge Bucket:")
        for bucket, bets in buckets.items():
            if bets:
                wins = len([b for b in bets if b['result'] == 'win'])
                total = len(bets)
                win_pct = (wins / total) * 100
                profit = sum(b['profit'] for b in bets)
                print(f"  {bucket}: {wins}/{total} ({win_pct:.1f}%) | Profit: ${profit:.2f}")


# ==============================================================================
# EXAMPLE 6: Complete Workflow
# ==============================================================================

def complete_workflow_example():
    """
    Shows a complete workflow from data to decision
    """
    print("=" * 80)
    print("COMPLETE WORKFLOW EXAMPLE")
    print("=" * 80)
    print()
    
    # 1. Initialize systems
    pr = CustomPowerRatings()
    bankroll = BankrollManagement(10000)
    tracker = BettingTracker()
    tracker.starting_bankroll = 10000
    
    # 2. Load team data (in practice, from real sources)
    duke_stats = TeamStats(
        name='Duke',
        offensive_efficiency=115.5,
        defensive_efficiency=95.2,
        tempo=70.5,
        recent_form=['W', 'W', 'L', 'W', 'W'],
        strength_of_schedule=2.5,
        injuries=[]
    )
    
    # 3. Calculate power ratings
    duke_rating = pr.calculate_power_rating(
        duke_stats,
        coach_experience=25,  # Coach K level experience
        venue_altitude=0
    )
    pr.ratings['Duke'] = duke_rating
    
    print(f"Duke Power Rating: {duke_rating:+.1f}")
    print()
    
    # 4. Get market data (in practice, from sportsbook API)
    market = {
        'spread': 5.5,
        'favorite': 'Duke',
        'total': 150.0
    }
    
    print(f"Market Line: Duke -{market['spread']}")
    print()
    
    # 5. Make prediction and calculate edge
    # (Simplified - would use full PredictionEngine)
    predicted_spread = 8.0
    edge = abs(predicted_spread - market['spread']) * 0.025
    
    print(f"Our Prediction: Duke -{predicted_spread}")
    print(f"Edge: {edge:.1%}")
    print()
    
    # 6. Decision: Should we bet?
    if bankroll.should_bet(edge, min_edge=0.03):
        bet_size = bankroll.calculate_bet_size(edge, confidence=0.75)
        print(f"✓ BET RECOMMENDED")
        print(f"  Bet Size: ${bet_size:.2f}")
        print(f"  Side: Duke -{market['spread']}")
        
        # 7. Record the bet
        tracker.record_bet(
            game='Duke vs UNC',
            bet_type='spread',
            amount=bet_size,
            odds=-110,
            edge=edge,
            result='pending'
        )
        print(f"  Bet recorded in tracker")
    else:
        print("✗ NO BET - Insufficient edge")
    
    print()
    print("=" * 80)
    print("This workflow can be automated to run daily for full game slates")
    print("=" * 80)


# ==============================================================================
# TIPS FOR PRODUCTION USE
# ==============================================================================

PRODUCTION_TIPS = """
TIPS FOR USING THIS SYSTEM IN PRODUCTION:

1. DATA SOURCES
   - Subscribe to KenPom, BartTorvik, or similar for team metrics
   - Use The Odds API or similar for real-time market lines
   - Follow beat reporters for injury news
   - Track line movements across multiple sportsbooks

2. AUTOMATION
   - Schedule daily data updates
   - Automatically fetch game schedules
   - Set up alerts for value opportunities
   - Automate bet placement (where legal/supported)

3. VALIDATION
   - Back-test your model on historical data
   - Track all predictions vs actual results
   - Calculate correlation between predicted edge and profit
   - Adjust model parameters based on performance

4. RISK MANAGEMENT
   - Never exceed 10% total bankroll exposure per day
   - Take smaller positions on correlated games
   - Reserve capital for high-edge opportunities
   - Adjust bet sizing based on recent performance

5. LEGAL CONSIDERATIONS
   - Only bet where legal in your jurisdiction
   - Pay taxes on winnings
   - Keep detailed records for tax purposes
   - Use licensed, regulated sportsbooks

6. CONTINUOUS IMPROVEMENT
   - Regularly review losing bets for patterns
   - Test new factors and metrics
   - Compare against other sharp bettors
   - Stay updated on rule changes and trends

7. PSYCHOLOGICAL DISCIPLINE
   - Stick to your system even during losing streaks
   - Don't chase losses with higher stakes
   - Take breaks if betting becomes emotional
   - Remember: long-term edge matters, not day-to-day variance

Remember: Billy Walters succeeded through discipline, patience, and 
mathematical rigor. Follow the principles, not the emotions.
"""


if __name__ == "__main__":
    complete_workflow_example()
    print()
    print(PRODUCTION_TIPS)
