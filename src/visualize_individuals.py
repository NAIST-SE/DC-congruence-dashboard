import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import plotly.express as px
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
import csv


def rearrange_data(repo, df, type_name, old_column):
    proj_df = df[df['Repo_name'] == repo]
    proj_df['Type'] = type_name
    proj_df['Value'] = proj_df[old_column]
    proj_df = proj_df.drop(old_column, axis=1)
    return proj_df

def filter_cong(df ,repo, role):
    proj_df = df[df['Repo_name'] == repo]
    condi1 = proj_df['Type'] == 'added:' + str(role)
    condi2 = proj_df['Type'] == 'removed:' + str(role)
    condi3 = proj_df['Type'] == 'upgraded:' + str(role)
    condi4 = proj_df['Type'] == 'downgraded:' + str(role)
    new_df = proj_df[(condi1) | (condi2) | (condi3) | (condi4)]
    new_df = new_df.sort_values(by='Interval_start', ascending=True)
    new_df['Type'] = new_df['Type'].str.replace(':'+ str(role), '')
    return new_df

def line_plotly(df, colors, ytitle, x_loc):
    fig = px.line(df, x="Interval_end", y="Value",color="Type",  color_discrete_sequence= colors)
    fig.update_layout(
        legend_title_text='',
    legend=dict(
    yanchor="top",
    y=1.28,
    xanchor="right",
    x=x_loc,
    orientation="h",
    font=dict(
    size=16
    )
    ))
    fig.update_xaxes(ticks="inside", title= '', title_font=dict(size=16),tickfont=dict(size=16),
    tickangle = 0)
    fig.update_yaxes(title= ytitle, ticks="inside",title_font=dict(size=16),tickfont=dict(size=16))

    fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=12,
                     label="1quarter",
                     step="month",
                     stepmode="backward"),
                dict(count=24,
                     label="1year",
                     step="month",
                     stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True,
            bgcolor =  'grey'
        ),
        type="date"
    )
)

    return fig

def plot_gauge(df, repo):
    repo = repo.replace('/', ':')
    df = df[(df['Repo_name'] == repo) & (df['Interval_end'] == '2020-09-30')]
    star = df['Star'].tolist()
    watcher = df['Watcher'].tolist()
    fork = df['Fork'].tolist()
    
    fig1 = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = star[0],
    domain = {'x': [0, 1], 'y': [0, 1]},
    number={'font.size': 60},
    title = {'text': 'Star', 'font': {'size': 40}},
    gauge = {
        'bgcolor': "grey",
        'axis': {'tickwidth': 5},
        'bar': {'color': "#50C878"}}))

    fig2 = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = watcher[0],
    number={'font.size': 60},
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': 'Watcher', 'font': {'size': 40}},
    gauge = {
        'bgcolor': "grey",
        'axis': {'tickwidth': 5},
        'bar': {'color': "#FFA600"}}))
    

    fig3 = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = fork[0],
    number={'font.size': 60},
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': 'Fork', 'font': {'size': 40}},
    gauge = {
        'bgcolor': "grey",
        'axis': {'tickwidth': 5},
        'bar': {'color': "#E55451"}}))

    return fig1, fig2, fig3



def plot_individuals(repo, role, df_commit, df_cong, df_contri, df_dep, df_issue, df_pull):
    repo = repo.replace('/', ':')
    df_commit = rearrange_data(repo, df_commit, '#commits', 'Num_commits')
    df_contri = rearrange_data(repo, df_contri, '#contributors', 'Contributors')
    df_dep = rearrange_data(repo, df_dep, '#dependencies', 'Num_dependencies')
    df_issue = rearrange_data(repo, df_issue, '#issues', 'Num_issues')
    df_pull = rearrange_data(repo, df_pull, '#PRs', 'Num_prs')

    df_cong = filter_cong(df_cong, repo, role)

    frames= [df_commit, df_contri, df_dep, df_issue, df_pull]  
    combined_df = pd.concat(frames, ignore_index=True)
    return line_plotly(combined_df,px.colors.qualitative.T10, '# Occurrences', 0.98), line_plotly(df_cong,px.colors.qualitative.Antique, 'DC Congruence', 0.9)


