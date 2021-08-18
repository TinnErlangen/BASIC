import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns
import statsmodels
from statsmodels.stats.anova import AnovaRM
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# setup directories
beh_dir = "D:/TSM_test/MEMO_behav/"
proc_dir = "D:/TSM_test/MEMO_proc/"

# subjects list
subjs = ["MEM_14","MEM_13","MEM_03","MEM_05","MEM_04","MEM_02","MEM_15","MEM_01",
         "MEM_12","MEM_07","MEM_09","MEM_06"]
nonill_subjs = ["MEM_08","MEM_10","MEM_11"]

# dictionary with your conditions/triggers
event_id = {'4000_b': 120, '7000_b': 140, '5500_b': 160, '8500_b': 180}
trig_id = {v: k for k,v in event_id.items()}

for sub in subjs:
    # load the epoched data
    epo = mne.read_epochs("{}{}-epo.fif".format(proc_dir,sub))
    # load the ratings.txt and collect the ratings for target trials (break sounds only)
    b_trials = []
    with open("{}MEMO_{}.txt".format(beh_dir,sub[-2:]),"r") as file:
        lines = file.readlines()
        del lines[:2]    # delete the header line "Subject recorded..." and column headings
        x_lines = [l.split() for l in lines]    # get "words" as list per line
        for l in x_lines:
            if l[1] in ["120","140","160","180"]:   # leave out control trials, 'break' sounds only
                b_trials.append((l[1],l[3]))
    # then iterate over b_trials, check if matching epoch is still in, else delete
    # also, write rating into the event_id, e.g. '4000_b/break/sure' for a (120,4), '7000_b/cont/unsure' for a (140,2) etc.


    # then, copy the epochs, and select them into 30 break (all sure, then random unsure) and 30 cont (all sure, then random unsure)
    sel_epo = epo.copy()
    # get "sures" in each category and their numbers
    b_sures = sel_epo["break/sure"]
    n_b_sures = len(b_sures)
    c_sures = sel_epo["cont/sure"]
    n_c_sures = len(c_sures)
    # then get "unsures" and how many are needed to fill up 30, then randomly select
    b_unsures = sel_epo["break/unsure"]
    n_b_rest = 30 - n_b_sures
    b_rest = random.sample(b_unsures,n_b_rest)

    c_unsures = sel_epo["cont/unsure"]
    n_c_rest = 30 - n_c_sures
    c_rest = random.sample(c_unsures,n_c_rest)

    # then concatenate epochs to analysis set
    sel_epo = mne.concatenate_epochs(b_sures,b_rest,c_sures,c_rest)
    sel_epo.save("{}{}-analysis-epo.fif".format(proc_dir,sub))
