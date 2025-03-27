import pandas as pd
from scipy.stats import mannwhitneyu
from itertools import combinations


def pairwise_test(df, var):
    cats = df['network_type'].cat.categories
    res = pd.DataFrame('', index=cats[:-1], columns=cats[1:])
    for i, j in combinations(cats, 2):
        stat, p = mannwhitneyu( df[df['network_type']==i][var], df[df['network_type']==j][var] )
        res.loc[i, j] = '{0:.3f}'.format(p) + stars(p)
    return res

def stars(p):
    if p < 0.001:
        return '***'
    elif p < 0.01:
        return '**'
    elif p < 0.05:
        return '*'
    elif p < 0.1:
        return '+'
    else:
        return ''