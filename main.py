import streamlit as st
from src.package_level_dc import *
from src.ecosystem_level_dc import *
from src.visualize_individuals import *
from tqdm import tqdm
import os
import pandas as pd
import csv
st.set_page_config(page_title="DC Congruence",layout="wide")
st.subheader("Giving Back: Contributions Congruent to Library Dependency Changes in a Software Ecosystem")
st.markdown("##")
result_dir = './congruence-results'
proj_dir = './project_data'
# Style
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

def cal_stat(df):
    max_dc = float(df['Score'].max())
    median_dc = float(df['Score'].median())
    mean_dc = float(df['Score'].mean())
    min_dc = float(df['Score'].min()) 
    return max_dc, median_dc, mean_dc, min_dc

def show_stat(title, df):
    max_dc, median_dc, mean_dc, min_dc = cal_stat(df)
    st.info(title,icon="📌")
    total1,total2,total3,total4=st.columns(4,gap='medium')
    with total1:
        st.metric(label="max",value=f"{max_dc:,.2f}")
    with total2:
        st.metric(label="median",value=f"{median_dc:,.2f}")
    with total3:
        st.metric(label="mean",value=f"{mean_dc:,.2f}")
    with total4:
        st.metric(label="min",value=f"{min_dc:,.2f}")

@st.cache_data  
def load_data(path):
    df = pd.read_csv(path)
    return df

def add_abstract():
    content = """
    The modern computer programs that run your favorite apps or websites can be extremely large, often measured in millions of lines of code. 
    This is obviously much more complex than can be handled by any one individual. Most programming languages therefore rely on specialized modules 
    called third-party libraries to accomplish specific tasks. These libraries are often open-source and freely available to anyone who wants to 
    download and use them. For example, programmers in JavaScript have access to over one million libraries, while there are more than 
    300,000 libraries for the Python community. The libraries themselves often rely on each other, with the typical library requiring the use of 
    about five others. However, the ecosystem of interconnected libraries and their dependencies on each other is poorly understood, which is 
    concerning since a failure in one could have cascading effects on the entire system. Sustained contributions are crucial, because 
    the dependencies of any one library on others must be constantly updated in response to changes. However, maintainers of these libraries are 
    often overworked and often contribute as unpaid volunteers.

    We study these networks by defining a metric called **"dependency-contribution congruence" (DC congruence)**, which measures how closely 
    the network of library dependencies matches the network of contributor changes. The congruence metric is largest when the same contributor 
    makes changes to both a library and its dependents. We found that DC congruence shares an inverse relationship with the likelihood that 
    a library becomes dormant. Specifically, a library is less likely to become dormant if the contributions are congruent with upgrading 
    dependencies. We measured the DC congruence within the npm ecosystem of JavaScript libraries and analyzed over 5.3 million change commits 
    across 107,242 different libraries.

    This research may help keep software running and identify fragile points in the dependency network, and may ultimately encourage 
    dependency contributions that support the maintenance of interdependent third-party libraries used in software development.
    """

    #with st.expander("🎯 Project Motivation and Description"):
    st.subheader("🎯 Project Motivation and Description")
    st.markdown(content)

    st.markdown("""---""")

def main():
    add_abstract()
    progress_text = "Downloading data. Please wait."
    my_bar = st.progress(0, text=progress_text)
    percent_complete = 0
    df_facet = load_data('{}/ecosystem-level-facet.csv'.format(result_dir)) 
    df_dist = load_data('{}/ecosystem-level-dist.csv'.format(result_dir))
    my_bar.progress(percent_complete + 25, text=progress_text)

    df_pkg = load_data('{}/package-level-dist.csv'.format(result_dir))
    my_bar.progress(percent_complete + 25, text=progress_text)

    df_commit = load_data('{}/project_commits.csv'.format(proj_dir))
    df_cong = load_data('{}/project_congruence.csv'.format(proj_dir))
    df_contri = load_data('{}/project_contributors.csv'.format(proj_dir))
    df_dep = load_data('{}/project_dependencies.csv'.format(proj_dir))
    df_issue = load_data('{}/project_issues.csv'.format(proj_dir))
    df_pull = load_data('{}/project_pulls.csv'.format(proj_dir))
    df_info = load_data('{}/project_repositories.csv'.format(proj_dir))
    repo_list = df_commit['Repo_name'].tolist()
    repo_list = list(set(repo_list))

    my_bar.progress(percent_complete + 50, text=progress_text)

    st.subheader("📊 Ecosystem Size")
    row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3, row2_3, row2_spacer4, row2_4, row2_spacer5, row2_5, row2_spacer6  = st.columns((.2, 1.6, .2, 1.6, .2, 1.6, .2, 1.6, .2, 1.6, .2))
    with row2_1:
        st.markdown("""
        ### 107,242 
        packages""")
    with row2_2:
        st.markdown("""
        ### 1,754,952 
        issues""")
    with row2_3:
         st.markdown("""
         ### 970,685 
         PRs""")
    with row2_4:
         st.markdown("""
         ### 5,325,129 
         commits""")
    with row2_5:
         st.markdown("""
         ### 437,045 
         developers""")

    st.markdown("""---""")

    tab1, tab2, tab3 = st.tabs(["Distributions of DC Congruence", "Library-level DC Congruence over time", "Ecosystem-level DC Congruence over time"])
    with tab1:
        left,right=st.columns(2)
        with left:
            st.markdown("### Library-Level DC congruence")
            st.plotly_chart(violin_box_plot_plotly(df_pkg), theme="streamlit", use_container_width=True)
            show_stat('Library-Level DC Congruence Statistic', df_pkg)
        with right:
            st.markdown("### Ecosystem-Level DC congruence")
            st.plotly_chart(box_plotly(df_dist),theme="streamlit", use_container_width=True)
            show_stat('Ecosystem-Level DC Congruence Statistic', df_dist)

    with tab2:
        show_list = [repo.replace(':','/') for repo in repo_list]
        selected_name = st.selectbox(
            label="Please choose Library repository name [owner name]/[repo name]",
            options=show_list,
        )

        roles = st.radio(
        "Please choose contribution type",['s-s', 'c-c', 'c-s', 's-c'])

        other_plot, cong_plot = plot_individuals(selected_name, roles, df_commit, df_cong, df_contri, df_dep, df_issue, df_pull)
        left2,right2=st.columns(2)
        with left2:
            st.markdown("### Library-level DC congruence over time")
            st.plotly_chart(cong_plot,theme="streamlit", use_container_width=True)
        with right2:
            st.markdown("### Other metrics over time")
            st.plotly_chart(other_plot,theme="streamlit", use_container_width=True)

        fig1, fig2, fig3 = plot_gauge(df_info, selected_name)
        left3,center3, right3=st.columns(3)
        with left3:
            st.plotly_chart(fig1,theme="streamlit", use_container_width=True)
        with center3:
            st.plotly_chart(fig2,theme="streamlit", use_container_width=True)
        with right3:
            st.plotly_chart(fig3,theme="streamlit", use_container_width=True)


    with tab3:
        selected_role = st.selectbox(
            label="Please choose contribution type",
            options=['s-s', 'c-c', 'c-s', 's-c'],
        )
        st.markdown("### Ecosystem-Level DC congruence over time")
        st.plotly_chart(facet_row_column(df_facet, selected_role),theme="streamlit", use_container_width=True)
    
    my_bar.empty()

    with st.expander("See notes"):
        st.markdown("""
        We define **Ecosystem-level DC Congruence** as the ratio of dependency changes that receive contributions 
        divided by the total number of dependency changes in the ecosystem.
        We also measure **Library-level DC Congruence** to quantify how the congruence related to a library contributed to the congruence value of the whole ecosystem.

        To calculate DC congruence, we define contribution types based on four different types of contributions which are: 
        - contributions from a contributor who commits to both client and library **(c-c)**
        - contributions from a contributor who commits to a client and submits to a library **(c-s)**
        - contributions from a contributor who submits to a client and commits to a library **(s-c)**
        - contributions from a contributor who submits to both client and library **(s-s)**
        

        In terms of the dependency changes, we consider four types of different dependency changes which are:
        - adding a dependency **(added)**
        - removing a dependency **(removed)** 
        - upgrading a dependency **(upgraded)**
        - downgrading a dependency **(downgraded)**""")

    citation = """
### Paper Citation
If you use this visualization in a scientific publication, we would appreciate citation to the following paper:
```
@ARTICLE{9964443,
  author={Wattanakriengkrai, Supatsara and Wang, Dong and Kula, Raula Gaikovina and Treude, Christoph and Thongtanunam, Patanamon and Ishio, Takashi and Matsumoto, Kenichi},
  journal={IEEE Transactions on Software Engineering}, 
  title={Giving Back: Contributions Congruent to Library Dependency Changes in a Software Ecosystem}, 
  year={2023},
  volume={49},
  number={4},
  pages={2566-2579},
  doi={10.1109/TSE.2022.3225197}}
```
    """
    st.markdown(citation)

main()

#theme
hide_st_style=""" 

<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
"""