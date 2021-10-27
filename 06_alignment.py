## PREPARE BEM-Model and Source Space(s)

import mne
import numpy as np
from nilearn import plotting

preproc_dir = "G:/TSM_test/NEM_proc/"
trans_dir = "G:/TSM_test/NEM_proc/" # enter your special trans file folder here
meg_dir = "G:/TSM_test/NEM_proc/"
mri_dir = "D:/freesurfer/subjects/"
sub_dict = {"TSM_02":"BAE51","TSM_07":"DTN25_fa","TSM_17":"EAH91_fa","TSM_19":"HHH42","TSM_26":"LEN04_fa",
            "TSM_22":"NAI16_fa","TSM_16":"NIC98","TSM_11":"NLK24_fa","TSM_04":"NLL75_fa","TSM_21":"NNE17",
            "TSM_15":"NOI26_fa","TSM_24":"NOR76","TSM_27":"NUT15_fa","TSM_20":"RTB16","TSM_23":"SRA67_fa",
            "TSM_06":"VIM71_fa","TSM_13":"BEU80"}
# sub_dict = {"NEM_26":"ENR41"}
runs = ["1","2","3","4"]


## prep subjects

for meg,mri in sub_dict.items():

    # read BEM solution for subject
    bem = mne.read_bem_solution("{dir}{meg}-bem.fif".format(dir=meg_dir,meg=meg))
    # load trans-file
    trans = "{dir}{mri}_{meg}-trans.fif".format(dir=trans_dir,mri=mri,meg=meg)
    # load source space
    src = mne.read_source_spaces("{dir}{meg}-oct6-src.fif".format(dir=meg_dir,meg=meg))
    # for each run, load info and plot alignment
    for run in runs:
        info = mne.io.read_info("{}{}_{}-epo.fif".format(preproc_dir,meg,run))
        mne.viz.plot_alignment(info, trans, subject=mri, dig='fiducials', meg=['helmet', 'sensors'], eeg=False, subjects_dir=mri_dir, surfaces='head-dense', bem=bem, src=src)
