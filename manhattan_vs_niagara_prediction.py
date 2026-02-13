"""
Manhattan vs Niagara Game Prediction
Using Billy Walters Framework for College Basketball

MAAC Conference Matchup Analysis with ATS Tracking
"""

from billy_walters_predictor import (
    TeamStats, PowerRatings, GameFactors, 
    PredictionEngine, BankrollManagement
)
from dataclasses import dataclass
from datetime import datetime
import numpy as np


@dataclass
class ATSRecord:
    """ATS (Against The Spread) Record"""
    wins: int
    losses: int
    pushes: int
    home_wins: int
    home_losses: int
    away_wins: int
    away_losses: int
    fav_wins: int
    fav_losses: int
    dog_wins: int
    dog_losses: int
    
    @property
    def ats_percentage(self) -> float:
        """Overall ATS win percentage"""
        total = self.wins + self.losses
        return (self.wins / total * 100) if total > 0 else 0.0
    
    @property
    def home_percentage(self) -> float:
        """Home ATS win percentage"""
        total = self.home_wins + self.home_losses
        return (self.home_wins / total * 100) if total > 0 else 0.0
    
    @property
    def away_percentage(self) -> float:
        """Away ATS win percentage"""
        total = self.away_wins + self.away_losses
        return (self.away_wins / total * 100) if total > 0 else 0.0
    
    @property
    def favorite_percentage(self) -> float:
        """Favorite ATS win percentage"""
        total = self.fav_wins + self.fav_losses
        return (self.fav_wins / total * 100) if total > 0 else 0.0
    
    @property
    def underdog_percentage(self) -> float:
        """Underdog ATS win percentage"""
        total = self.dog_wins + self.dog_losses
        return (self.dog_wins / total * 100) if total > 0 else 0.0


def get_manhattan_ats() -> ATSRecord:
    """
    Manhattan Jaspers ATS Record
    Estimated mid-major profile for 2023-24 season
    """
    return ATSRecord(
        wins=14,
        losses=11,
        pushes=1,
        home_wins=9,
        home_losses=4,
        away_wins=5,
        away_losses=7,
        fav_wins=8,
        fav_losses=6,
        dog_wins=6,
        dog_losses=5
    )


def get_niagara_ats() -> ATSRecord:
    """
    Niagara Purple Eagles ATS Record
    Estimated mid-major profile for 2023-24 season
    """
    return ATSRecord(
        wins=12,
        losses=13,
        pushes=1,
        home_wins=7,
        home_losses=6,
        away_wins=5,
        away_losses=7,
        fav_wins=5,
        fav_losses=8,
        dog_wins=7,
        dog_losses=5
    )


def get_manhattan_stats() -> TeamStats:
    """
    Manhattan Jaspers Statistics
    Conference: MAAC (Metro Atlantic Atlantic Conference)
    
    Based on typical mid-major profile with estimated 2023-24 season stats
    """
    return TeamStats(
        name="Manhattan",
        offensive_efficiency=103.5,  # Points per 100 possessions
        defensive_efficiency=106.2,  # Points allowed per 100 possessions
        tempo=70.5,  # Possessions per game
        recent_form=['W', 'L', 'W', 'W', 'L'],  # Last 5 games: 3-2
        strength_of_schedule=-2.5,  # Mid-major schedule
        injuries=[]  # No major injuries reported
    )


def get_niagara_stats() -> TeamStats:
    """
    Niagara Purple Eagles Statistics
    Conference: MAAC (Metro Atlantic Athletic Conference)
    
    Based on typical mid-major profile with estimated 2023-24 season stats
    """
    return TeamStats(
        name="Niagara",
        offensive_efficiency=101.8,  # Points per 100 possessions
        defensive_efficiency=105.5,  # Points allowed per 100 possessions
        tempo=68.2,  # Possessions per game (slower pace)
        recent_form=['L', 'W', 'L', 'W', 'W'],  # Last 5 games: 3-2
        strength_of_schedule=-2.8,  # Mid-major schedule
        injuries=[]  # No major injuries reported
    )


def run_prediction():
    """
    Complete matchup analysis for Manhattan vs Niagara
    """
    print("=" * 90)
    print("MANHATTAN vs NIAGARA - GAME PREDICTION")
    print("Billy Walters Framework Analysis")
    print("=" * 90)
    print()
    
    # Get team statistics
    manhattan_stats = get_manhattan_stats()
    niagara_stats = get_niagara_stats()
    
    print("GAME SETUP")
    print(f"  Home Team: Manhattan Jaspers")
    print(f"  Away Team: Niagara Purple Eagles")
    print(f"  Location: Draddy Gymnasium (Bronx, NY)")
    print(f"  Conference: MAAC")
    print()
    
    # Calculate power ratings
    print("-" * 90)
    print("TEAM STATISTICS & POWER RATINGS")
    print("-" * 90)
    print()
    
    power_ratings = PowerRatings()
    
    manhattan_rating = power_ratings.calculate_power_rating(manhattan_stats)
    niagara_rating = power_ratings.calculate_power_rating(niagara_stats)
    
    # Store ratings for prediction engine
    power_ratings.ratings["Manhattan"] = manhattan_rating
    power_ratings.ratings["Niagara"] = niagara_rating
    
    print(f"MANHATTAN JASPERS")
    print(f"  Offensive Efficiency: {manhattan_stats.offensive_efficiency:.1f} pts/100 poss")
    print(f"  Defensive Efficiency: {manhattan_stats.defensive_efficiency:.1f} pts/100 poss")
    print(f"  Net Efficiency: {manhattan_stats.offensive_efficiency - manhattan_stats.defensive_efficiency:.1f}")
    print(f"  Tempo: {manhattan_stats.tempo:.1f} possessions/game")
    print(f"  Recent Form: {'-'.join(manhattan_stats.recent_form)} (3-2 in last 5)")
    print(f"  Strength of Schedule: {manhattan_stats.strength_of_schedule:.1f}")
    print(f"  ★ POWER RATING: {manhattan_rating:.2f}")
    print()
    
    print(f"NIAGARA PURPLE EAGLES")
    print(f"  Offensive Efficiency: {niagara_stats.offensive_efficiency:.1f} pts/100 poss")
    print(f"  Defensive Efficiency: {niagara_stats.defensive_efficiency:.1f} pts/100 poss")
    print(f"  Net Efficiency: {niagara_stats.offensive_efficiency - niagara_stats.defensive_efficiency:.1f}")
    print(f"  Tempo: {niagara_stats.tempo:.1f} possessions/game")
    print(f"  Recent Form: {'-'.join(niagara_stats.recent_form)} (3-2 in last 5)")
    print(f"  Strength of Schedule: {niagara_stats.strength_of_schedule:.1f}")
    print(f"  ★ POWER RATING: {niagara_rating:.2f}")
    print()
    
    # ATS (Against The Spread) Analysis
    print("-" * 90)
    print("ATS (AGAINST THE SPREAD) RECORDS")
    print("-" * 90)
    print()
    
    manhattan_ats = get_manhattan_ats()
    niagara_ats = get_niagara_ats()
    
    print(f"MANHATTAN JASPERS ATS RECORD")
    print(f"  Overall: {manhattan_ats.wins}-{manhattan_ats.losses}-{manhattan_ats.pushes} ({manhattan_ats.ats_percentage:.1f}%)")
    print(f"  Home: {manhattan_ats.home_wins}-{manhattan_ats.home_losses} ({manhattan_ats.home_percentage:.1f}%)")
    print(f"  Away: {manhattan_ats.away_wins}-{manhattan_ats.away_losses} ({manhattan_ats.away_percentage:.1f}%)")
    print(f"  As Favorite: {manhattan_ats.fav_wins}-{manhattan_ats.fav_losses} ({manhattan_ats.favorite_percentage:.1f}%)")
    print(f"  As Underdog: {manhattan_ats.dog_wins}-{manhattan_ats.dog_losses} ({manhattan_ats.underdog_percentage:.1f}%)")
    
    # Evaluate Manhattan's ATS strength
    if manhattan_ats.ats_percentage >= 55:
        print(f"  ✓ STRONG ATS PERFORMER (Above breakeven)")
    elif manhattan_ats.ats_percentage >= 50:
        print(f"  → SOLID ATS PERFORMER (Near breakeven)")
    else:
        print(f"  ⚠ BELOW AVERAGE ATS (Under 50%)")
    
    print()
    
    print(f"NIAGARA PURPLE EAGLES ATS RECORD")
    print(f"  Overall: {niagara_ats.wins}-{niagara_ats.losses}-{niagara_ats.pushes} ({niagara_ats.ats_percentage:.1f}%)")
    print(f"  Home: {niagara_ats.home_wins}-{niagara_ats.home_losses} ({niagara_ats.home_percentage:.1f}%)")
    print(f"  Away: {niagara_ats.away_wins}-{niagara_ats.away_losses} ({niagara_ats.away_percentage:.1f}%)")
    print(f"  As Favorite: {niagara_ats.fav_wins}-{niagara_ats.fav_losses} ({niagara_ats.favorite_percentage:.1f}%)")
    print(f"  As Underdog: {niagara_ats.dog_wins}-{niagara_ats.dog_losses} ({niagara_ats.underdog_percentage:.1f}%)")
    
    # Evaluate Niagara's ATS strength
    if niagara_ats.ats_percentage >= 55:
        print(f"  ✓ STRONG ATS PERFORMER (Above breakeven)")
    elif niagara_ats.ats_percentage >= 50:
        print(f"  → SOLID ATS PERFORMER (Near breakeven)")
    else:
        print(f"  ⚠ BELOW AVERAGE ATS (Under 50%)")
    
    print()
    
    # ATS Trends Analysis
    print("ATS TRENDS FOR THIS MATCHUP:")
    print(f"  Manhattan at home: {manhattan_ats.home_percentage:.1f}% ATS")
    print(f"  Niagara on road: {niagara_ats.away_percentage:.1f}% ATS")
    
    # Determine ATS edge
    ats_edge = manhattan_ats.home_percentage - niagara_ats.away_percentage
    if abs(ats_edge) >= 15:
        edge_team = "Manhattan" if ats_edge > 0 else "Niagara"
        print(f"  🔥 STRONG ATS EDGE: {edge_team} ({abs(ats_edge):.1f}% difference)")
    elif abs(ats_edge) >= 10:
        edge_team = "Manhattan" if ats_edge > 0 else "Niagara"
        print(f"  ✓ MODERATE ATS EDGE: {edge_team} ({abs(ats_edge):.1f}% difference)")
    else:
        print(f"  → EVEN ATS MATCHUP (within {abs(ats_edge):.1f}%)")
    
    print()
    
    # Handicapping analysis
    print("-" * 90)
    print("HANDICAPPING FACTORS")
    print("-" * 90)
    print()
    
    # Home court advantage
    home_court = GameFactors.HOME_COURT_ADVANTAGE
    print(f"✓ Home Court Advantage: +{home_court:.1f} points for Manhattan")
    
    # Travel factor (Manhattan to Niagara is ~350 miles)
    travel_miles = 350
    travel_penalty = GameFactors.calculate_travel_fatigue(travel_miles, 2)
    print(f"✓ Travel Factor: -{travel_penalty:.1f} points for Niagara ({travel_miles} miles)")
    
    # Motivational factors
    motivation = GameFactors.calculate_motivation_factor(
        is_rivalry=True,
        is_conference_game=True,
        revenge_game=False
    )
    print(f"✓ Motivation Bonus: +{motivation:.1f} points (Conference rivalry game)")
    print(f"✓ Rest Situation: Both teams on 2 days rest (normal)")
    print()
    
    # Score prediction using PredictionEngine
    print("-" * 90)
    print("SCORE PREDICTION")
    print("-" * 90)
    print()
    
    predictor = PredictionEngine(power_ratings)
    
    # Get spread prediction
    predicted_spread, favorite = predictor.predict_spread(
        home_team="Manhattan",
        away_team="Niagara",
        is_neutral_site=False,
        miles_traveled=travel_miles,
        days_rest_home=2,
        days_rest_away=2,
        is_rivalry=True,
        is_conference_game=True,
        revenge_game=False
    )
    
    # Get total prediction
    predicted_total = predictor.predict_total(
        home_team="Manhattan",
        away_team="Niagara",
        home_stats=manhattan_stats,
        away_stats=niagara_stats
    )
    
    # Calculate individual scores
    if favorite == "Manhattan":
        manhattan_score = (predicted_total / 2) + (predicted_spread / 2)
        niagara_score = (predicted_total / 2) - (predicted_spread / 2)
    else:
        manhattan_score = (predicted_total / 2) - (predicted_spread / 2)
        niagara_score = (predicted_total / 2) + (predicted_spread / 2)
    
    print(f"Manhattan: {manhattan_score:.1f}")
    print(f"Niagara: {niagara_score:.1f}")
    print()
    print(f"PREDICTED SPREAD: {favorite} -{predicted_spread:.1f}")
    print(f"PREDICTED TOTAL: {predicted_total:.1f} points")
    print()
    
    # Determine underdog
    underdog = "Niagara" if favorite == "Manhattan" else "Manhattan"
    
    print(f"FAVORITE: {favorite} -{predicted_spread:.1f}")
    print(f"UNDERDOG: {underdog} +{predicted_spread:.1f}")
    print()
    
    # Key matchup factors
    print("-" * 90)
    print("KEY MATCHUP FACTORS")
    print("-" * 90)
    print()
    
    # Pace advantage
    pace_diff = manhattan_stats.tempo - niagara_stats.tempo
    faster_team = "Manhattan" if pace_diff > 0 else "Niagara"
    print(f"✓ PACE ADVANTAGE: {faster_team}")
    print(f"  Manhattan tempo: {manhattan_stats.tempo:.1f} poss/game")
    print(f"  Niagara tempo: {niagara_stats.tempo:.1f} poss/game")
    print(f"  Difference: {abs(pace_diff):.1f} possessions")
    print(f"  Expected game pace: {(manhattan_stats.tempo + niagara_stats.tempo) / 2:.1f} possessions")
    
    # Offensive vs Defensive matchup
    print()
    print(f"✓ OFFENSIVE MATCHUP:")
    print(f"  Manhattan offense ({manhattan_stats.offensive_efficiency:.1f}) vs")
    print(f"  Niagara defense ({niagara_stats.defensive_efficiency:.1f})")
    man_off_edge = manhattan_stats.offensive_efficiency - niagara_stats.defensive_efficiency
    print(f"  Manhattan edge: {man_off_edge:+.1f} points")
    
    print()
    print(f"✓ DEFENSIVE MATCHUP:")
    print(f"  Niagara offense ({niagara_stats.offensive_efficiency:.1f}) vs")
    print(f"  Manhattan defense ({manhattan_stats.defensive_efficiency:.1f})")
    niag_off_edge = niagara_stats.offensive_efficiency - manhattan_stats.defensive_efficiency
    print(f"  Niagara edge: {niag_off_edge:+.1f} points")
    
    # Efficiency comparison
    manhattan_net = manhattan_stats.offensive_efficiency - manhattan_stats.defensive_efficiency
    niagara_net = niagara_stats.offensive_efficiency - niagara_stats.defensive_efficiency
    
    print()
    print(f"✓ NET EFFICIENCY:")
    print(f"  Manhattan: {manhattan_net:+.1f}")
    print(f"  Niagara: {niagara_net:+.1f}")
    print(f"  Advantage: {'Manhattan' if manhattan_net > niagara_net else 'Niagara'} by {abs(manhattan_net - niagara_net):.1f} points")
    
    print()
    
    # Betting recommendations
    print("-" * 90)
    print("BETTING ANALYSIS & RECOMMENDATIONS")
    print("-" * 90)
    print()
    
    # Calculate edge scenarios
    typical_market_spread = round(predicted_spread * 2) / 2  # Round to nearest 0.5
    
    print(f"MODEL SPREAD: {favorite} -{predicted_spread:.1f}")
    print(f"LIKELY MARKET: {favorite} -{typical_market_spread:.1f} (estimated)")
    print()
    
    # Edge calculation
    edge = abs(predicted_spread - typical_market_spread)
    
    if edge >= 2.0:
        print(f"🔥 STRONG EDGE: {edge:.1f} points - Significant value detected")
    elif edge >= 1.0:
        print(f"✓ MODERATE EDGE: {edge:.1f} points - Playable with proper bankroll management")
    else:
        print(f"⚠ MINIMAL EDGE: {edge:.1f} points - Consider passing or small bet only")
    
    print()
    
    # Bankroll management
    bankroll = 10000
    bankroll_manager = BankrollManagement(total_bankroll=bankroll)
    
    if edge >= 0.5:
        bet_size = bankroll_manager.calculate_bet_size(
            edge=edge / 10,  # Convert edge to decimal
            confidence=0.7
        )
        
        bet_percentage = (bet_size / bankroll) * 100
        
        print(f"RECOMMENDED BET SIZE:")
        print(f"  {bet_percentage:.1f}% of bankroll")
        print(f"  ${bet_size:.2f} on ${bankroll:,.0f} bankroll")
        print()
    
    # Total analysis
    print(f"TOTAL (OVER/UNDER) ANALYSIS:")
    print(f"  Predicted Total: {predicted_total:.1f} points")
    print(f"  Expected Pace: {(manhattan_stats.tempo + niagara_stats.tempo) / 2:.1f} possessions")
    
    if predicted_total > 145:
        print(f"  Outlook: HIGH SCORING - Over likely")
    elif predicted_total < 130:
        print(f"  Outlook: LOW SCORING - Under likely")
    else:
        print(f"  Outlook: MODERATE SCORING - Typical MAAC game")
    
    print()
    
    # Key betting angles
    print("-" * 90)
    print("KEY BETTING ANGLES")
    print("-" * 90)
    print()
    
    print("FACTORS FAVORING MANHATTAN:")
    print(f"  ✓ Home court advantage (+{home_court:.1f} points)")
    if manhattan_net > niagara_net:
        print("  ✓ Superior net efficiency")
    if manhattan_stats.tempo > niagara_stats.tempo:
        print("  ✓ Controls pace with faster tempo")
    print("  ✓ Familiar venue (Draddy Gymnasium)")
    print("  ✓ No travel fatigue")
    if manhattan_ats.home_percentage > 55:
        print(f"  ✓ Strong home ATS record ({manhattan_ats.home_percentage:.1f}%)")
    if manhattan_ats.fav_wins > manhattan_ats.fav_losses and favorite == "Manhattan":
        print(f"  ✓ Covers well as favorite ({manhattan_ats.favorite_percentage:.1f}%)")
    
    print()
    print("FACTORS FAVORING NIAGARA:")
    if niagara_net > manhattan_net:
        print("  ✓ Superior net efficiency")
    print("  ✓ Better defensive efficiency")
    if niagara_stats.tempo < manhattan_stats.tempo:
        print("  ✓ Can slow the game to their preferred pace")
    print("  ✓ Recent form equally strong (3-2)")
    print("  ✓ Experience in road conference games")
    if niagara_ats.dog_wins > niagara_ats.dog_losses and underdog == "Niagara":
        print(f"  ✓ Covers well as underdog ({niagara_ats.underdog_percentage:.1f}%)")
    if niagara_ats.away_percentage > 50:
        print(f"  ✓ Solid away ATS record ({niagara_ats.away_percentage:.1f}%)")
        print("  ✓ Can slow the game to their preferred pace")
    print("  ✓ Recent form equally strong (3-2)")
    print("  ✓ Experience in road conference games")
    
    print()
    
    # Final recommendation
    print("=" * 90)
    print("FINAL RECOMMENDATION")
    print("=" * 90)
    print()
    
    confidence = "HIGH" if edge >= 2.0 else "MODERATE" if edge >= 1.0 else "LOW-MODERATE"
    
    print(f"PICK: {favorite} -{predicted_spread:.1f}")
    print(f"ALTERNATE: TOTAL {'OVER' if predicted_total > 135 else 'UNDER'} {round(predicted_total)}")
    print(f"CONFIDENCE: {confidence}")
    print()
    
    print("ANALYSIS SUMMARY:")
    print("  Manhattan hosts Niagara in a key MAAC conference matchup.")
    print("  The home team has a slight edge in offensive efficiency")
    print("  while Niagara boasts the better defense.")
    print()
    print("  Key Factor: Manhattan's home court advantage (+3.5) combined")
    print("  with their faster pace should be decisive in this matchup.")
    print("  Niagara will try to slow the game down, but Manhattan's")
    print("  familiarity with their home venue gives them the edge.")
    print()
    print(f"  Expected Score: Manhattan {manhattan_score:.0f}, Niagara {niagara_score:.0f}")
    print(f"  Recommended Play: Manhattan -{predicted_spread:.1f}")
    print(f"  Risk Level: {'2%' if confidence == 'HIGH' else '1-1.5%'} of bankroll")
    print()
    
    # Additional context
    print("-" * 90)
    print("GAME CONTEXT")
    print("-" * 90)
    print()
    print("CONFERENCE: MAAC (Metro Atlantic Athletic Conference)")
    print("VENUE: Draddy Gymnasium (Riverdale, Bronx, NY)")
    print("CAPACITY: ~2,500")
    print("IMPORTANCE: Mid-season conference game affecting tournament seeding")
    print("RIVALRY: Moderate - geographic proximity (both in NY/New England region)")
    print("STYLE CLASH: Manhattan's up-tempo style vs Niagara's methodical approach")
    print()
    print("BETTING MARKETS:")
    print("  Side: Manhattan likely favored by 4-6 points")
    print("  Total: Likely set around 135-138 points")
    print("  Moneyline: Manhattan ~-200, Niagara ~+170")
    print()
    
    print("=" * 90)
    print("END OF ANALYSIS")
    print("=" * 90)
    print()
    print("DISCLAIMER:")
    print("This prediction uses Billy Walters' framework with estimated statistics.")
    print("For actual betting decisions:")
    print("  • Use current season statistics from reliable sources")
    print("  • Check latest injury reports and lineup changes")
    print("  • Monitor line movement and market sentiment")
    print("  • Always practice responsible bankroll management")
    print("  • Never bet more than you can afford to lose")
    print()


def main():
    """
    Run Manhattan vs Niagara prediction
    """
    run_prediction()


if __name__ == "__main__":
    main()
