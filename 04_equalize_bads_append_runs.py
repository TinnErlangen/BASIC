# step 4 - I) equalize bad channels for runs to be compared or appended in analyses
#          II) append runs (concatenate_epochs) if needed, after manually equalizing device-to-head-transformation matrix
#              Check before that 04_head_pos.py does not give a warning for excessive head position difference between the runs!
#
# the example uses run 1 and run 2 - be sure which ones you need for your analyses;
# you might want to equalize bads for more runs than you want to append, depending on analyses plan;
# it might make sense to save the final files with a more meaningful name

import mne
import numpy as np

# define file locations
proc_dir = "D:/XXX_analyses_new/proc/"
# pass subject and run lists
subjs = ["XXX_01","XXX_02",]
runs = ["1","2",]


for sub in subjs:

    # load epoch files for all needed runs
    epo_1 = mne.read_epochs("{}{}_1-epo.fif".format(proc_dir,sub))
    epo_2 = mne.read_epochs("{}{}_2-epo.fif".format(proc_dir,sub))
    # ... more if needed

    # lines for equalizing bad channels between runs
    # collect all bads into a list & pass it back to all epo.infos (duplicates don't matter so it's ok)
    bads = epo_1.info['bads'] + epo_2.info['bads']  # + more if needed
    epo_1.info['bads'] = bads
    epo_2.info['bads'] = bads
    # ... and so on

    # lines for appending runs into one epoch object
    # overwriting the device-to-head-transform of one run with the other
    epo_1.info['dev_head_t'] = epo_2.info['dev_head_t']
    # ... or for more..
    epos_12 = mne.concatenate_epochs([epo_1, epo_2])    # can be more than two
    epos_12.save("{}{}_exp-epo.fif".format(proc_dir,sub),overwrite=True)   # choose a good filename here
