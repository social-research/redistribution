"""
Created on Jun 1 2023
@author: milenavt
Purpose: Helping functions for plotting
"""

import numpy as np
import pandas as pd
from ineq import *
from concentration_library import gini_popadj, mad
from scipy.stats import pearsonr, kurtosis
from pandas.api.types import CategoricalDtype

RECODE_NETS = {'representative': 'repr', 'segregated': 'segr', 'homophily': 'homo', 
               'heterophily': 'hete', 'rich visible': 'rich', 'poor visible': 'poor'}
RECODE_STATUSES = {'rich': 'R', 'poor': 'P'}
NET_CATS = CategoricalDtype(categories=['repr', 'segr', 'homo', 'hete', 'rich', 'poor'])
STAT_CATS = CategoricalDtype(categories=['P', 'R'])


def get_sim_data(dirname, prob=None):   
    """Read csv file with simulation data into pandas dataframe.
    """
    
    df = pd.read_csv(dirname, header=6) 
    
    df = df[['[run number]', 'population-size', 'num-observed', 
                 'gamma', 'a', 'b', 'wealth-assortativity', 'wealth-visibility', 
                 '[step]', 'gini', 'median-vote', 'num-observers', 
                 'observed-mean-wealth', 'observed-gini', 'observed-subj-ineq', 
                 'wealths', 'utilities', 'votes']]
    df.columns = ['run', 'pop_size', 'num_observed', 
                    'gamma', 'a', 'b', 'h', 'v', 
                    'period', 'gini', 'median_vote', 'num_observers', 
                    'observed_mean_wealth', 'observed_gini', 'observed_subj_ineq', 
                    'wealths', 'utilities', 'votes']
    
    # Actual assortativity: Correlation between own and neighbor's average wealth
    df['assortativity'] = np.vectorize(get_defacto_assortativity)(df['wealths'], df['observed_mean_wealth'])
    
    # Population inequality: Population Gini in all periods and last period
    # Confirms NetLogo estimates, so no need to duplicate
    #df['gini_new_estimate'] = np.vectorize(get_new_gini_estimate)(df['wealths'])
    
    # Vote polarization: variance (spread), kurtosis 
    #        (bimodality, negative means flatter, approaching -2 is bimodal) (DiMaggio et al. 1996)
    df['vote_var'] = np.vectorize(get_vote_variance)(df['votes'])
    df['vote_mad'] = np.vectorize(get_vote_mad)(df['votes'])
    df['vote_kurt'] = np.vectorize(get_vote_kurtosis)(df['votes'])
    
    return df


def get_sim_data_exp(dirname):   
    """Read csv file with simulation data into pandas dataframe.
    """
    
    df = pd.read_csv(dirname, header=6) 

    df = df[(df['network'] != 'equal')] # Remove 4-4 for analyses    
    df = df[['[run number]', 'gamma', 'network',
             '[step]', 'gini', 'median-vote', 'num-observers', 
             'observed-mean-wealth', 'observed-gini', 'observed-subj-ineq', 
             'statuses', 'wealths', 'utilities', 'votes']]
    df.columns = ['run', 'gamma', 'network_type', 
                  'period', 'gini', 'median_vote', 'num_observers', 
                  'observed_mean_wealth', 'observed_gini', 'observed_subj_ineq', 
                  'statuses', 'wealths', 'utilities', 'votes']
    
    df['network_type'] = df['network_type'].replace(RECODE_NETS)
    df['network_type'] = df['network_type'].astype(NET_CATS)
    
    # Actual assortativity: Correlation between own and neighbor's average wealth
    df['assortativity'] = np.vectorize(get_defacto_assortativity)(df['wealths'], df['observed_mean_wealth'])
    
    # Vote polarization: variance (spread), kurtosis 
    #        (bimodality, negative means flatter, approaching -2 is bimodal) (DiMaggio et al. 1996)
    df['vote_var'] = np.vectorize(get_vote_variance)(df['votes'])
    df['vote_mad'] = np.vectorize(get_vote_mad)(df['votes'])
    df['vote_kurt'] = np.vectorize(get_vote_kurtosis)(df['votes'])
    
    return df


def get_agent_data(df):
    
    agent_data = []
    
    for index, row in df.iterrows():

        num_obs = get_ints_from_str(row['num_observers'])
        log_num_obs = get_logints1_from_str(row['num_observers'])
        obs_mean_w = get_floats_from_str(row['observed_mean_wealth'])
        obs_gini = get_floats_from_str(row['observed_gini'])
        obs_subj_ineq = get_floats_from_str(row['observed_subj_ineq'])
        w = get_floats_from_str(row['wealths'])
        u = get_floats_from_str(row['utilities'])
        v = get_ints_from_str(row['votes'])

        data = {'run': row['run'],
                'h': row['h'], 
                'v': row['v'],
                'num_observers': num_obs,
                'log_num_observers': log_num_obs,
                'observed_mean_wealth': obs_mean_w,
                'observed_gini': obs_gini,
                'observed_subj_ineq': obs_subj_ineq,
                'wealth': w, 
                'utility': u,
                'vote': v
                }
        agent_data.append(pd.DataFrame(data=data))

    df_long = pd.concat(agent_data)
    
    # Re-number runs by treatment    
    df_long['run'] = df_long.groupby(['h', 'v'])['run'].rank('dense').astype('int')
    
    return df_long


def get_agent_data_exp(df):
    
    agent_data = []
    
    for index, row in df.iterrows():

        num_obs = get_ints_from_str(row['num_observers'])
        obs_mean_w = get_floats_from_str(row['observed_mean_wealth'])
        obs_gini = get_floats_from_str(row['observed_gini'])
        obs_subj_ineq = get_floats_from_str(row['observed_subj_ineq'])
        s = get_strs_from_str(row['statuses'])
        w = get_floats_from_str(row['wealths'])
        u = get_floats_from_str(row['utilities'])
        v = get_ints_from_str(row['votes'])

        data = {'run': row['run'],
                'network_type': row['network_type'],
                'num_observers': num_obs,
                'observed_mean_wealth': obs_mean_w,
                'observed_gini': obs_gini,
                'observed_subj_ineq': obs_subj_ineq,
                'status': s,
                'wealth': w, 
                'utility': u,
                'vote': v
                }
        agent_data.append(pd.DataFrame(data=data))

    df_long = pd.concat(agent_data)
    
    # Re-number runs by treatment    
    df_long['network_type'] = df_long['network_type'].astype(NET_CATS)
    df_long['status'] = df_long['status'].astype(STAT_CATS)
    df_long['run'] = df_long.groupby(['network_type'])['run'].rank('dense').astype('int')
    
    return df_long


def get_defacto_assortativity(wealths, observed_wealths):
    """Actual assortativity: Pearson correlation between own and neighbors' mean wealth
    Gets string of listed wealths and string of listed neighbors' wealths.
    Returns an objects Pearson correlation coefficient.
    """
    w = get_floats_from_str(wealths)
    obs_mean_w = get_floats_from_str(observed_wealths)
    return pearsonr(w, obs_mean_w).statistic


def get_vote_variance(votes):
    """Vote polarization: variance (measures spread)
    See (DiMaggio et al. 1996)
    Gets string of listed votes.
    Returns variance.
    """
    v = get_ints_from_str(votes)
    return np.var(v)

def get_vote_mad(votes):
    """Vote polarization: mean absolute deviation (measures spread)
    Gets string of listed votes.
    Returns mean absolute deviation.
    """
    v = get_ints_from_str(votes)
    return mad(v)


def get_vote_kurtosis(votes):
    """Vote polarization: kurtosis (measures bimodality, negative means flatter, approaching -2 is bimodal)
    See (DiMaggio et al. 1996)
    Gets string of listed votes.
    Returns kurtosis.
    """
    v = get_ints_from_str(votes)
    return kurtosis(v)


def get_new_gini_estimate(wealths):
    return gini_popadj(get_floats_from_str(wealths))

def get_stats_per_period(df):
    periods = list(sorted(df['period'].unique()))
    for i in periods:
        pass

def get_floats_from_str(datum):
    return [float(i) for i in datum.rstrip(']').lstrip('[').split()]

def get_ints_from_str(datum):
    return [int(i) for i in datum.rstrip(']').lstrip('[').split()]

def get_logints1_from_str(datum):
    return [np.log10(int(i) + 1) for i in datum.rstrip(']').lstrip('[').split()]

def get_strs_from_str(datum):
    return [RECODE_STATUSES[i] for i in datum.rstrip(']').lstrip('[').split()]