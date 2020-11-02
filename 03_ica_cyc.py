#step 5 - inspect the ICA results and select components to exclude for all files

import mne
import matplotlib.pyplot as plt
import numpy as np

plt.ion() #this keeps plots interactive

# define file locations
proc_dir = "D:/XXX/proc/"
# pass subject and run lists
subjs = ["XXX_01","XXX_02",]
runs = ["1","3"]
# create new lists, if you want to try things on single subjects or runs

#dictionary with conditions/triggers for plotting
event_id = {'rest':100, 'baseline':80,
            'sound/tinn/neg/r1':110, 'sound/tinn/neg/r2':130, 'sound/tinn/neg/s1':150, 'sound/tinn/neg/s2':170,
            'sound/tinn/pos/r1':120, 'sound/tinn/pos/r2':140, 'sound/tinn/pos/s1':160, 'sound/tinn/pos/s2':180,
            'sound/iads/neg/max':210, 'sound/iads/neg/mid':220, 'sound/iads/pos/mid':230, 'sound/iads/pos/max':240,
            'exp/tinn/neg/r1':115, 'exp/tinn/neg/r2':135, 'exp/tinn/neg/s1':155, 'exp/tinn/neg/s2':175,
            'exp/tinn/pos/r1':125, 'exp/tinn/pos/r2':145, 'exp/tinn/pos/s1':165, 'exp/tinn/pos/s2':185,
            'exp/iads/neg/max':215, 'exp/iads/neg/mid':225, 'exp/iads/pos/mid':235, 'exp/iads/pos/max':245}

#collecting the files : triplets of annotated epoch file and corresponding reference and MEG ica result files
filelist = []
for sub in subjs:
    for run in runs:
        filelist.append(['{dir}{sub}_{run}_m-raw.fif'.format(dir=proc_dir,sub=sub,run=run),
                         '{dir}{sub}_{run}_ref-ica.fif'.format(dir=proc_dir,sub=sub,run=run),
                         '{dir}{sub}_{run}_meg-ica.fif'.format(dir=proc_dir,sub=sub,run=run),
                         '{dir}{sub}_{run}-ica.fif'.format(dir=proc_dir,sub=sub,run=run)])

ref_comp_num = 8   #number of reference components to be used as 'ground'

#definition of cycler object to go through the file list for component selection and exclusion
class Cycler():

    def __init__(self,filelist,ref_comp_num):
        self.filelist = filelist
        self.ref_comp_num = ref_comp_num

        #the go() method plots all components and sources for inspection/selection
    def go(self,idx=0):
        plt.close('all')
        # load the next epo/ICA files
        self.fn = self.filelist.pop(idx)
        self.raw = mne.io.Raw(self.fn[0],preload=True)
        self.events = np.load(self.fn[0][:-10]+"_events.npy")
        self.icaref = mne.preprocessing.read_ica(self.fn[1])
        self.icameg = mne.preprocessing.read_ica(self.fn[2])
        self.ica = mne.preprocessing.read_ica(self.fn[3])

        #housekeeping on reference components, add them to raw data
        refcomps = self.icaref.get_sources(self.raw)
        for c in refcomps.ch_names[:self.ref_comp_num]: # they need to have REF_ prefix to be recognised by MNE algorithm
            refcomps.rename_channels({c:"REF_"+c})
        self.raw.add_channels([refcomps])

        self.comps = []

        # plot everything out for overview
        self.ica.plot_components(picks=list(range(40)))
        self.ica.plot_sources(self.raw)
        self.raw.plot(duration=15.0,n_channels=90,scalings=dict(mag=1e-12,ref_meg=3e-12,misc=10),events=self.events,event_id=event_id)
        self.raw.plot_psd(fmax=95)

    def show_file(self):
        print("Current Raw File: " + self.fn[0])

    def identify_bad(self,method,threshold=3):        # old corr threshold was 0.5  (this one is z scores)
        # search for components which correlate with noise
        if isinstance(method,str):
            method = [method]
        elif not isinstance(method,list):
            raise ValueError('"method" must be string or list.')
        for meth in method:
            print(meth)
            if meth == "eog":
                inds, scores = self.ica.find_bads_eog(self.raw)
            elif meth == "ecg":
                inds, scores = self.ica.find_bads_ecg(self.raw)
            elif meth == "ref":
                inds, scores = self.ica.find_bads_ref(self.raw, method="separate",threshold=threshold)       # method="separate" is needed since mne vers. 0.21
            else:
                raise ValueError("Unrecognised method.")
            print(inds)
            if inds:
                self.ica.plot_scores(scores, exclude=inds)
                self.comps += inds

    def plot_props(self,props=None):
        # in case you want to take a closer look at a component
        if not props:
            props = self.comps
        self.ica.plot_properties(self.raw,props)

    def without(self,comps=None,fmax=95):
        # see what the data would look like if we took comps out
        self.comps += self.ica.exclude
        if not comps:
            comps = self.comps
        test = self.raw.copy()
        test.load_data()
        test = self.ica.apply(test,exclude=comps)
        test.plot_psd(fmax=fmax)
        test.plot(duration=15.0,n_channels=90,scalings=dict(mag=1e-12,ref_meg=3e-12,misc=10),events=self.events,event_id=event_id)
        self.test = test

        #when saving, enter the MEG components to be excluded, bad reference components are excluded automatically
    def save(self,comps=None):
        self.comps += self.ica.exclude
        if not comps:
            self.ica.apply(self.raw,exclude=self.comps).save(self.fn[0][:-10]+'_ica-raw.fif',overwrite=True)
        elif isinstance(comps,list):
            self.ica.apply(self.epo,exclude=self.comps+comps).save(self.fn[0][:-10]+'_ica-raw.fif',overwrite=True)
        else:
            print("No components applied, saving anyway for consistency")
            self.raw.save(self.fn[0][:-10]+'_ica-raw.fif',overwrite=True)


cyc = Cycler(filelist, ref_comp_num)

#run this file from command line with '-i' for interactive mode
#then use the cyc.go() command each time to pop the next file pair in the list for component inspection and selection
#and cyc.save() with "comps =" for the ones to be excluded when done -> it will save the 'cleaned' epochs in a new file
#then cyc.go() goes on to the next file pair again... until list is empty
