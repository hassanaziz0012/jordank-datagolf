import requests
import pandas as pd


def get_data():
    result = {}

    url = "https://feeds.datagolf.com/preds/live-tournament-stats?stats=sg_ott,distance,accuracy,sg_t2g,sg_app,gir,prox_fw,sg_putt,scrambling&round=event_avg&display=value&key=30ad309cf5e6335f0fe4743b0aec"

    response = requests.request("GET", url).json()

    response = response['live_stats']

    df = pd.DataFrame(response)

    data_cols = [
        'position',
        'player_name',
        'total',
        'round',
        'thru',
        'accuracy',
        'gir',
        'sg_t2g',
        'distance',
        'scrambling',
        'dg_id'
    ]

    df = df[data_cols]

    df['Last_Name'] = df['player_name'].str.rsplit(", ").str.get(0)

    df['First_Name'] = df['player_name'].str.split(",").str[1]

    df['Full_Name'] = df['First_Name'] + " " + df['Last_Name']

    df['holes_left'] = 18 - df['thru']

    data_cols_2 = [
        'position',
        'Full_Name',
        'total',
        'thru',
        'round',
        'holes_left',
        'accuracy',
        'gir',
        'sg_t2g',
        'distance',
        'scrambling',
        'dg_id'
    ]

    df2 = df[data_cols_2]

    # INTRODUCE DG RANKINGS

    url2 = "https://feeds.datagolf.com/preds/get-dg-rankings?file_format=json&key=30ad309cf5e6335f0fe4743b0aec"

    response2 = requests.request("GET", url2).json()

    response2 = response2['rankings']

    dfrankings = pd.DataFrame(response2)

    dfrankings['Last_Name'] = dfrankings['player_name'].str.rsplit(", ").str.get(0)

    dfrankings['First_Name'] = dfrankings['player_name'].str.split(",").str[1]

    dfrankings['Full_Name'] = dfrankings['First_Name'] + \
        " " + dfrankings['Last_Name']
    data_cols2 = [
        'Full_Name',
        'datagolf_rank',
        'owgr_rank',
        'primary_tour',
        'country',
        'player_name',
        'dg_id'
    ]

    dfrankings = dfrankings[data_cols2]

    dfmerge = df2.merge(dfrankings, left_on='Full_Name',
                        right_on='Full_Name', how='left')


    data_cols_3 = [
        'position',
        'Full_Name',
        'total',
        'thru',
        'round',
        'holes_left',
        'accuracy',
        'gir',
        'sg_t2g',
        'distance',
        'scrambling',
        'datagolf_rank',
        'owgr_rank',
        'dg_id_x'
    ]

    dffinal = dfmerge[data_cols_3]

    # dffinal.rename(columns = {'dg_id_x':'dg_id'}, inplace = True)

    # dffinal.rename(columns = {'owgr_rank':'World Rank'}, inplace = True)

    # dffinal.set_index('position', inplace=True)

    # print(dffinal)

    # Find the min and max value from the 'total' column
    min_total = dffinal['total'].min()
    max_total = dffinal['total'].max()

    # Create a list of all numbers between the min and max total
    total_range = list(range(int(min_total), int(max_total) + 1))

    # Create a new DataFrame with 'total' column
    new_df = pd.DataFrame(total_range, columns=['total'])

    # print(new_df)

    # Merge the new DataFrame with the original DataFrame on 'total', keeping all 'total's in the new DataFrame
    merged_df = pd.merge(
        new_df, dffinal[['total', 'datagolf_rank']], on='total', how='left')

    # Pivot the DataFrame to get 'DG Rank' values as new columns for each corresponding 'total'
    pivoted_df = merged_df.pivot_table(
        index='total',
        columns=merged_df.groupby('total').cumcount().add(1),
        values='datagolf_rank', aggfunc='first'
    )

    # Clean up column names
    pivoted_df.columns = ['DG Rank ' + str(col) for col in pivoted_df.columns]

    # Reset index for final DataFrame
    final_df = pivoted_df.reset_index()
    final_df = final_df.fillna('')


    final_df.rename(columns={'datagolf_rank': 'DG Rank'}, inplace=True)
    final_df.set_index('total', inplace=True)

    # final_df.to_csv('Live/Live_Leaderboard_DG.csv')

    # Write the DataFrame to an Excel file
    # writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')

    # final_df.to_excel(writer, sheet_name='Sheet1')

    # Access the xlsxwriter workbook and worksheet objects from the dataframe.
    # workbook = writer.book
    # worksheet = writer.sheets['Sheet1']

    # Define the format for highlighting.
    # green_format = workbook.add_format({'bg_color': '#C6EFCE'})
    # yellow_format = workbook.add_format({'bg_color': '#FFEB9C'})
    # red_format = workbook.add_format({'bg_color': '#FFC7CE'})

    # Get last row
    last_row = len(final_df) + 1

    # Apply conditional formatting to all columns except the first one
    # for col_num, col_letter in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ', start=2):
    #     if col_letter not in ['A']:  # Skip the first column
    #         # Green format for numbers between 1 and 25
    #         worksheet.conditional_format(
    #             f'{col_letter}2:{col_letter}{last_row}',
    #             {
    #                 'type': 'cell',
    #                 'criteria': 'between',
    #                 'minimum': 1,
    #                 'maximum': 25,
    #                 'format': green_format
    #             })
    #         # Yellow format for numbers between 26 and 50
    #         worksheet.conditional_format(
    #             f'{col_letter}2:{col_letter}{last_row}',
    #             {
    #                 'type': 'cell',
    #                 'criteria': 'between',
    #                 'minimum': 26,
    #                 'maximum': 50,
    #                 'format': yellow_format
    #             })
    #         # Red format for numbers between 51 and 80
    #         worksheet.conditional_format(
    #             f'{col_letter}2:{col_letter}{last_row}', {
    #                 'type': 'cell',
    #                 'criteria': 'between',
    #                 'minimum': 51,
    #                 'maximum': 80,
    #                 'format': red_format
    #             })

    # END OF Data retrieval and manipulation

    # Find the min (best) score, which is the lead
    lead_score = dffinal['total'].min()

    # Create a dataframe that counts the number of occurrences of each score
    score_counts = dffinal['total'].value_counts().sort_index().reset_index()
    score_counts.columns = ['total', 'count']

    # Create a new dataframe with the offsets from the lead and their respective counts
    offset_counts = score_counts[score_counts['total'].between(lead_score, lead_score + 5)].copy()
    offset_counts['offset'] = offset_counts['total'] - lead_score
    offset_counts = offset_counts[['offset', 'count']]

    # Set the offset as the index
    offset_counts.set_index('offset', inplace=True)

    # Write the offset_counts dataframe to the second sheet of the Excel file
    # offset_counts.to_excel(writer, sheet_name='Sheet2')

    # Create a new dataframe that counts the cumulative number of players within each offset from the lead
    cumulative_counts = score_counts[score_counts['total'].between(lead_score, lead_score + 5)].copy()
    cumulative_counts['within_offset'] = cumulative_counts['total'] - lead_score
    cumulative_counts['cumulative_count'] = cumulative_counts['count'].cumsum()

    # Create a dataframe with just the 'within_offset' and 'cumulative_count' columns, and set 'within_offset' as the index
    cumulative_counts = cumulative_counts[['within_offset', 'cumulative_count']]
    cumulative_counts.set_index('within_offset', inplace=True)

    # Write the cumulative_counts dataframe to the third sheet of the Excel file
    # cumulative_counts.to_excel(writer, sheet_name='Sheet3')

    # Create a new dataframe that counts the cumulative number of players within each offset from the lead, excluding the leaders
    cumulative_counts_excluding_leaders = score_counts[score_counts['total'].between(lead_score + 1, lead_score + 5)].copy()
    cumulative_counts_excluding_leaders['within_offset'] = cumulative_counts_excluding_leaders['total'] - lead_score
    cumulative_counts_excluding_leaders['cumulative_count'] = cumulative_counts_excluding_leaders['count'].cumsum()

    # Create a dataframe with just the 'within_offset' and 'cumulative_count' columns, and set 'within_offset' as the index
    cumulative_counts_excluding_leaders = cumulative_counts_excluding_leaders[['within_offset', 'cumulative_count']]
    cumulative_counts_excluding_leaders.set_index('within_offset', inplace=True)

    # Write the cumulative_counts_excluding_leaders dataframe to the fourth sheet of the Excel file
    # cumulative_counts_excluding_leaders.to_excel(writer, sheet_name='Sheet4')

    # Save the changes and close the file, only once at the end
    # writer.close()
    result = {
        "final_df": final_df,
        "offset_counts": offset_counts,
        "cumulative_counts": cumulative_counts,
        "cumulative_counts_excluding_leaders": cumulative_counts_excluding_leaders
    }
    return result
