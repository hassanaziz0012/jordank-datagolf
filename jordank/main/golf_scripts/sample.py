import requests
import pandas as pd
import numpy as np

def get_data():
    # Fetch data from the first API
    response = requests.get("https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market=win&odds_format=american&file_format=json&key=30ad309cf5e6335f0fe4743b0aec")
    data = response.json()

    # Extract relevant information and put into a DataFrame
    data = [i for i in data['odds'] if 'betcris' in i]
    df = pd.DataFrame(data)

    # Fetch datagolf_rank data from the second API
    response_rank = requests.get("https://feeds.datagolf.com/preds/get-dg-rankings?key=30ad309cf5e6335f0fe4743b0aec")
    rank_data = response_rank.json()

    # Extract the 'rankings' list which is nested inside the json response
    rankings = rank_data['rankings']

    # Convert it to a DataFrame
    df_rank = pd.DataFrame(rankings)

    # Merge both DataFrames on "dg_id"
    df = pd.merge(df, df_rank[['dg_id', 'datagolf_rank']], on='dg_id', how='left')

    # Keep only columns "betcris", "player_name", "datagolf_rank", and "dg_id"
    df = df[['betcris', 'player_name', 'datagolf_rank', 'dg_id']]

    # Ensure the 'betcris' column is numeric
    df['betcris'] = pd.to_numeric(df['betcris'], errors='coerce')

    # Apply the formula and create a new column 'win_pct'
    df['win_pct'] = np.where(df['betcris'] > 0, 100 / (df['betcris'] + 100), np.abs(df['betcris']) / (np.abs(df['betcris']) + 100))

    # Convert 'win_pct' to a percentage with two decimal places
    df['win_pct'] = (df['win_pct'] * 100).apply(lambda x: '{:.2f}%'.format(x))

    # Add 'rank' column that ranks 'betcris'
    df['rank'] = df['betcris'].rank(method='min')

    df['Last_Name'] = df['player_name'].str.rsplit(", ").str.get(0)
    df['First_Name'] = df['player_name'].str.split(",").str[1]
    df['Full_Name'] = df['First_Name'] + " " + df['Last_Name']

    # Sort by 'rank'
    df = df.sort_values('rank')

    data_cols = [
        'Full_Name',
        'rank',
        'betcris',
        'win_pct',
        'datagolf_rank',
        'dg_id'
    ]

    df = df[data_cols]
    return df