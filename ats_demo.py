"""
Complete ATS Tracking Demonstration
Shows both manual tracking and TeamRankings.com import
"""

from ats_tracker import ATSTracker
from teamrankings_importer import TeamRankingsImporter


def main():
    print("=" * 80)
    print("COLLEGE BASKETBALL ATS TRACKING - COMPLETE DEMONSTRATION")
    print("=" * 80)
    print()
    
    # =========================================================================
    # PART 1: Manual Game Tracking (Track games as they happen)
    # =========================================================================
    print("PART 1: MANUAL GAME TRACKING")
    print("-" * 80)
    print()
    
    tracker = ATSTracker()
    
    print("Adding recent games with results...")
    print()
    
    # Example: You watched these games and want to track ATS performance
    recent_games = [
        # Date, Home, Away, Home Score, Away Score, Spread
        ("2026-02-10", "Duke", "UNC", 79, 76, -2.5),      # Duke wins by 3, covers
        ("2026-02-10", "Kansas", "Baylor", 82, 79, -4.0), # Kansas wins by 3, doesn't cover
        ("2026-02-11", "Houston", "UCF", 85, 68, -15.5),  # Houston wins by 17, covers
        ("2026-02-11", "Purdue", "Indiana", 78, 75, -5.5),# Purdue wins by 3, doesn't cover
        ("2026-02-12", "Arizona", "Oregon", 88, 80, -9.0),# Arizona wins by 8, doesn't cover
    ]
    
    for date, home, away, h_score, a_score, spread in recent_games:
        result = tracker.add_game(date, home, away, h_score, a_score, spread)
        
        # Show what happened
        margin = h_score - a_score
        if spread < 0:
            line = f"{home} -{abs(spread)}"
        else:
            line = f"{away} -{abs(spread)}"
        
        print(f"{date}: {home} {h_score}, {away} {a_score} (Line: {line})")
        print(f"   Actual margin: {home} by {margin}")
        print(f"   ATS Result: {home} ({result['home_result']}), "
              f"{away} ({result['away_result']})")
        print()
    
    # Show stats from manual tracking
    print("\nManually Tracked Team Statistics:")
    print("-" * 80)
    tracker.display_team_stats("Duke")
    tracker.display_leaderboard(min_games=1, top_n=5)
    
    # =========================================================================
    # PART 2: Import from TeamRankings.com (Full season data)
    # =========================================================================
    print("\n" + "=" * 80)
    print("PART 2: IMPORT FROM TEAMRANKINGS.COM")
    print("-" * 80)
    print()
    
    print("Loading ATS records from TeamRankings.com...")
    print("(Using current 2025-26 season data)")
    print()
    
    importer = TeamRankingsImporter()
    importer.import_from_csv('sample_teamrankings_data.csv')
    
    print(f"✓ Loaded {len(importer.teams_data)} teams with complete ATS records")
    print()
    
    # Show leaderboard
    importer.display_leaderboard(min_games=10, top_n=10)
    
    # Show detailed team stats
    print("Detailed Team Statistics from TeamRankings.com:")
    print("-" * 80)
    importer.display_team_stats("Houston")
    importer.display_team_stats("Duke")
    
    # Compare teams
    importer.compare_teams("Houston", "Purdue")
    
    # =========================================================================
    # PART 3: Practical Analysis (How to use this data)
    # =========================================================================
    print("\n" + "=" * 80)
    print("PART 3: PRACTICAL ANALYSIS")
    print("-" * 80)
    print()
    
    print("Finding Value Opportunities:")
    print()
    
    # Scenario: Duke vs UNC tonight, market line is Duke -6
    print("Scenario: Duke vs UNC tonight")
    print("Market Line: Duke -6")
    print()
    
    duke_data = importer.get_team_data("Duke")
    unc_data = importer.get_team_data("UNC")
    
    if duke_data and unc_data:
        print(f"Duke ATS Record: {duke_data.ats_wins}-{duke_data.ats_losses}-{duke_data.ats_pushes}")
        print(f"  Overall: {duke_data.ats_win_pct:.1%}")
        
        # Parse home record
        h_wins, h_losses, h_pushes = importer.parse_record_string(duke_data.home_ats_record)
        h_pct = h_wins / (h_wins + h_losses) if (h_wins + h_losses) > 0 else 0
        print(f"  At Home: {duke_data.home_ats_record} ({h_pct:.1%})")
        
        # Parse favorite record
        f_wins, f_losses, f_pushes = importer.parse_record_string(duke_data.favorite_ats_record)
        f_pct = f_wins / (f_wins + f_losses) if (f_wins + f_losses) > 0 else 0
        print(f"  As Favorite: {duke_data.favorite_ats_record} ({f_pct:.1%})")
        print()
        
        print(f"UNC ATS Record: {unc_data.ats_wins}-{unc_data.ats_losses}-{unc_data.ats_pushes}")
        print(f"  Overall: {unc_data.ats_win_pct:.1%}")
        
        # Parse away record
        a_wins, a_losses, a_pushes = importer.parse_record_string(unc_data.away_ats_record)
        a_pct = a_wins / (a_wins + a_losses) if (a_wins + a_losses) > 0 else 0
        print(f"  On Road: {unc_data.away_ats_record} ({a_pct:.1%})")
        
        # Parse underdog record
        u_wins, u_losses, u_pushes = importer.parse_record_string(unc_data.underdog_ats_record)
        u_pct = u_wins / (u_wins + u_losses) if (u_wins + u_losses) > 0 else 0
        print(f"  As Underdog: {unc_data.underdog_ats_record} ({u_pct:.1%})")
        print()
        
        print("Analysis:")
        if duke_data.ats_win_pct >= 0.55:
            print(f"✓ Duke covers at {duke_data.ats_win_pct:.1%} rate - above 55% threshold")
        else:
            print(f"✗ Duke covers at {duke_data.ats_win_pct:.1%} rate - below 55% threshold")
        
        if h_pct >= 0.60:
            print(f"✓ Duke at home covers at {h_pct:.1%} - strong home ATS record")
        
        if u_pct >= 0.55:
            print(f"✓ UNC as underdog covers at {u_pct:.1%} - worth considering")
        
        print()
        print("Recommendation: Use this ATS data along with Billy Walters power ratings")
        print("to identify games where your model disagrees with the market.")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("Two Ways to Track ATS Records:")
    print()
    print("1. MANUAL TRACKING (ats_tracker.py)")
    print("   • Track games as they happen")
    print("   • Calculate ATS results automatically")
    print("   • Build your own historical database")
    print("   • Best for: Current season tracking")
    print()
    print("2. TEAMRANKINGS.COM IMPORT (teamrankings_importer.py)")
    print("   • Import complete season data")
    print("   • Comprehensive statistics available")
    print("   • Home/Away and Favorite/Underdog splits")
    print("   • Best for: Historical analysis and research")
    print()
    print("Combine ATS data with Billy Walters power ratings for:")
    print("  • Identifying value opportunities")
    print("  • Finding teams that consistently cover")
    print("  • Spotting situational advantages")
    print("  • Making data-driven betting decisions")
    print()
    print("See ATS_GUIDE.md for complete documentation!")
    print("=" * 80)


if __name__ == "__main__":
    main()
