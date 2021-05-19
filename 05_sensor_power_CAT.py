import mne
import numpy as np
import matplotlib.pyplot as plt

plt.ioff()

# define file locations
proc_dir = "D:/TSM_test/CAT_proc/"
fig_dir = "D:/TSM_test/CAT_proc/plot/"
# pass subject and run lists
subjs = ["CAT_03","CAT_10","CAT_18",
         "CAT_06","CAT_11","CAT_12"]
acute = ["CAT_06","CAT_11","CAT_12"]
chronic = ["CAT_03","CAT_10","CAT_18"]
runs = ["2"]

# provide the dictionary with your conditions/triggers
event_id = {'tinn': 180, 'zahl': 160, 'vis': 140}
trig_id = {v: k for k,v in event_id.items()}
conds = ['tinn', 'zahl', 'vis']

# for each subject
for sub in subjs:

    # read in epo file for CAT (run 2)
    epo = mne.read_epochs("{}{}_2-epo.fif".format(proc_dir,sub))
    # get data for different conditions
    for cond in conds:
        # plot PSD for each condition
        fig1 = epo[cond].plot_psd(fmax=45,bandwidth=1,show=False)
        fig1.savefig("{d}{s}_{c}_psd.png".format(d=fig_dir,s=sub,c=cond))
        # plot PSD topomap for alpha band for each condition
        fig2 = epo[cond].plot_psd_topomap(bands=[(7, 13, 'Alpha')],bandwidth=1,vlim=(None,None),show=False)
        fig2.savefig("{d}{s}_{c}_alpha_topo.png".format(d=fig_dir,s=sub,c=cond))

        
