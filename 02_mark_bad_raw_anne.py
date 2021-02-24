# This script creates a Cycler object to loop over your raw data to mark bad segments
# Run this file from command line with '-i' for interactive mode
# Then use the cyc.go() command each time to pop the next file in the list for inspection and annotation - then use cyc.save() when done
# ...then cyc.go() again for the next file... until the list is empty

import mne
import matplotlib.pyplot as plt
import numpy as np

plt.ion() #this keeps plots interactive

# define file locations
proc_dir = "D:/TSM_test/proc/"
# pass subject and run lists
subjs = ["TSM_01","TSM_03","TSM_04","TSM_05"]
# subjs = ["TSM_01"]
runs = ["3"]
# runs = ["1"]
# create new lists, if you want to try things on single subjects or runs

#dictionary with conditions/triggers for plotting
event_id_old = {'block1': 200,'block2': 220}
event_id = {'anspannung': 60,'entspannung': 80, 'anspannung/r1':190, 'anspannung/r2':191, 'anspannung/s1':192, 'anspannung/s2':193,
            'entspannung/r1':195, 'entspannung/r2':196, 'entspannung/s1':197, 'entspannung/s2':198}
cond_seq = {"TSM_01": 1, "TSM_03": 2, "TSM_04": 2, "TSM_05": 1}   # 1 = Anspannung zuerst; 2 = Entspannung zuerst

# Korrektur der Triggerzuschreibung in SOMA-Block 2
for sub in subjs:
    events_old = np.load("{dir}{sub}_2_events.npy".format(dir=proc_dir,sub=sub))
    events = events_old.copy()
    if cond_seq[sub] == 1:
        for i in range(events.shape[0]):
            if events[i][2] == 200:
                events[i][2] = 60
            if events[i][2] == 220:
                events[i][2] = 80
    if cond_seq[sub] == 2:
        for i in range(events.shape[0]):
            if events[i][2] == 200:
                events[i][2] = 80
            if events[i][2] == 220:
                events[i][2] = 60
    np.save("{dir}{sub}_2_events_old.npy".format(dir=proc_dir,sub=sub),events_old)
    np.save("{dir}{sub}_2_events.npy".format(dir=proc_dir,sub=sub),events)

# collecting the files for annotation into a list
filelist = []
for sub in subjs:
    for run in runs:
        filelist.append('{dir}{sub}_{run}-raw.fif'.format(dir=proc_dir,sub=sub,run=run))

#definition of cycler object to go through the file list for annotation
class Cycler():

    def __init__(self,filelist):
        self.filelist = filelist    # when initializing the object, the filelist is collected

    def go(self):
        self.fn = self.filelist.pop(0)    # this pops the first raw file from the list
        self.raw = mne.io.Raw(self.fn)
        self.events = np.load(self.fn[:-8]+"_events.npy")   # and loads the events
        self.raw.plot(duration=15.0,n_channels=90,scalings=dict(mag=0.5e-12),events=self.events,event_id=event_id)    #  these parameters work well for inspection, but change to your liking (works also interactively during plotting)
        self.raw.plot_psd(fmax=95)    # we also plot the PSD, which is helpful to spot bad channels

    def plot(self,n_channels=90):
        self.raw.plot(duration=15.0,n_channels=90,scalings=dict(mag=0.5e-12),events=self.events,event_id=event_id)

    def show_file(self):
        print("Current Raw File: " + self.fn)    # use this to find out which subject/run we're looking at currently

    def save(self):
        self.raw.save(self.fn[:-8]+'_m-raw.fif',overwrite=True)   # important: save the annotated file in the end !

cyc = Cycler(filelist)


# Tipps: click on bad channels to mark them (they're easily spotted from the PSD plot); press 'a' to switch in annotation mode and drag the mouse over 'BAD' segments to mark with that label
# important: close the plot to save the markings! - then do cyc.save() to save the file
