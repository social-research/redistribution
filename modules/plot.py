"""
Created on Jun 1 2023
@author: milenavt
Purpose: Helping functions for plotting
"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from ineq import *
import string
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.gridspec import GridSpec

piyg = sns.color_palette("PiYG", 5)
rdbu = sns.color_palette("RdBu", 5)
HUE_ORDER = ['repr', 'segr', 'homo', 'hete', 'rich', 'poor']
NET_LABELS = ['repr', 'segr', 'homo', 'hete', 'richvis', 'poorvis']
OFFSET = {'repr': -0.05, 'segr': -0.03, 'homo': -0.01, 'hete': 0.01, 'rich': 0.03, 'poor': 0.05}
LEGENDS = {'gender': {'M': 'male', 'F': 'female'},
           'p_sex': {'Male': 'male', 'Female': 'female'},
           'status': {'P': 'poor', 'R': 'rich'}}
CUSTOM_PALETTES = {'gender': ['turquoise', 'coral'],
                   'p_sex': ['turquoise', 'coral'],
                   'status': ['lightgrey', 'darkgrey'],
                   'network_type': [piyg[2], rdbu[4], rdbu[3], rdbu[1], piyg[4], piyg[0]],
                   'black': ['k', rdbu[4], rdbu[3], rdbu[1], piyg[4], piyg[0]],
                   'rationale_code':['tab:red', 'tab:olive', 'tab:green',
                                    'tab:pink', 'tab:purple','tab:brown', 
                                     'tab:gray','tab:gray'],
                    'group_feel_code': ['tab:blue', 'tab:cyan', 'tab:green',
                                        'tab:olive', 
                                        'tab:orange','tab:red', 'tab:purple', 
                                        'tab:gray']}
LABELS = {'network_type': 'Network type', 'rationale_code': 'Strategy', 
          'median_vote': 'Voted tax rate', 'vote_mad': 'Vote polarization',
          'vote_kurt': 'Kurtosis of vote distribution', 
          'score_gini': 'Gini coefficient', 'gini': 'Gini coefficient', 
          'observed_gini': 'Observed Gini', 'observed_subj_ineq': 'Perceived subjective inequality',
          'group_feel_code': 'Feelings about group',
          'gender': 'Gender', 'proportion': 'Proportion', 'proportion_poor': 'Proportion of poor', 'proportion_rich': 'Proportion of rich',
          'observed_mean_wealth': 'Observed mean wealth',
          'award_satisfied': 'Satisfied with initial score', 'result_satisfied': 'Satisfied with final score',
          'award_dist_fair': 'Initial scores were fair', 'result_dist_fair': 'Final scores were fair',
          'num_observers': 'Indegree'}

def init_plot():
    #sns.set_style('ticks')
    mpl.rcParams['font.size'] = 6
    mpl.rcParams['xtick.labelsize'] = 6
    mpl.rcParams['ytick.labelsize'] = 6
    mpl.rcParams['legend.fontsize'] = 6
    mpl.rcParams['axes.titlesize'] = 7
    mpl.rcParams['axes.linewidth'] = 0.2
    mpl.rcParams['xtick.major.size'] = 2
    mpl.rcParams['ytick.major.width'] = 0.2
    mpl.rcParams['ytick.major.size'] = 2
    mpl.rcParams['xtick.major.width'] = 0.2
    mpl.rcParams['xtick.major.pad']='2'
    mpl.rcParams['ytick.major.pad']='2'
    mpl.rcParams['xtick.minor.size'] = 2
    mpl.rcParams['ytick.minor.width'] = 0.2
    mpl.rcParams['ytick.minor.size'] = 2
    mpl.rcParams['xtick.minor.width'] = 0.2
    mpl.rcParams['lines.linewidth'] = 0.5
    mpl.rcParams['patch.linewidth'] = 0.2
    #mpl.rcParams['lines.markersize'] = 3
    #mpl.rcParams['font.family'] = 'sans-serif'
    mpl.rcParams['font.sans-serif'] = ['Arial']
    mpl.rcParams["savefig.dpi"] = 400


def plot_assortativity(data, save=None):
    sns.violinplot(x='h', y='assortativity',
            hue='v', palette=sns.color_palette("PiYG", 5),
            data=data, linewidth=0.5)
    plt.title('Assortativity by wealth')
    plt.ylabel('Correlation of own and mean observed wealth')
    plt.xlabel(r'Homophily $h$')
    plt.legend(title=r'Visibility $v$')
    if save != None:
        plt.savefig(save, format=save[-3:], bbox_inches='tight')
    plt.show()
    plt.close() # clear
    
def plot_assortativity_exp(data, save=None):
    sns.violinplot(x='network_type', y='assortativity',
            palette=sns.color_palette("PiYG", 5),
            data=data, linewidth=0.5)
    plt.title('Assortativity by wealth')
    plt.ylabel('Correlation of own and mean observed wealth')
    plt.xlabel(r'Homophily $h$')
    plt.legend(title=r'Visibility $v$')
    if save != None:
        plt.savefig(save, format=save[-3:], bbox_inches='tight')
    plt.show()
    plt.close() # clear


def _y_hv(ax, data, y, title, ylim, baseline=None, legend=True):
    """Plot all data and mean for h on x-axis and v as hue."""
    # Create the stripplot on the specified axes
    sns.stripplot(x='h', y=y, hue='v', palette=sns.color_palette("PiYG", 5),
                data=data, alpha=0.4, jitter=0.1, dodge=True, 
                edgecolor="gray", size=3, linewidth=0.2, ax=ax, zorder=1, legend=False) 
    
    # The "mean" markers
    sns.pointplot(x='h', y=y, hue='v', palette=sns.color_palette("PiYG", 5),
              data=data, linestyle='none', dodge=.98 - .98 / 3, 
              markers="d", markeredgecolor='k', markeredgewidth=0.5,
              markersize=5, errorbar=None, ax=ax, zorder=2)
        
    if baseline != None:
        ax.axhline(y=baseline, color='k', lw=0.5, ls='--', dashes=(10, 5))

    ax.set(ylim=ylim, title=title, ylabel=LABELS[y], xlabel=r'Homophily $h$') 

    if legend:
        h, l = ax.get_legend_handles_labels()
        # Show legend only for mean markers and make sure legend is on top of them
        ax.legend(h[:5], l[:5], title=r'Visibility $v$', ncol=3).set_zorder(101) 
    else:
        ax.get_legend().remove()



def plot_y_hv(data, y, title, ylim, baseline=None, save=None):
    """Plot all data and mean for h on x-axis and v as hue."""
    fig, ax = plt.subplots(figsize=(5, 3))
    _y_hv(ax, data, y, title, ylim, baseline)

    if save != None:
        plt.savefig(save, format=save[-3:], bbox_inches='tight')
    plt.show()
    plt.close()


def plot2_y_hv(data1, y1, title1, ylim1, 
               data2, y2, title2, ylim2, 
               baseline1=None, baseline2=None, 
               subfig_letter=False, save=None):
    """Plot figure with left and right subplot.
    Each subplot is all data and mean for h on x-axis and v as hue.
    """
    fig = plt.figure(layout="tight", figsize=(5.1, 1.4))
    gs = GridSpec(1, 2, figure=fig, wspace=0.27)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    _y_hv(ax1, data1, y1, title1, ylim1, baseline1)
    _y_hv(ax2, data2, y2, title2, ylim2, baseline2, legend=False)

    if subfig_letter:
        ax1.text(-0.2, 1.05, 'B', transform=ax1.transAxes, size=9)

    if save != None:
        plt.savefig(save, format=save[-3:], bbox_inches='tight')
    plt.show()
    plt.close()
    

def _y_net_line(ax, data, y, title, ylim, errorbar, legend=False):
    """Helping lineplot function for experiment data."""
    data = data.copy()
    for i in OFFSET:
        data.loc[data['network_type'] == i, 'round'] += OFFSET[i]
    sns.lineplot(x='round', hue='network_type', y=y,
                 palette=sns.color_palette(CUSTOM_PALETTES['black']),
                 linewidth = 0.75,
                 #estimator='median', # Looks messy with median so will use default mean
                 data=data, ax=ax, errorbar=errorbar, err_style="bars",
                 err_kws={'capsize': 2, 'elinewidth': 0.4, 'capthick': 0.4})
    ax.set(ylim=ylim, title=title, ylabel=LABELS[y], xlabel=None, 
           xticks=[1, 2, 3], xticklabels=['round 1', 'round 2', 'round 3']) 
    if legend:
        # Remove legend title
        ax.get_legend().set_title(None)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, NET_LABELS, ncol=2)
    else:
        ax.get_legend().remove()


def _y_net_box(ax, data, y, title, ylim, baseline=None):
    """Helping boxplot function for experiment data."""
    # This should come first in order to modify line color only for the "mean" markers
    sns.boxplot(x='network_type', y=y, hue='network_type', 
                palette=sns.color_palette(CUSTOM_PALETTES['network_type']),
                data=data, linewidth=0.5, showfliers=False, ax=ax, legend=False)

    # Truncate the 'network' labels to first 5 characters
    #ax.set_xticklabels(data['network_type'].cat.categories)
    
    plt.setp(ax.lines, zorder=100)
    plt.setp(ax.collections, zorder=100, label="")

    # Make sure boxes have black outlines
    for i in ax.artists:
        i.set_edgecolor('black')

    # Create the stripplot on the same axes (optional, to show individual data points)
    if data[y].size < 6*20:
        msize = 1.2
    else:
        msize = 0.5
    sns.stripplot(x='network_type', y=y, hue='network_type',
                  palette=6*['k'],
                  data=data, alpha=1, jitter=True, 
                  edgecolor="k", size=msize, linewidth=0.1, ax=ax)
    #ax.get_legend().remove()
    
    if baseline != None:
        ax.axline((0, baseline), slope=0, c='k', lw=0.5, ls='--', dashes=(10, 5))

    ax.set(ylim=ylim, title=title, ylabel=LABELS[y], xlabel=None, xticklabels=NET_LABELS) #xlabel=LABELS['network_type']) 


def _y_hue_net_box(ax, data, y, hue, title, ylim, legend=False, baseline=None):
    """Helping boxplot with hue function for experiment data."""
    
    # This should come first in order to modify line color only for the "mean" markers
    sns.boxplot(x='network_type', y=y, hue=hue, 
                palette=sns.color_palette(CUSTOM_PALETTES[hue]), 
                linewidth=0.35, medianprops={"linewidth": 0.75},
                gap=.1, data=data, dodge=True, showfliers=False, ax=ax)

    # Truncate the 'network' labels to first 5 characters
    #ax.set_xticklabels(data['network_type'].cat.categories)
    # Format legend
    if legend:
        ax.get_legend().set_title(None)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[:2], [LEGENDS[hue][i] for i in labels[:2]])
    else:
        ax.get_legend().remove()
      
    ax.set(ylim=ylim, title=title, ylabel='Vote in round 1', 
           xlabel=None, xticklabels=NET_LABELS) #xlabel=LABELS['network_type']) 

def y_gender_net_box(ax, data, y, title, ylabel, ylim, baseline=None):
    """Helping boxplot with hue function for experiment data."""
    # This should come first in order to modify line color only for the "mean" markers
    sns.boxplot(x='network_type', y=y, hue="p_sex", 
                palette=sns.color_palette(CUSTOM_PALETTES['gender']),
                data=data, dodge=True, showfliers=False, ax=ax)

    # Truncate the 'network' labels to first 5 characters
    ax.set_xticklabels(data['network_type'].cat.categories)
    # Format legend
    ax.get_legend().set_title(None)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[:2], [LEGENDS['gender'][i] for i in labels[:2]])
      
    if baseline != None:
        ax.axline((0, baseline), slope=0, c='k', lw=0.5, ls='--', dashes=(10, 5))
    ax.set(ylim=ylim, title=title, ylabel=ylabel, xlabel=None) #xlabel=LABELS['network_type']) 


def plot_y_net_box(data, y, title, ylabel, ylim, baseline=None, save=None):
    """Plot figure with a boxplot for network_type.
    """
    fig, ax = plt.subplots(figsize=(4.5, 2))
    y_net_box(ax, data, y, title, ylabel, ylim, baseline)

    if save != None:
        plt.savefig(save, format=save[-3:], bbox_inches='tight')
    plt.show()
    plt.close()


def plot2_y_net_box(data1, y1, title1, ylim1, 
                    data2, y2, title2, ylim2, 
                    baseline1=None, baseline2=None, 
                    subfig_letter=False, save=None):
    """Plot figure with left and right subplot. 
    Each subplot is a boxplot for network_type.
    """
    fig, axes = plt.subplots(1,2, figsize=(5, 1.75))
    _y_net_box(axes[0], data1, y1, title1, ylim1, baseline1)
    _y_net_box(axes[1], data2, y2, title2, ylim2, baseline2)

    if subfig_letter:
        _subfig_letter(axes)
    fig.tight_layout(w_pad=3)

    if save != None:
        plt.savefig(save, format=save[-3:], bbox_inches='tight')
    plt.show()
    plt.close()

def plot1_y_hue_net_box(data, y, hue, title, ylim, 
                       baseline=None, save=None):
    """Plot figure with a boxplot for network_type.
    """
    fig, ax = plt.subplots(1,1, figsize=(4.5, 2.25))
    _y_hue_net_box(ax, data, y, hue, title, ylim, legend=True, baseline=None)
    if save != None:
        plt.savefig(save, format=save[-3:], bbox_inches='tight')
    plt.show()
    plt.close()


def plot2_y_hue_net_box(data1, y1, hue1, title1, ylim1, 
                        data2, y2, hue2, title2, ylim2, 
                        baseline1=None, baseline2=None,
                        subfig_letter=False, save=None):
    """Plot figure with a boxplot for network_type.
    """
    fig, axes = plt.subplots(1,2, figsize=(5, 1.75))
    _y_hue_net_box(axes[0], data1, y1, hue1, title1, ylim1, legend=False, baseline=baseline1)
    _y_hue_net_box(axes[1], data2, y2, hue2, title2, ylim2, legend=True, baseline=baseline2)

    if subfig_letter:
        _subfig_letter(axes)
    fig.tight_layout(w_pad=3)

    if save != None:
        plt.savefig(save, format=save[-3:], bbox_inches='tight')
    plt.show()
    plt.close()


def plot_lowess_fits(data, x, y, ylim, xlabel, ylabel, 
                     baseline=None, subfig_letter=False, save=None):
    """Fit Lowess line for y vs. x for each run, 
    with a separate plot for each hv combination."""
    p = sns.lmplot(data=data, x=x, y=y, 
            col='h', row='v', height=0.78, aspect=1.1,
            row_order=[1, 0.5, 0, -0.5, -1], col_order=[-1, -0.5, 0, 0.5, 1], 
            scatter=False, lowess=True, legend=False,
            hue='run', line_kws={'linewidth': 0.75, 'color': 'gray', "alpha": 0.2}
    )
    for ax in p.axes.flat:
        newtitle = ax.get_title().replace('h', '$h$').replace('v', '$v$')
        ax.set_title(r'%s' % newtitle, fontsize=6)

    if baseline != None:
        for ax in p.axes.flat:
            ax.axline((0, baseline), slope=0, c='k', lw=0.5, ls='--', dashes=(10, 5))

    p.set(ylim=ylim)
    p.set_axis_labels(x_var=xlabel, y_var=ylabel)

    plt.annotate('Heterophily', xytext=(0.124, 0.015), xy=(0.52, 0.015), xycoords='figure fraction', 
                 fontsize=8, horizontalalignment='left', verticalalignment='center', 
                 arrowprops=dict(arrowstyle="<-", lw=0.75))
    plt.annotate('Homophily', xytext=(1, 0.015), xy=(0.5, 0.015), xycoords='figure fraction', 
                 fontsize=8, horizontalalignment='right', verticalalignment='center', 
                 arrowprops=dict(arrowstyle="<-", lw=0.75))
    plt.annotate('Poor visible', xytext=(0.017, 0.114), xy=(0.017, 0.52), xycoords='figure fraction', 
                 fontsize=8, horizontalalignment='center', verticalalignment='bottom', rotation=90, 
                 arrowprops=dict(arrowstyle="<-", lw=0.75))
    plt.annotate('Rich visible', xytext=(0.017, 0.964), xy=(0.017, 0.5), xycoords='figure fraction', 
                 fontsize=8, horizontalalignment='center', verticalalignment='top', rotation=90, 
                 arrowprops=dict(arrowstyle="<-", lw=0.75))
    if subfig_letter:
        #plt.annotate('A', xytext=(0.02, 1.01), xy=(0.02, 1.05), xycoords='figure fraction',
        #             horizontalalignment='left', verticalalignment='bottom', fontsize=9)
        plt.text(0, 1, 'A', transform=plt.gcf().transFigure, size=9)

    if save != None:
        plt.savefig(save, format=save[-3:], bbox_inches='tight')
    
    plt.show()
    plt.close()


def clear_axis(ax, axtype):
    if axtype == 'x':
        ax.set_xticks([])
        ax.set_xticklabels([])
    else:
        ax.set_yticks([])
        ax.set_yticklabels([])


def plot2_dynamics(data1, y1, title1, ylim1, 
                    data2, y2, title2, ylim2, 
                    errorbar, subfig_letter=False, save=None):
    """Plot figure with left and right subplot. 
    Each subplot shows lines colored by network_type showing
    how y1 and y2 change per round.
    """
    fig, axes = plt.subplots(1,2, figsize=(5, 1.75))
    _y_net_line(axes[0], data1, y1, title1, ylim1, errorbar)
    _y_net_line(axes[1], data2, y2, title2, ylim2, errorbar, legend=True)

    if subfig_letter:
        _subfig_letter(axes)
    fig.tight_layout(w_pad=3)

    if save != None:
        plt.savefig(save, format=save[-3:], bbox_inches='tight')
    plt.show()
    plt.close()

def plot1_votes_by_status(data, save=None):
    fig, ax = plt.subplots(1, 1, figsize=(5, 2.25))
    _vote_status_violin(ax, data=data, ylabel='Vote', legend=True)
    ax.set(xlim=[-0.5, 6])
    fig.tight_layout()
    if save != None:
        plt.savefig(save, format=save[-3:], bbox_inches='tight')
    plt.show()
    plt.close()

def plot2_votes_by_status(data, subfig_letter=False, save=None):
    fig, axes = plt.subplots(1, 2, figsize=(4.5, 1.6))
    _vote_status_violin(axes[0], data=data[data['round']==1], 
                       ylabel='Vote in round 1', legend=True)
    _vote_status_violin(axes[1], data=data[data['round']==3], 
                       ylabel='Vote in round 3', legend=False)
    
    if subfig_letter:
        _subfig_letter(axes)
    fig.tight_layout(w_pad=2)

    if save != None:
        plt.savefig(save, format=save[-3:], bbox_inches='tight')
    plt.show()
    plt.close()

def _subfig_letter(axes):
    for n, ax in enumerate(axes.flat):
        ax.text(-0.15, 1.05, string.ascii_uppercase[n], transform=ax.transAxes, 
                size=9)

def _vote_status_violin(ax, data, ylabel, legend=False):
    """Helping violin plot with hue function for experiment data."""

    # Violin split plot
    sns.violinplot(data=data, x="network_type", y="vote", 
                   hue="status", linewidth=0.5,
                   palette=sns.color_palette(CUSTOM_PALETTES['status']),
                   cut=0, split=True, inner='quart', ax=ax)  #, inner=None if using pointplot
    # Pointplot of median with CI
    #sns.pointplot(data=data, x="network_type", y="vote", 
    #              hue="status", estimator='median', errwidth=0.5, 
    #               scale = 0.75, dodge=0.3, join=False, palette=['k'], ax=ax)
    
    # Vertical line of difference between medians
    x = data[['network_type', 'status', 'vote']].groupby(['network_type', 'status']).median().reset_index()
    for i, net in enumerate(x['network_type'].cat.categories):
        ax.vlines(i, x[(x['network_type']==net) & (x['status']=='R')].iloc[0]['vote'], 
                   x[(x['network_type']==net) & (x['status']=='P')].iloc[0]['vote'],
                   color='k', lw=2, zorder=100)
    
    if legend:
        ax.get_legend().set_title(None)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[:2], [LEGENDS['status'][i] for i in labels[:2]])
        # Replace labels
        # new_labels = ['poor', 'rich']
        # for t, l in zip(ax.legend_.texts, new_labels):
        #     t.set_text(l)
    else:
        ax.get_legend().remove()

    ax.set(ylim=[-5, 105], title=None, 
           xlabel=None, xticklabels=NET_LABELS) #xlabel=LABELS['network_type']) 
    ax.set_ylabel(ylabel=ylabel, labelpad=0)


def plot_turnout(df, var='turnout2_frac', title="Voter turnout in rounds 2 and 3", save=None):
    # Get rates per group per status
    turn_df = df[['network_type', 'status', 'group', 
                    var]].groupby(['network_type', 'status', 'group']).mean().reset_index()
    turn_df = turn_df.dropna()
    
    fig, ax = plt.subplots(figsize=(4.4, 2.5))
    sns.barplot(df, x='network_type', y=var, hue='status',
                palette=sns.color_palette(CUSTOM_PALETTES['status']),
                errorbar=('ci'), errwidth=0.4, capsize=0.1, ax=ax)
    # Legend
    ax.get_legend().set_title(None)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[:2], [LEGENDS['status'][i] for i in labels[:2]])
    # Layout
    ax.set(ylim=[0, 1.05], title=title, ylabel='Turnout', xlabel=None, xticklabels=NET_LABELS) #xlabel=LABELS['network_type'])
    fig.tight_layout()
    if save != None:
        plt.savefig(save, format=save[-3:], bbox_inches='tight')
    plt.show()
    plt.close()


def _bar_by_status(ax, data, y, title, ylim, legend=False):
    sns.barplot(data, x='network_type', y=y, hue='status',
                palette=sns.color_palette(CUSTOM_PALETTES['status']),
                errorbar=('ci'), errwidth=0.4, capsize=0.1, ax=ax)
    if legend:
        ax.get_legend().set_title(None)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[:2], [LEGENDS['status'][i] for i in labels[:2]])
    else:
        ax.legend().remove()
    ax.set(ylim=ylim, title=title, ylabel=LABELS[y], 
           xlabel=None, xticklabels=NET_LABELS) #xlabel=LABELS['network_type'])

def _bar_by_hue(ax, data, y, x, hue, title, ylim, 
                legend=False, legend_out=False, xrotate=False):
    sns.barplot(data, y=y, x=x, hue=hue,
                palette=sns.color_palette(CUSTOM_PALETTES[hue]),
                ax=ax)
    if legend:
        ax.get_legend().set_title(None)
        if legend_out:
             sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
        if hue in LEGENDS:
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles[:2], [LEGENDS[hue][i] for i in labels[:2]])
    else:
        ax.legend().remove()
    ax.set(ylim=ylim, title=title, ylabel=LABELS[y], xlabel=None)
    if xrotate:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    else:
        ax.set(xticklabels=NET_LABELS)

def _plot_treatments(ax):
    x = [i+j for j in range(0, 21, 4) for i in [0, 1, 2, 0, 2, 0, 1, 2]]
    yr = 6*[0, 0, 0, 1, 1, 2, 2, 2]
    yp = [3.5+i for i in yr]
    sp, sr = 10, 50
    s_53 = [sr, sr, sr, sp, sp, sp, sp, sp]
    colors = {sp: 'lightgrey', sr: 'darkgrey'}
    s_80 = [sp]*8
    s_08 = [sr]*8
    s_62 = [sp, sr, sr, sp, sp, sp, sp, sp]
    s_26 = [sr, sr, sr, sr, sr, sp, sp, sr]
    s_others = {'repr': {'P': s_53, 'R': s_53},
               'segr': {'P': s_80, 'R': s_08},
               'homo': {'P': s_62, 'R': s_26},
               'hete': {'P': s_26, 'R': s_62},
               'rich': {'P': s_26, 'R': s_26},
               'poor': {'P': s_62, 'R': s_62}}
    s_ego = {'P': [sp], 'R': [sr]}
    # Ego
    ax.scatter(range(1, 22, 4), 6*[1], c=colors[sr], linewidths=0.75, edgecolors='k', s=sr)
    ax.scatter(range(1, 22, 4), 6*[4.5], c=colors[sp], linewidths=0.75, edgecolors='k', s=sp)
    # Alters
    ax.scatter(x, yp, c=[colors[j] for i in ['repr', 'segr', 'homo', 
                                             'hete', 'rich', 'poor'] for j in s_others[i]['P']], 
               linewidths=0.25, edgecolors='k',
               s=[j for i in ['repr', 'segr', 'homo', 
                              'hete', 'rich', 'poor'] for j in s_others[i]['P']])
    ax.scatter(x, yr, c=[colors[j] for i in ['repr', 'segr', 'homo', 
                                             'hete', 'rich', 'poor'] for j in s_others[i]['R']], 
               linewidths=0.25, edgecolors='k',
               s=[j for i in ['repr', 'segr', 'homo', 
                              'hete', 'rich', 'poor'] for j in s_others[i]['R']])
    ax.set_ylim(-0.5, 6)
    ax.set_xlim(-5.5, 24)
    for side in ['top','right','bottom','left']:
        ax.spines[side].set_visible(False)
    ax.tick_params(axis='x', which='both', bottom=False)
    ax.tick_params(axis='y', which='both', left=False, labelleft=False)
    ax.set_xticks(range(1, 22, 4), NET_LABELS)
    ax.text(-5.5, 0.9, 'Participant rich', size=6, ha='left')
    ax.text(-5.5, 4.4, 'Participant poor', size=6, ha='left')
    

def plot2_bar_by_status(data1, y1, title1, ylim1, 
                        data2, y2, title2, ylim2,
                        subfig_letter=False, save=None):
    
    fig, axes = plt.subplots(1, 2, figsize=(5, 1.75))
    _bar_by_status(axes[0], data1, y1, title1, ylim1, legend=False)
    _bar_by_status(axes[1], data2, y2, title2, ylim2, legend=True)

    if subfig_letter:
        _subfig_letter(axes)
    fig.tight_layout(w_pad=3)

    if save != None:
        plt.savefig(save, format=save[-3:], bbox_inches='tight')
    plt.show()
    plt.close()

def plot2_bar(data1, y1, x1, hue1, title1, ylim1, legend1, x1rotate,
              data2, y2, x2, hue2, title2, ylim2, legend2, x2rotate, 
              legend_out=False, vertical=False,
              subfig_letter=False, save=None):
    
    if vertical:
        fig, axes = plt.subplots(2, 1, figsize=(5, 3.25))
    else:
        fig, axes = plt.subplots(1, 2, figsize=(5, 2))
    _bar_by_hue(axes[0], data1, y1, x1, hue1, title1, ylim1, legend1, legend_out, xrotate=x1rotate)
    _bar_by_hue(axes[1], data2, y2, x2, hue2, title2, ylim2, legend2, legend_out, xrotate=x2rotate)


    if subfig_letter:
        _subfig_letter(axes)
    fig.tight_layout(w_pad=3)

    if save != None:
        plt.savefig(save, format=save[-3:], bbox_inches='tight')
    plt.show()
    plt.close()


def plot_experiment(data, baseline1, baseline2, save=None):
    fig = plt.figure(layout="tight", figsize=(3.9, 2.2))
    gs = GridSpec(2, 2, figure=fig, wspace=0.27, hspace=0.4, 
                  left=0, right=1, top=1, bottom=0,
                  height_ratios=[1, 1.2])
    ax1 = fig.add_subplot(gs[0, :])
    ax2 = fig.add_subplot(gs[1, :-1])
    ax3 = fig.add_subplot(gs[1, -1])

    _plot_treatments(ax1)
    _y_net_box(ax2, data, y='median_vote', title=None, ylim=(0, 100), baseline=baseline1)
    _y_net_box(ax3, data, y='vote_mad', title=None, ylim=(0, 45), baseline=baseline2)

    ax1.text(-0.1, 1.05, 'A', transform=ax1.transAxes, size=9)
    ax2.text(-0.225, 1.05, 'B', transform=ax2.transAxes, size=9)

    #fig.tight_layout()
    if save != None:
        plt.savefig(save, format=save[-3:], bbox_inches='tight')
    plt.show()
    plt.close()


def plot_results(data12, data34, baseline1, baseline2, save=None):
    fig = plt.figure(layout="tight", figsize=(5, 3.3))
    gs = GridSpec(2, 2, figure=fig, wspace=0.27, hspace=0.4)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])

    _y_net_box(ax1, data12, y='median_vote', title=None, ylim=(0, 55), baseline=baseline1)
    _y_net_box(ax2, data12, y='vote_mad', title=None, ylim=(0, 35), baseline=baseline2)
    _y_net_line(ax3, data34, y='median_vote', title=None, ylim=(0, 55), errorbar='ci')
    _y_net_line(ax4, data34, y='vote_mad', title=None, ylim=(0, 35), errorbar='ci', legend=True)


    ax1.text(-0.225, 1.05, 'A', transform=ax1.transAxes, size=9)
    ax3.text(-0.225, 1.05, 'B', transform=ax3.transAxes, size=9)

    #fig.tight_layout()
    if save != None:
        plt.savefig(save, format=save[-3:], bbox_inches='tight')
    plt.show()
    plt.close()


def plot_polarization(data12, data34, save=None):
    fig = plt.figure(layout="tight", figsize=(5, 3.3))
    gs = GridSpec(2, 2, figure=fig, wspace=0.27, hspace=0.4)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])

    _vote_status_violin(ax1, data=data12[data12['round']==1], ylabel='Vote in round 1', legend=False)
    _vote_status_violin(ax2, data=data12[data12['round']==3], ylabel='Vote in round 3', legend=False)
    _bar_by_status(ax3, data34, y='result_satisfied', title=None, ylim=[-1.1, 1.6], legend=False)
    _bar_by_status(ax4, data34, y='result_dist_fair', title=None, ylim=[-1.1, 1.6], legend=True)


    ax1.text(-0.225, 1.05, 'A', transform=ax1.transAxes, size=9)
    ax3.text(-0.225, 1.05, 'B', transform=ax3.transAxes, size=9)

    #fig.tight_layout()
    if save != None:
        plt.savefig(save, format=save[-3:], bbox_inches='tight')
    plt.show()
    plt.close()
