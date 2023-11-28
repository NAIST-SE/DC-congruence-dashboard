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
sns.set_style('white')
result_dir = './congruence-results'

def get_data(type_name, contri_type):
    
    start = ['2014-04-01','2014-07-01', '2014-10-01','2015-01-01', '2015-04-01','2015-07-01', '2015-10-01', '2016-01-01', '2016-04-01','2016-07-01', '2016-10-01', '2017-01-01', '2017-04-01','2017-07-01', '2017-10-01',  '2018-01-01', '2018-04-01','2018-07-01', '2018-10-01','2019-01-01', '2019-04-01','2019-07-01', '2019-10-01', '2020-01-01', '2020-04-01','2020-07-01']
    end = [ '2014-06-30', '2014-09-30', '2014-12-31', '2015-03-31', '2015-06-30', '2015-09-30', '2015-12-31','2016-03-31', '2016-06-30', '2016-09-30', '2016-12-31', '2017-03-31', '2017-06-30', '2017-09-30', '2017-12-31', '2018-03-31', '2018-06-30', '2018-09-30', '2018-12-31', '2019-03-31', '2019-06-30', '2019-09-30', '2019-12-31', '2020-03-31', '2020-06-30', '2020-09-30']
    mean_values = []
    median_values = []
    #for each period
    all_values = []

    for ins, item in enumerate(start):
        m3_periods_start = [item] * 4
        m3_periods_end = [end[ins]] * 4
        dep_matrix_names = ['add','remove', 'upgrade', 'downgrade']
        con_matrix_names = [contri_type] * 4
        pkg_dc_value = []

        #for each dependency type
        for i, item in enumerate(m3_periods_start):
            zero_cong = 0
            all_cong = 0

            name = str(dep_matrix_names[i]) + '-' + str(con_matrix_names[i]) + '-' + type_name +'-Congruence:' + str(m3_periods_start[i]) + '-' + str(m3_periods_end[i]) + '.json' 
            f = open('./congruence-results/' + name, "r")
            data = json.loads(f.read())
                
            for pkg_name in data:
                if pkg_name != 'eco_congruence' and data[pkg_name] != 0:
                    pkg_dc_value.append(data[pkg_name])
                    all_values.append(data[pkg_name])

            f.close()

        mean_values.append(np.mean(pkg_dc_value))
        median_values.append(np.median(pkg_dc_value))


    return all_values

def violin_box_plot(nonmaintain, maintain, client, library):
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
    order = ['s-s', 'c-c', 'c-s', 's-c']
    palette = 'Set2'
    plt.figure(figsize=(3, 3))
    ax = sns.violinplot(x="Type", y="Score", data=df, hue="Type", dodge=False,
                    palette=palette,
                    scale="width", inner=None)

    for violin in ax.collections:
        bbox = violin.get_paths()[0].get_extents()
        x0, y0, width, height = bbox.bounds
        violin.set_clip_path(plt.Rectangle((x0, y0), width / 2, height, transform=ax.transData))

    sns.boxplot(x="Type", y="Score", data=df, saturation=1, showfliers=False,
            width=0.3, boxprops={'zorder': 3, 'facecolor': 'none'}, ax=ax)
    old_len_collections = len(ax.collections)
    sns.stripplot(x="Type", y="Score", data=df, hue="Type", palette=palette, dodge=False, ax=ax)
    for dots in ax.collections[old_len_collections:]:
        dots.set_offsets(dots.get_offsets() + np.array([0.3, 0]))
    ax.legend_.remove()
    #ax.set(yscale="log")
    
    ax.set_xlabel('Contribution Types',fontsize=18)
    ax.set_ylabel('Library-level DC Congruence',fontsize=18)
    ax.tick_params(labelsize=16)
    #ax.set_xticklabels(ax.get_xticklabels(), 
    #rotation=15)

    test_results = add_stat_annotation(ax, data=df, x='Type', y='Score', order=order,
                                   box_pairs=[("s-s", "c-c"),("s-s", "c-s"),
                                   ("s-s", "s-c"),("c-c", "c-s"),
                                   ("c-c", "s-c"),("c-s", "s-c")],
                                   test='Kruskal', text_format='star', fontsize='xx-large',
                                   loc='outside', verbose=2)
    #plt.legend(loc='upper left', bbox_to_anchor=(1.03, 1), title='', fontsize = 18)
    #plt.savefig('RQ1_stat_package.png', dpi=300, bbox_inches='tight')
    return plt

def violin_box_plot_plotly(df):

    fig = px.box(df, x= "Type", y="Score", color="Type")
    fig.update_layout(showlegend=False,
    xaxis_title="Contribution Types",
    yaxis_title="DC Congruence",
    font=dict(
        size=16
    ))
    fig.update_xaxes(title_font=dict(size=16),tickfont=dict(size=16))
    fig.update_yaxes(title_font=dict(size=16),tickfont=dict(size=16))

    return fig

def rearrange_data(nonmaintain, maintain, client, library):
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
    df.to_csv('{}/package-level-dist.csv'.format(result_dir), index=False)


def get_pkg_level_plot():
    typ = ['contributor', 'maintainer', 'dependent', 'lib_maintainer']
    ss,cc, cs, sc = [],[],[],[]
    for j, item in tqdm(enumerate(typ)):
        values_pr = get_data('pr', typ[j])
        values_issue = get_data('issue', typ[j])
        print(len(values_pr), len(values_issue))
        
        if item == 'contributor':
            ss = ss + values_pr + values_issue
            print(len(ss))
        elif item ==  'maintainer':
            cc = cc + values_pr + values_issue
            print(len(cc))
        elif item == 'dependent':
            cs = cs + values_pr + values_issue
            print(len(cs))
        elif item == 'lib_maintainer':
            sc = sc + values_pr + values_issue
            print(len(sc))

    rearrange_data(ss, cc, cs, sc)
    