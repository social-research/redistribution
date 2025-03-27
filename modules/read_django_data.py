"""
Created on Jun 1 2023
@author: milenavt
Purpose: Helping functions for plotting
"""

import sqlite3
import numpy as np
import pandas as pd
from ineq import *
from concentration_library import gini_popadj, mad
from scipy.stats import kurtosis
from pandas.api.types import CategoricalDtype

NET_CATS = CategoricalDtype(categories=['repr', 'segr', 'homo', 'hete', 'rich', 'poor'])
STAT_CATS = CategoricalDtype(categories=['P', 'R'])

# Equivalency of treatments
# P: poor = homo, rich = hete
# R: rich = homo, poor = hete 
EQUIVALENCY = {'rich': {'P': ['rich', 'hete'], 'R': ['rich', 'homo']},
            'poor': {'P': ['poor', 'homo'], 'R': ['poor', 'hete']},
            'homo': {'P': ['homo', 'poor'], 'R': ['homo', 'rich']},
            'hete': {'P': ['hete', 'rich'], 'R': ['hete', 'poor']},
            'repr': {'P': ['repr'], 'R': ['repr']},
            'segr': {'P': ['segr'], 'R': ['segr']},
            }

    


### TO DO - TRANSFORM GROUPS + 100, 200, etc.

def combine_datasets(datasets, fun, csv_path=''):
    dfs = [fun(db, batchnum) for db, batchnum in datasets]
    df = pd.concat(dfs, ignore_index=True)
    if csv_path:
        df.to_csv(csv_path, index=False)
    return df


def get_quiz_results(database, batchnum):
    """Read sqlite database and return pandas dataframe
    with quiz results per player.
    """
    db = sqlite3.connect(database)
    c = db.cursor()
    c.execute("""
        SELECT participant_id, answer_date, attempt, a1, a2, a3
        FROM vgame_quiz
    """)
    df = pd.DataFrame(c.fetchall())
    c.close()
    db.close()
    
    df.columns = ['participant_id', 'answer_date', 'attempt', 
                  'a1', 'a2', 'a3']
    return df


def get_player_records(database, batchnum):
    """Read sqlite database and return pandas dataframe
    with status, award and vote per player.
    """
    db = sqlite3.connect(database)
    c = db.cursor()
    c.execute("""
        SELECT t.network, g.id, gr.round,  
               s.player_id, s.id, s.status, s.award, d.vote
        FROM vgame_decision as d
        JOIN vgame_subject AS s ON d.subject_id = s.id
        JOIN vgame_groupround AS gr ON d.group_round_id = gr.id
        JOIN vgame_group AS g ON gr.group_id = g.id
        JOIN vgame_treatment AS t ON g.treatment_id = t.id
    """)
    df = pd.DataFrame(c.fetchall())
    c.close()
    db.close()
    
    df.columns = ['network_type', 'group', 'round', 
                  'pid', 'sid', 'status', 'award', 'vote']
    df['batch'] = batchnum
    df['group'] += batchnum*100
    df['sid'] += batchnum*1000
    df['network_type'] = df['network_type'].astype(NET_CATS)
    df['status'] = df['status'].astype(STAT_CATS)
    df = df[['batch', 'network_type', 'group', 'round', 
             'pid', 'sid', 'status', 'award', 'vote']]
    df = df.sort_values(by=['network_type', 'group', 'round', 'pid'])

    # There are several duplicate records (database errors), keep last recorded !!!
    bef = df.shape[0]
    df = df.drop_duplicates(subset=['batch', 'network_type', 'group', 'pid', 'round'], keep='last')
    print(f"WARNING! Removed {bef - df.shape[0]} duplicate records (database errors).")

    return df

def categorize_df(df):
    df['network_type'] = df['network_type'].astype(NET_CATS)
    if 'status' in df.columns:
        df['status'] = df['status'].astype(STAT_CATS)
    return df

def get_group_outcomes(database, batchnum):
    """Read sqlite database and return pandas dataframe
    with selected media_vote and tax_benefit per group, per round.
    """
    db = sqlite3.connect(database)
    c = db.cursor()
    c.execute("""
        SELECT t.network, g.id, gr.round, 
               gr.median_vote, gr.tax_benefit
        FROM vgame_groupround AS gr
        JOIN vgame_group AS g ON gr.group_id = g.id
        JOIN vgame_treatment AS t ON g.treatment_id = t.id
        WHERE NOT gr.round=?
    """, (4,))
    df = pd.DataFrame(c.fetchall())
    c.close()
    db.close()

    df.columns = ['network_type', 'group', 'round', 
                  'median_vote', 'tax_benefit']
    df['batch'] = batchnum
    df['group'] += batchnum*100
    df['network_type'] = df['network_type'].astype(NET_CATS)
    df = df[['batch', 'network_type', 'group', 'round', 
                  'median_vote', 'tax_benefit']]
    df = df.sort_values(by=['network_type', 'group', 'round'])

    return df


def get_player_votes_with_context(DATAFILE, batchnum): 
    """"""
    # Get player voting data (excluding survey round)
    vote_df = get_player_records(DATAFILE, batchnum)
    vote_df = vote_df[vote_df['vote'] != 999]
    # Get group data
    group_df = get_group_outcomes(DATAFILE, batchnum)
    # Merge previous-round group results with current-round decisions
    temp_df = group_df[group_df['round'] != 3]
    temp_df['round'] += 1
    vote_df = pd.merge(vote_df, temp_df, 
                    on=['batch', 'network_type', 'group', 'round'], 
                    how='left')
    # Estimate player's current score when making decision
    vote_df['score'] = vote_df['award'] + vote_df['tax_benefit'] - round((vote_df['award']*vote_df['median_vote'])/100, 0)
    # Score in the first round is the same as award
    vote_df.loc[vote_df['round'] == 1, 'score'] = vote_df['award']
    return vote_df


def get_participant_data(database, batchnum):
    """"""
    db = sqlite3.connect(database)
    c = db.cursor()
    c.execute("""
        SELECT s.id, s.age, s.gender, s.race, s.education, 
              s.religion, s.politics, s.income, s.percentile, s.tax,
              s.award_satisfied, s.award_dist_fair, 
              s.result_satisfied, s.result_dist_fair,
              s.rationale, s.group_feel, t.network, g.id, s.status
        FROM vgame_subject AS s
        JOIN vgame_group AS g ON s.group_id = g.id
        JOIN vgame_treatment AS t ON g.treatment_id = t.id
    """)
    df = pd.DataFrame(c.fetchall())
    c.close()
    db.close()
    df.columns = ['sid', 'age', 'gender',' race', 'education', 
                  'religion', 'politics', 'income', 'percentile', 'tax',
                  'award_satisfied', 'award_dist_fair', 
                  'result_satisfied', 'result_dist_fair',
                  'rationale', 'group_feel', 'network_type', 'group', 'status']
    df['batch'] = batchnum
    df['sid'] += batchnum*1000
    num_cols = ['age', 'politics', 'income', 'percentile', 'tax',
        'award_satisfied', 'award_dist_fair', 
        'result_satisfied', 'result_dist_fair']
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')
    df['network_type'] = df['network_type'].astype(NET_CATS)
    df = df.sort_values(by=['sid'])
    return df


def get_group_outcomes_from_votes(df, csv_path=''):
    """Calculate game-round information from individual decisions.
    Return as pandas dataframe.
    """
    # Estimate new median_vote and tax_benefit from individual decisions in round
    df.drop(columns=['median_vote', 'tax_benefit', 'score'])
    df = calculate_group_stats(df, ['batch', 
                                    'network_type', 
                                    'group', 
                                    'round'])
    # Leave only unique game-round entries
    df = df[['batch', 'network_type', 'group', 'round', 'median_vote', 
             'score_gini', 'vote_var', 'vote_mad', 'vote_kurt']].drop_duplicates()
    df = df.sort_values(by=['network_type', 'group', 'round'])
    if csv_path:
        df.to_csv(csv_path, index=False)

    return df

def calculate_group_stats(df, group_vars):
    # Estimate new median_vote and tax_benefit from individual decisions in round
    df['median_vote'] = df.groupby(group_vars)['vote'].transform(lambda x: int( round(np.median(x), 0) ))
    df['tax_paid'] = round(df['median_vote'] * df['award'] / 100, 0) 
    df['tax_benefit'] = df.groupby(group_vars)['tax_paid'].transform(lambda x: round(sum(x) / 4, 0) )
    df['score'] = df['award'] - df['tax_paid'] + df['tax_benefit']
           
    # Group Gini
    df['score_gini'] = df.groupby(group_vars)['score'].transform(gini_popadj)
    
    # Vote polarization: variance (spread)
    df['vote_var'] = df.groupby(group_vars)['vote'].transform(np.var)
    # Vote polarization: mean absolute deviation (spread)
    df['vote_mad'] = df.groupby(group_vars)['vote'].transform(mad)
    # Vote polarization: kurtosis  (bimodality, negative means flatter, 
    # approaching -2 is bimodal) (DiMaggio et al. 1996)
    df['vote_kurt'] = df.groupby(group_vars)['vote'].transform(kurtosis)
    return df


def get_participant_turnout(df, csv_path=''):
    """Calculate turnout for each player."""
    # Estimate over rounds 2, 3, and 4
    df3 = df[['batch', 'network_type', 'group', 'pid', 'vote']][ df['round'] !=1 ].groupby(['batch', 'network_type', 'group', 'pid']).count().reset_index()
    df3.columns = ['batch', 'network_type', 'group', 'pid', 'turnout3']
    df3['turnout3_frac'] = df3['turnout3'] / 3
    
    # Estimate over voting rounds only (2 and 3)
    df2 = df[['batch', 'network_type', 'group', 'pid', 
              'vote']][ (df['round'] == 2) | (df['round'] == 3) ].groupby(['batch', 
                                                                           'network_type', 
                                                                           'group', 
                                                                           'pid']).count().reset_index()
    df2.columns = ['batch', 'network_type', 'group', 'pid', 'turnout2']
    df2['turnout2_frac'] = df2['turnout2'] / 2

    turn_df = pd.merge(df[['batch', 'network_type', 'group', 
                           'pid', 'sid', 'status', 'award']].drop_duplicates(), 
                       df2, on=['batch', 'network_type', 'group', 'pid'])
    turn_df = pd.merge(turn_df, df3, on=['batch', 'network_type', 'group', 'pid'])
    turn_df = turn_df.sort_values(by=['network_type', 'group', 'pid'])

    if csv_path:
        turn_df.to_csv(csv_path, index=False)

    return turn_df

def merge_with_prolific_demos(df, datasets, prolific_files, csv_path=''):
    # Get Prolific ids matched to sid
    ids = []
    for dataset, batchnum in datasets:
        db = sqlite3.connect(dataset)
        c = db.cursor()
        c.execute("""
            SELECT id, participant_id
            FROM vgame_subject
        """)
        dfid = pd.DataFrame(c.fetchall())
        c.close()
        db.close()

        dfid.columns = ['sid', 'participant_id']
        dfid['sid'] += batchnum*1000
        ids.append(dfid)
    df_ids = pd.concat(ids, ignore_index=True)

    # Get Prolific demographic data
    df_demo = get_prolific_demo_data(prolific_files)

    # Merge with demographic data
    dfmerged = pd.merge(df_ids, df_demo, on='participant_id', how='left').drop(columns='participant_id')
    dfnew = pd.merge(df, dfmerged, on='sid', how='left')

    if csv_path:
        dfnew.to_csv(csv_path, index=False)

    return dfnew


def get_prolific_demo_data(prolific_files):
    demos = []
    for dataset in prolific_files:
        dfdemo = pd.read_csv(dataset)[['Participant id', 'Time taken', 'Total approvals', 
                                       'Age', 'Sex', 'Ethnicity simplified', 'Country of birth', 
                                       'Language', 'Student status', 'Employment status']]
        demos.append(dfdemo)
    df_demo = pd.concat(demos, ignore_index=True)
    df_demo.columns = ['participant_id', 'p_time_taken', 'p_total_approvals', 
                        'p_age', 'p_sex', 'p_ethnicity', 'p_country_of_birth', 
                        'p_language', 'p_student_status', 'p_employment_status']
    return df_demo


def get_recombinations(vote_df, reps, csv_path=''):

    # Take results from first round, randomly draw to form groups, repeat X times
    vote_1 = vote_df[vote_df['round']==1][['network_type', 'sid', 'status', 'award', 'vote']]

    # Draw 9 rich, 15 poor from respective treatments
    df_reps = []

    for net in EQUIVALENCY:
        sim_P = vote_1[(vote_1['status']=='P') 
                        & (vote_1['network_type'].isin(EQUIVALENCY[net]['P']))]
        sim_R = vote_1[(vote_1['status']=='R') 
                        & (vote_1['network_type'].isin(EQUIVALENCY[net]['R']))]

        for rep in range(reps):
            p = sim_P.sample(n=15)
            r = sim_R.sample(n=9)
            df = pd.concat([p, r], ignore_index=True)
            df.columns = ['network_type_old', 'sid', 'status', 'award', 'vote']
            df['network_type'] = net
            df['group'] = rep
            df_reps.append(df[['network_type', 'group', 'sid', 'status', 'award', 'vote']])

    df_sim = pd.concat(df_reps, ignore_index=True)
    df_sim = calculate_group_stats(df_sim, ['network_type', 'group'])

    # Leave only unique game-round entries
    df_sim = df_sim[['network_type', 'group', 'median_vote', 
             'score_gini', 'vote_var', 'vote_mad', 'vote_kurt']].drop_duplicates()
    df_sim = df_sim.sort_values(by=['network_type', 'group'])
    # Make categorical variables
    df_sim['network_type'] = df_sim['network_type'].astype(NET_CATS)

    if csv_path:
        df_sim.to_csv(csv_path, index=False)

    return df_sim


def get_resplits(vote_df, seed=None, csv_path=''):

    # Take results from first round, randomly split into groups
    vote_1 = vote_df[vote_df['round']==1][['network_type', 'sid', 'status', 'award', 'vote']]

    # Draw 9 rich, 15 poor from respective treatments
    df_reps = []

    for net in EQUIVALENCY:
        # Select data and shuffle
        sim_P = vote_1[(vote_1['status']=='P') 
                        & (vote_1['network_type'].isin(EQUIVALENCY[net]['P']))]
        sim_P = sim_P.sample(frac=1, random_state=seed).reset_index(drop=True)
        sim_R = vote_1[(vote_1['status']=='R') 
                        & (vote_1['network_type'].isin(EQUIVALENCY[net]['R']))]
        sim_R = sim_R.sample(frac=1, random_state=seed*seed).reset_index(drop=True)

        bp, ep = 0, 15
        br, er = 0, 9
        gnum = 0
        while ep < sim_P.shape[0] + 1:
            p = sim_P.loc[bp:ep]
            r = sim_R.loc[br:er]
            df_part = pd.concat([p, r], ignore_index=True)
            df_part.columns = ['network_type_old', 'sid', 'status', 'award', 'vote']
            df_part['network_type'] = net
            df_part['group'] = gnum
            df_reps.append(df_part[['network_type', 'group', 'sid', 'status', 'award', 'vote']])
            bp += 15
            ep +=15
            br += 9
            er +=9
            gnum +=1

    df = pd.concat(df_reps, ignore_index=True)

    df = calculate_group_stats(df, ['network_type', 'group'])

    # Leave only unique game-round entries
    df = df[['network_type', 'group', 'median_vote', 
             'score_gini', 'vote_var', 'vote_mad', 'vote_kurt']].drop_duplicates()
    df = df.sort_values(by=['network_type', 'group'])
    # Make categorical variables
    df['network_type'] = df['network_type'].astype(NET_CATS)

    if csv_path:
        df.to_csv(csv_path, index=False)

    return df

def get_assigned_with_equivalency(vote_df, csv_path=''):
    # Take results from first round
    vote_1 = vote_df[vote_df['round']==1][['network_type', 'group', 'sid', 'status', 'award', 'vote']]

    extras = {'rich': {'P': 'hete', 'R': 'homo'},
            'poor': {'P': 'homo', 'R': 'hete'},
            'homo': {'P': 'poor', 'R': 'rich'},
            'hete': {'P': 'rich', 'R': 'poor'}
            }

    # Draw the respective participants from the equivalent treatments
    df_reps = [vote_1]

    for net in extras:

        # Select data
        sim_P = vote_1[(vote_1['status']=='P') 
                        & (vote_1['network_type']==extras[net]['P'])]
        sim_R = vote_1[(vote_1['status']=='R') 
                        & (vote_1['network_type']==extras[net]['R'])]
        
        # Number groups by order
        sim_P = sim_P.sort_values(by=['group'])
        sim_P['idx'] = sim_P['group'].rank(method='dense').add(900).astype(int)
        
        sim_R = sim_R.sort_values(by=['group'])
        sim_R['idx'] = sim_R['group'].rank(method='dense').add(900).astype(int)

        # Combine and rename columns
        df_part = pd.concat([sim_P, sim_R], ignore_index=True)
        df_part.columns = ['network_type_old', 'group_old', 'sid', 'status', 'award', 'vote', 'group']
        df_part['network_type'] = net
        df_reps.append(df_part[['network_type', 'group', 'sid', 'status', 'award', 'vote']])

    df = pd.concat(df_reps, ignore_index=True)

    df = calculate_group_stats(df, ['network_type', 'group'])

    # Leave only unique game-round entries
    df = df[['network_type', 'group', 'median_vote', 
             'score_gini', 'vote_var', 'vote_mad', 'vote_kurt']].drop_duplicates()
    df = df.sort_values(by=['network_type', 'group'])
    # Make categorical variables
    df['network_type'] = df['network_type'].astype(NET_CATS)

    if csv_path:
        df.to_csv(csv_path, index=False)

    return df

def get_whole_sample_estimates(vote_df, csv_path=''):
    # Take results from first round, randomly draw to form groups, repeat X times
    vote_1 = vote_df[vote_df['round']==1][['network_type', 'sid', 'status', 'award', 'vote']]

    # Draw all in respective treatments
    df_reps = []

    for net in EQUIVALENCY:
        sim_P = vote_1[(vote_1['status']=='P') 
                        & (vote_1['network_type'].isin(EQUIVALENCY[net]['P']))]
        sim_R = vote_1[(vote_1['status']=='R') 
                        & (vote_1['network_type'].isin(EQUIVALENCY[net]['R']))]

        df = pd.concat([sim_P, sim_R], ignore_index=True)
        df.columns = ['network_type_old', 'sid', 'status', 'award', 'vote']
        df['network_type'] = net
        df_reps.append(df[['network_type', 'sid', 'status', 'award', 'vote']])

    df = pd.concat(df_reps, ignore_index=True)
    df = calculate_group_stats(df, ['network_type'])

    # Leave only unique game-round entries
    df = df[['network_type', 'median_vote', 
             'score_gini', 'vote_var', 'vote_mad', 'vote_kurt']].drop_duplicates()
    df = df.sort_values(by=['network_type'])
    # Make categorical variables
    df['network_type'] = df['network_type'].astype(NET_CATS)

    if csv_path:
        df.to_csv(csv_path, index=False)

    return df
