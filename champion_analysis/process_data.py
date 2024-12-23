import pandas as pd
import os

def process_data(file: str, options = "korea"):
    """
    Wrangles data result from extract_matchdata.py
    
    Parameters:
        file (str): Path to the input CSV file
        options (str): Regions. 'korea' needs low memory option 

    Returns:
        pd.DataFrame: A cleaned DataFrame containing champion data for each lane and team results.
        
    """
    # Validate input
    if not os.path.exists(file):
        raise FileNotFoundError(f"The file '{file}' does not exist.")
    if options not in {'korea', 'other'}:
        raise ValueError("Options must be 'korea' or 'other'.")
        
    try:
        low_memory = options == 'korea'
        df = pd.read_csv(file, header=None, index_col=0, low_memory = low_memory)
    except pd.errors.EmptyDataError:
        raise ValueError(f"File '{file}' is empty or invalid.")    
    
    # Indices 0-6 includes matchId, gameCreation, gameMode, gameType, gameVersion, mapId
    # Index 7 is queueId. Interested in queueId [400,420,430,440] for relevant game modes
    VALID_QUEUE_IDS = [400, 420, 430, 440]
    df_filtered = df[df[7].isin(VALID_QUEUE_IDS)].iloc[:, 7:]
    
    # Columns representing champions for lanes, unioned with win columns
    CHAMPION_COLUMNS_STEP = 3 # Every 3rd column starting from idx 1 represents a champion for a lane
    WIN_COLUMNS = [22, 37] # Indices for team 1 and 2 respective win status columns
    lane_and_win_columns = df_filtered.columns[1::CHAMPION_COLUMNS_STEP].union(WIN_COLUMNS)

    # Split the data into two DataFrames for the two teams
    team_dataframes = [
        df_filtered[lane_and_win_columns].iloc[:, :6],  # Team 1: First 6 columns
        df_filtered[lane_and_win_columns].iloc[:, 6:]   # Team 2: Last 6 columns
    ]
    
    # Assign meaningful column names for lanes and win status
    COLUMN_NAMES = ["Top", "Jungle", "Middle", "Bot", "Support", "Win"]
    for team_df in team_dataframes:
        team_df.columns = COLUMN_NAMES
        
    # Stack the two teams into one DataFrame
    combined_df = pd.concat(team_dataframes, ignore_index=True)        
    
    # Convert the 'Win' column from boolean (%TRUE%/%FALSE%) to integer
    combined_df['Win'] = combined_df['Win'].astype(str).str.lower().map({'true': 1, 'false': 0}).fillna(0)
    return combined_df