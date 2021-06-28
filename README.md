# esi_football

Project for projecting daily and season-long fantasy football.
Uses data from two sources requiring paid accounts: ArmChairAnalysis.com and pff.com.


## Core data files
- players.csv --- Contains a list of all players and basic information
- season_projections.csv --- Contains all projections for a player from various websites
- sites.csv --- Contains a list of all sites with projections

## TODOs
- Format projections into intermediary format
- Use AA data for players.csv
- Write algorithm to match projections with PlayerID
- Covert AA PBP data into historical data by game each season.
  - Include the position and team of the player each week.
