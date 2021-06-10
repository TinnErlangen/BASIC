#step 4 A - epoching by slicing up long trials (e.g. 60s into 1s or 2s slices)

import mne
import numpy as np

# define file locations
proc_dir = "D:/TSM_test/CAT_proc/"
# pass subject and run lists
subjs = ["CAT_03","CAT_10","CAT_18",
         "CAT_06","CAT_11","CAT_12"]
acute = ["CAT_06","CAT_11","CAT_12"]
chronic = ["CAT_03","CAT_10","CAT_18"]
runs = ["2"]

# provide the dictionary with your conditions/triggers
event_id = {'tinn': 180, 'zahl': 160, 'vis': 140}
trig_id = {v: k for k,v in event_id.items()}   # this reverses the dictionary and might be useful later
# !! event_id specifies the triggers to use for epoching - so make sure to include only those needed in the dictionary !!
# you might provide a new, reduced dictionary here for creating the epochs object below
# event_id = {'rest': 220}


# HERE, define the slicing parameters
# mini_epochs_num gives the total number of slices per trial
# ex1) for a 180s resting state recording and 2s epochs, this will be 90 (for 1s epochs 180)
# ex2) for recurring trials of 20s length, this will be 10 for 2s epochs (20 for 1s epochs) etc.
mini_epochs_num = 60
# mini_epochs_len gives the time length of the slices in seconds, i.e. 2 for 2s epochs etc.
mini_epochs_len = 1


for sub in subjs:
    for run in runs:
        #loading raw data and original events array
        raw = mne.io.Raw('{}{}_{}_ica-raw.fif'.format(proc_dir,sub,run))
        # the event array is converted to a list to be able to append our new slice events
        events = list(np.load('{}{}_{}_events.npy'.format(proc_dir,sub,run)))
        #creating new event list with starting time points (sample points) for the sliced epochs
        new_events = []
        # each time we encounter a original event (trigger): ...
        for e in events:
            # for as many slices as we need per long event: ...
            for me in range(mini_epochs_num):
                # write new mini events with our slicing time points into the new_events list
                new_events.append(np.array(
                [e[0]+me*mini_epochs_len*raw.info["sfreq"], 0, e[2]]))
                # above, in [...,0,...], the first term calculates the sample time point of the mini event onset using sfreq,
                # the last term provides the trigger value to assign to the mini event;
                # in this example, the trigger of the original event is just repeated for each mini event,
                # but you could provide code to assign different triggers dependent on order of slice/part or similar
        # when done, re-transform the event list into an integer array for MNE
        new_events = np.array(new_events).astype(int)

        # optional check if events are alright. with these lines you could check if the sample time points are calculated correctly,
        # the number of total new events is right, and check the triggers
        # ..comment out, if not needed
        print(new_events[:25,:])
        print(len(new_events))
        print(np.unique(new_events[:,2]))

        # creating Epoch object from new event list
        # !! event_id specifies the triggers to use for epoching - so make sure to include only those needed in the dictionary !!
        # note that sliced epochs have no baseline, so tmin=0, tmax=mini_epochs_len
        epochs = mne.Epochs(raw,new_events,event_id=event_id,baseline=None,picks=['meg'],tmin=0,tmax=mini_epochs_len,preload=True)

        # optional check of the epochs and labels; practice to use slicing, condition selection, or the drop log
        # ..comment out, if not needed
        print(epochs.event_id)
        print(epochs.events[:12])
        print(epochs[1:3])
        print(epochs['tinn'])   # try your own condition label(s) or sub-labels here
        print(epochs.drop_log)
        print(len(epochs.drop_log))

        # saving the epochs to file
        epochs.save('{}{}_{}-epo.fif'.format(proc_dir,sub,run),overwrite=True)

        # optional plotting check - try looking at the epoch data with diff. plots
        # ..comment out, if not needed
        epochs.plot(n_epochs=10,n_channels=90,picks=['meg'],scalings=dict(mag=0.5e-12),events=new_events,event_id=event_id)
        epochs.plot_psd(fmax=95,bandwidth=1)
        epochs.plot_psd_topomap()
