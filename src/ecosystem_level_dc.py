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
from statannot import add_stat_annotation

result_dir = './congruence-results'

def get_data(type_name, contri_type):
    
    dep, add, remove, upgrade, downgrade = [], [], [], [], []
    start = ['2014-04-01','2014-07-01', '2014-10-01','2015-01-01', '2015-04-01','2015-07-01', '2015-10-01', '2016-01-01', '2016-04-01','2016-07-01', '2016-10-01', '2017-01-01', '2017-04-01','2017-07-01', '2017-10-01',  '2018-01-01', '2018-04-01','2018-07-01', '2018-10-01','2019-01-01', '2019-04-01','2019-07-01', '2019-10-01', '2020-01-01', '2020-04-01','2020-07-01']
    end = [ '2014-06-30', '2014-09-30', '2014-12-31', '2015-03-31', '2015-06-30', '2015-09-30', '2015-12-31','2016-03-31', '2016-06-30', '2016-09-30', '2016-12-31', '2017-03-31', '2017-06-30', '2017-09-30', '2017-12-31', '2018-03-31', '2018-06-30', '2018-09-30', '2018-12-31', '2019-03-31', '2019-06-30', '2019-09-30', '2019-12-31', '2020-03-31', '2020-06-30', '2020-09-30']
    
    for ins, item in enumerate(start):
        m3_periods_start = [item] * 20
        m3_periods_end = [end[ins]] * 20
        dep_matrix_names = ['dependency', 'add','remove', 'upgrade', 'downgrade','dependency', 'add','remove', 'upgrade', 'downgrade','dependency', 'add','remove', 'upgrade', 'downgrade','dependency', 'add','remove', 'upgrade', 'downgrade']
        con_matrix_names = ['contributor','contributor', 'contributor','contributor', 'contributor', 'maintainer','maintainer','maintainer','maintainer','maintainer','dependent','dependent','dependent','dependent','dependent', 'lib_maintainer','lib_maintainer','lib_maintainer','lib_maintainer','lib_maintainer']
        
        for i, item in enumerate(m3_periods_start):
            zero_cong = 0
            all_cong = 0
            if con_matrix_names[i] == contri_type:
                
                name = str(dep_matrix_names[i]) + '-' + str(con_matrix_names[i]) + '-' + type_name +'-Congruence:' + str(m3_periods_start[i]) + '-' + str(m3_periods_end[i]) + '.json' 
                f = open('./congruence-results/' + name, "r")
                data = json.loads(f.read())
                
                if dep_matrix_names[i] == 'dependency':
                    dep.append(float(data['eco_congruence']))
                elif dep_matrix_names[i] == 'add':
                    add.append(float(data['eco_congruence']))
                elif dep_matrix_names[i] == 'remove':
                    remove.append(float(data['eco_congruence']))
                elif dep_matrix_names[i] == 'upgrade':
                    upgrade.append(float(data['eco_congruence']))
                elif dep_matrix_names[i] == 'downgrade':  
                    downgrade.append(float(data['eco_congruence']))
 
                f.close()
                
    return dep, add, remove, upgrade, downgrade

def box_plotly(df):
    ax = sns.boxplot(data=df, x='Type', y='Score',palette="Set2")
    fig = px.box(df, x= "Type", y="Score", color="Type")
    fig.update_layout(showlegend=False,
    xaxis_title="Contribution Types",
    yaxis_title="DC Congruence <br> (logarithmic scale)",
    font=dict(
        size=16
    ))
    fig.update_xaxes(title_font=dict(size=16),tickfont=dict(size=16))
    fig.update_yaxes(type="log",title_font=dict(size=16),tickfont=dict(size=16))


    return fig

def facet_row_column(df, select_role):
    df = df[(df['Role'] == select_role) & (df['Contribution'] == 'Issue')]
    #facet_col="Role", facet_row="Contribution",
    fig = px.line(df, x="Year", y="DC Congruence", color="Dependency_change", color_discrete_sequence= px.colors.qualitative.Set2 )
    fig.update_layout(legend_title_text='',
    legend=dict(
    yanchor="top",
    y=1.18,
    xanchor="right",
    x=0.70,
    orientation="h",
    font=dict(
    size=16
    )
    ))
    fig.update_xaxes(ticks="inside", title= '', title_font=dict(size=16),tickfont=dict(size=16),
    tickangle = 0)
    fig.update_yaxes(ticks="inside",title_font=dict(size=16),tickfont=dict(size=16))

    fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=15,
                     label="1quarter",
                     step="month",
                     stepmode="backward"),
                dict(count=30,
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

def arranage_distribution(nonmaintain, maintain, client, library):
    type_list, value_list= [], []

    value_list = value_list + nonmaintain
    type_list = type_list + ['s-s'] * len(nonmaintain)
    value_list = value_list + maintain
    type_list = type_list + ['c-c'] * len(maintain)
    value_list = value_list + client 
    type_list = type_list + ['c-s'] * len(client)
    value_list = value_list + library
    type_list = type_list + ['s-c'] * len(library)


    dicts = {'Type': type_list,'Score': value_list}
    df = pd.DataFrame(dicts, columns = ['Type', 'Score'])

    df.to_csv('{}/ecosystem-level-dist.csv'.format(result_dir), index=False)

def get_eco_level_plot():

    dep, add, remove, upgrade, downgrade = get_data('issue', 'contributor')
    pr_dep, pr_add, pr_remove, pr_upgrade, pr_downgrade = get_data('pr', 'contributor')

    typ = ['contributor', 'maintainer', 'dependent', 'lib_maintainer']
    typ_new = ['s-s', 'c-c', 'c-s', 's-c']
    issue_data = []
    pr_data = []
    date_list = []
    value_list = []
    contri_list = []
    dep_list = []
    pr_list = []

    non_maintain = []
    dep_maintain = []
    client_maintain = []
    library_maintain = []

    print('loading ecosystem-level data')
    for j, item in tqdm(enumerate(typ)):
        dep, add, remove, upgrade, downgrade = get_data('issue', typ[j])
        pr_dep, pr_add, pr_remove, pr_upgrade, pr_downgrade = get_data('pr', typ[j])
        issue_data.append([add, remove, upgrade, downgrade])
        pr_data.append([pr_add, pr_remove, pr_upgrade, pr_downgrade])
        date_list = date_list + [ '2014-06-30', '2014-09-30', '2014-12-31', '2015-03-31', '2015-06-30', '2015-09-30', '2015-12-31','2016-03-31', '2016-06-30', '2016-09-30', '2016-12-31', '2017-03-31', '2017-06-30', '2017-09-30', '2017-12-31', '2018-03-31', '2018-06-30', '2018-09-30', '2018-12-31', '2019-03-31', '2019-06-30', '2019-09-30', '2019-12-31', '2020-03-31', '2020-06-30', '2020-09-30'] * 8
        contri_list = contri_list + [typ_new[j]] * 208
        value_list = value_list + add + remove + upgrade + downgrade 
        dep_list = dep_list + (['added'] * len(add)) + (['removed'] * len(remove))+ (['upgraded'] * len(upgrade))+ (['downgraded'] * len(downgrade))
        pr_list = pr_list + ['Issue'] * 104

        value_list = value_list + pr_add + pr_remove + pr_upgrade + pr_downgrade 
        dep_list = dep_list + (['added'] * len(pr_add)) + (['removed'] * len(pr_remove))+ (['upgraded'] * len(pr_upgrade))+ (['downgraded'] * len(pr_downgrade))
        pr_list = pr_list + ['PR'] * 104

        if item == 'contributor':
            non_maintain = non_maintain + add + remove + upgrade +  downgrade
            non_maintain = non_maintain + pr_add + pr_remove + pr_upgrade + pr_downgrade

        elif item ==  'maintainer':
            dep_maintain = dep_maintain + add + remove + upgrade +  downgrade
            dep_maintain = dep_maintain + pr_add + pr_remove + pr_upgrade + pr_downgrade
        elif item == 'dependent':
            client_maintain = client_maintain + add + remove + upgrade +  downgrade
            client_maintain = client_maintain + pr_add + pr_remove + pr_upgrade + pr_downgrade
        elif item == 'lib_maintainer':
            library_maintain = library_maintain + add + remove + upgrade +  downgrade
            library_maintain = library_maintain + pr_add + pr_remove + pr_upgrade + pr_downgrade

    dicts = {'Year': date_list,'DC Congruence': value_list, 'Role': contri_list, 'Dependency_change': dep_list, 'Contribution': pr_list}
    df = pd.DataFrame(dicts, columns = ['Year', 'DC Congruence','Role', 'Dependency_change','Contribution'])
    df.to_csv('{}/ecosystem-level-facet.csv'.format(result_dir), index=False)

    arranage_distribution(non_maintain, dep_maintain, client_maintain, library_maintain)

