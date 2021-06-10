## Compute the Cross-Spectral-Density ##
## Preparation for DICS Beamformer Source Localization ##

import mne
import matplotlib.pyplot as plt
import numpy as np
from mne.time_frequency import csd_morlet,csd_multitaper

# define file locations
proc_dir = "D:/TSM_test/CAT_proc/"
# pass subject and run lists
subjs = ["CAT_03"]

# from your event_id or else define conditions needed for analyses & file naming
conditions = {'tinn':'tinn',
              'zahl':'zahl', 'vis':'vis'}
conditions = {'tinn':'tinn'}

# the frequencies passed as lists (for CSD calculation)
# take some time to choose appropriate values for your analysis, esp. for cycle number: what are your goals? what is the window length? etc.
freqs_n = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46]
cycs_n = [5, 5, 5, 5, 5, 7, 7,  7,  7,  7,  7,  9,  9,  9,  9,  9,  9,  9,  9, 11, 11, 11, 11, 11, 11, 11, 11, 11, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13]

freqs_g = [65, 67, 69, 71, 73, 75, 77, 79, 81, 83, 85, 87, 89, 91, 93, 95]
cycs_g = [15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15]
# fmins = [3, 8, 14, 22, 31]
# fmaxs = [7, 13, 21, 30, 46]

# for the Beamforming analysis, you need a CSD over all conditions to calculate shared filters
# for each subject, calc csd_all& csd_g_all
for sub in subjs:
    epo = mne.read_epochs("{}{}_2-epo.fif".format(proc_dir,sub))

    csd_n = csd_morlet(epo, frequencies=freqs_n, n_jobs=8, n_cycles=cycs_n, decim=1)
    csd_n.save("{}{}-csd.h5".format(proc_dir,sub))
    breakpoint()

    csd_g = csd_morlet(epo, frequencies=freqs_g, n_jobs=8, n_cycles=cycs_g, decim=1)
    csd_g.save("{}{}-gamma-csd.h5".format(proc_dir,sub))

# then, you need CSDs for the single conditions you want to pass through the filters and compare
# for each subject, calc csd & csd_g for each condition
for sub in subjs:
    epo = mne.read_epochs("{}{}_2-epo.fif".format(proc_dir,sub))

    for cond,c in conditions.items():

        csd_n = csd_morlet(epo[c], frequencies=freqs_n, n_jobs=8, n_cycles=cycs_n, decim=1)
        csd_n.save("{}{}_{}-csd.h5".format(proc_dir,sub,cond))

        csd_g = csd_morlet(epo[c], frequencies=freqs_g, n_jobs=8, n_cycles=cycs_g, decim=1)
        csd_g.save("{}{}_{}-gamma-csd.h5".format(proc_dir,sub,cond))
