#step 4 B - epoching by selecting epochs around existing triggers for target events, defining length and baseline

import mne
import numpy as np

# define file locations
proc_dir = "D:/XXX_analyses_new/proc/"
# pass subject and run lists
subjs = ["XXX_01","XXX_02",]
runs = ["1","2",]

# provide the dictionary with your conditions/triggers
event_id = {'cond_A/pic': 100, 'cond_A/tone': 110, 'cond_B/pic': 200, 'cond_B/tone': 210}
trig_id = {v: k for k,v in event_id.items()}   # this reverses the dictionary and might be useful later
# !! event_id specifies the triggers to use for epoching - so make sure to include only those needed in the dictionary !!
# you might provide a new, reduced dictionary here for creating the epochs object below
zero_id = {'cond_A/pic': 100, 'cond_B/pic': 200}    # e.g. if trials are centered on pictures as zero point for a trial containing pic then tone

# set parameters for epoching; tmin/tmax are in seconds
baseline = None     # if baseline correction should be applied; can be done manually later
tmin = -0.4         # starting before 0 defines the baseline period
tmax = 2.6          # gives the end point, i.e. trial length


for sub in subjs:
    for run in runs:
        # loading raw data and events array
        raw = mne.io.Raw('{}{}_{}_ica-raw.fif'.format(proc_dir,sub,run))
        events = np.load('{}nc_{}_{}_events.npy'.format(proc_dir,sub,run))
        # creating the epochs around our zero event triggers
        epochs = mne.Epochs(raw,events,event_id=zero_id,baseline=baseline,picks=['meg'],tmin=tmin,tmax=tmax,preload=True)
        # optional check, if it worked correctly
        print(epochs)

        # optional check of the epochs and labels; practice to use slicing, condition selection, or the drop log
        # ..comment out, if not needed
        print(epochs.event_id)
        print(epochs.events[:12])
        print(epochs[1:3])
        print(epochs['cond_A'])   # try your own condition label(s) or sub-labels here
        print(epochs['cond_B/pic'])   # try your own condition label(s) or sub-labels here
        print(epochs.drop_log)
        print(len(epochs.drop_log))

        # saving the epochs to file
        epochs.save('{}{}_{}-epo.fif'.format(proc_dir,sub,run),overwrite=True)

        # optional plotting check - try looking at the epoch data with diff. plots
        # ..comment out, if not needed
        epochs.plot(n_epochs=10,n_channels=90,picks=['meg'],scalings=dict(mag=0.5e-12),events=events,event_id=event_id) # providing event_id here should draw lines for all events, not just the zero event
        epochs.plot_psd(fmax=95,bandwidth=1)
        epochs.plot_psd_topomap()
