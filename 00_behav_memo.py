import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns
import statsmodels
from statsmodels.stats.anova import AnovaRM
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# setup directories
beh_dir = "D:/TSM_test/MEMO_behav/"

# subjects list
subjs = ["MEM_01","MEM_02","MEM_03","MEM_04","MEM_05","MEM_06","MEM_07","MEM_08",
         "MEM_09","MEM_10","MEM_11","MEM_12","MEM_13","MEM_14","MEM_15",
         "TSM_01","TSM_02","TSM_04","TSM_06","TSM_07","TSM_08","TSM_09","TSM_10",
         "TSM_11","TSM_12","TSM_13","TSM_14","TSM_15","TSM_16","TSM_17","TSM_19",
         "TSM_20","TSM_21",
         "TSM_03","TSM_05","TSM_18"]
control = ["MEM_01","MEM_02","MEM_03","MEM_04","MEM_05","MEM_06","MEM_07","MEM_08",
           "MEM_09","MEM_10","MEM_11","MEM_12","MEM_13","MEM_14","MEM_15"]
chronic = ["TSM_01","TSM_02","TSM_04","TSM_06","TSM_07","TSM_08","TSM_09","TSM_10",
           "TSM_11","TSM_12","TSM_13","TSM_14","TSM_15","TSM_16","TSM_17","TSM_19",
           "TSM_20","TSM_21"]               # !! TSM_14 has no MEG data, maybe all numbering after that is wrong here...
acute = ["TSM_03","TSM_05","TSM_18"]        # !! Vorsicht! MEMO_cat_18 might not be TSM_18 !!


# make a dict container for group stat dataframe columns
group_df = {"Subject":subjs,"Group":[],"Ill_ratio":[],"Cont_count":[],"Break_count":[]}

# loop over subjects and fill values
for sub in subjs:
    # first add the group value
    if sub in control:
        group_df["Group"].append("control")
    if sub in chronic:
        group_df["Group"].append("chronic")
    if sub in acute:
        group_df["Group"].append("acute")
    # now read in the ratings, collect values and calculate illusion ratio
    cont_count = 0
    break_count = 0
    if sub in control:
        with open("{}MEMO_{}.txt".format(beh_dir,sub[-2:]),"r") as file:
            lines = file.readlines()
            del lines[:2]    # delete the header line "Subject recorded..." and column headings
            x_lines = [l.split() for l in lines]    # get "words" as list per line
            for l in x_lines:
                if l[1] in ["120","140","160","180"]:   # leave out control trials, 'break' sounds only 
                    if l[3] in ["1","2"]:
                        cont_count = cont_count + 1
                    if l[3] in ["3","4"]:
                        break_count = break_count + 1
    if sub in chronic or sub in acute:
        with open("{}MEMO_cat_{}.txt".format(beh_dir,sub[-2:]),"r") as file:
            lines = file.readlines()
            del lines[:2]    # delete the header line "Subject recorded..." and column headings
            x_lines = [l.split() for l in lines]    # get "words" as list per line
            for l in x_lines:
                if l[1] in ["120","140","160","180"]:
                    if l[3] in ["1","2"]:
                        cont_count = cont_count + 1
                    if l[3] in ["3","4"]:
                        break_count = break_count + 1
    ill_rat = cont_count / (cont_count + break_count)   # the total trial number differs between patients and controls!
    group_df["Ill_ratio"].append(ill_rat)
    group_df["Cont_count"].append(cont_count)
    group_df["Break_count"].append(break_count)

# now creata a pandas dataframe and make simple analyses
memo_df = pd.DataFrame(group_df)

print(memo_df.groupby("Group").describe())
l = sns.boxplot(x="Group",y="Ill_ratio",data=memo_df)
plt.show()
l = sns.swarmplot(x="Group",y="Ill_ratio",data=memo_df)
plt.show()

# anova_ill = AnovaRM(memo_df,depvar="Ill_ratio",subject="Subject",within=["Group"],aggregate_func=None).fit()
# print(anova_ill.summary())      # gives error, because data are unbalanced

# explore numbers of people with lots of or few illusions
# throw out acute patients
memo = memo_df.query("Group != 'acute'")
memo.Ill_ratio.describe()
ill_people = memo.query("Ill_ratio > 0.5")
print(ill_people.groupby("Group").count())
nonill_people = memo.query("Ill_ratio < 0.5")
print(nonill_people.groupby("Group").count())
# or also
ill_people = memo.query("Ill_ratio > (Ill_ratio.mean() + Ill_ratio.std())")
nonill_people = memo.query("Ill_ratio < (Ill_ratio.mean() - Ill_ratio.std())")

# and so on ....
