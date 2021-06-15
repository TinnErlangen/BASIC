## read behavioral data from .txt into a pandas dataframe and make simple statistics ##

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns
import statsmodels
from statsmodels.stats.anova import AnovaRM
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# setup directories
beh_dir = "D:/TSM_test/TEMO_behav/"

# subjects list
subjs = ["CAT_02","CAT_03","CAT_04","CAT_05","CAT_06","CAT_07","CAT_08","CAT_09",
         "CAT_10","CAT_11","CAT_12","CAT_13","CAT_14","CAT_16","CAT_17","CAT_18",
         "CAT_20","CAT_21","CAT_22","CAT_23","CAT_24","CAT_25","CAT_26","CAT_27",
         "CAT_28","CAT_29","CAT_30"]
# subjs = ["CAT_02"]


# make a dict container for group stat dataframe columns
group_df = {"Subject":subjs,"N_Laut":[],"P_Laut":[],"T_Laut":[],"N_Ang":[],"P_Ang":[],"T_Ang":[]}

# for each subject, read in the .txt results files and collect the data
for sub in subjs:
    # make containers for category data
    n_laut = []
    n_ang = []
    p_laut = []
    p_ang = []
    t_laut = []
    t_ang = []
    # read in data for N & P conditions from emo.txt, and sort them into the containers
    with open("{}{}_emo.txt".format(beh_dir,sub),"r") as file:
        lines = file.readlines()
        del lines[:2]    # delete the header line "Subject recorded..." and column headings
        x_lines = [l.split() for l in lines]    # get "words" as list per line
        for l in x_lines:
            if l[2] == "P":
                p_laut.append(l[4])
                p_ang.append(l[5])
            if l[2] == "N":
                n_laut.append(l[4])
                n_ang.append(l[5])
    # read in data for T condition from temo.txt, and sort them into the containers
    with open("{}{}_temo.txt".format(beh_dir,sub),"r") as file:
        lines = file.readlines()
        del lines[:2]    # delete the header line "Subject recorded..." and column headings
        x_lines = [l.split() for l in lines]    # get "words" as list per line
        for l in x_lines:
            t_laut.append(l[0])
            t_ang.append(l[1])

# now get the subject average for each category, and fill it into the group data dict
    group_df["N_Laut"].append(np.mean(np.array(n_laut,dtype='float64')))
    group_df["N_Ang"].append(np.mean(np.array(n_ang,dtype='float64')))
    group_df["P_Laut"].append(np.mean(np.array(p_laut,dtype='float64')))
    group_df["P_Ang"].append(np.mean(np.array(p_ang,dtype='float64')))
    group_df["T_Laut"].append(np.mean(np.array(t_laut,dtype='float64')))
    group_df["T_Ang"].append(np.mean(np.array(t_ang,dtype='float64')))

# when all subject category averages are filled in, create the pandas dataframe
temo_df = pd.DataFrame(group_df)

# do some basic stats
# e.g. get descriptives for each data column
for col in temo_df.columns:
    s = temo_df[col]
    print(s.describe())
# or plot some boxplots to look at the distributions (see how we imported seaborn above)
l = sns.boxplot(data=temo_df[["N_Laut","P_Laut","T_Laut"]])
plt.show()  # we got do this cause our seaborn output is a matplotlib object
a = sns.boxplot(data=temo_df[["N_Ang","P_Ang","T_Ang"]])
plt.show()  # we got do this cause our seaborn output is a matplotlib object
# calculate T-tests for diff. comparisons (see how we imported scipy.stats above)
print(stats.ttest_rel(temo_df['N_Laut'],temo_df['P_Laut']))
print(stats.ttest_rel(temo_df['N_Laut'],temo_df['T_Laut']))
print(stats.ttest_rel(temo_df['P_Laut'],temo_df['T_Laut']))
print(stats.ttest_rel(temo_df['N_Ang'],temo_df['P_Ang']))
print(stats.ttest_rel(temo_df['N_Ang'],temo_df['T_Ang']))
print(stats.ttest_rel(temo_df['P_Ang'],temo_df['T_Ang']))

# now do a 'real' repeated-measures ANOVA analysis
# for the function in statsmodels, we need to restructure the dataframe to 'long form'
# so we create new columns
subs = 3*subjs
subs.sort()
conds = ["N","P","T"] * len(subjs)
laut = []
for i in range(len(subjs)):
    laut.append(group_df["N_Laut"][i])
    laut.append(group_df["P_Laut"][i])
    laut.append(group_df["T_Laut"][i])
ang = []
for i in range(len(subjs)):
    ang.append(group_df["N_Ang"][i])
    ang.append(group_df["P_Ang"][i])
    ang.append(group_df["T_Ang"][i])
# and throw them in a dict to make a dataframe
dict = {"Subject":subs,"Bed":conds,"Laut":laut,"Ang":ang}
temo_long = pd.DataFrame(dict)
# now we can calculate the rmANOVAs for each Laut & Ang (see how we imported AnovaRM from statsmodels above)
anova_laut = AnovaRM(temo_long,depvar="Laut",subject="Subject",within=["Bed"],aggregate_func=None).fit()
print(anova_laut.summary())
tukey_hsd_laut = pairwise_tukeyhsd(temo_long.Laut, groups=temo_long.Bed, alpha=0.05)
print(tukey_hsd_laut.summary())
anova_ang = AnovaRM(temo_long,depvar="Ang",subject="Subject",within=["Bed"],aggregate_func=None).fit()
print(anova_ang.summary())
tukey_hsd_ang = pairwise_tukeyhsd(temo_long.Ang, groups=temo_long.Bed, alpha=0.05)
print(tukey_hsd_ang.summary())


## Example for saving a csv file from dataframe to read with another program (e.g. R or Excel)
# temo_df.to_csv("{}TEMO.csv".format(dir))  # define directory and file name to your need...
