from teamrankings_importer import TeamRankingsImporter

# Test CSV import
importer = TeamRankingsImporter()
importer.import_from_csv('sample_teamrankings_data.csv')

print("CSV Import Test")
print("=" * 70)
print(f"Loaded {len(importer.teams_data)} teams")
print()

# Show a few teams
for team in ['Houston', 'Duke', 'UNC']:
    data = importer.get_team_data(team)
    if data:
        print(f"{team}: {data.ats_wins}-{data.ats_losses}-{data.ats_pushes} ({data.ats_win_pct:.1%})")

print()
importer.display_leaderboard(min_games=10, top_n=5)
