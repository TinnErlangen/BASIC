# look at Grand Averages of Evoked, and of TFR
import mne
import numpy as np

# setup directories
beh_dir = "C:/Users/kimca/Documents/MEMO_analyses_BA/behav/"
proc_dir = "C:/Users/kimca/Documents/MEMO_analyses_BA/proc/"

# subjects list
subjs = ["MEM_14","MEM_13","MEM_03","MEM_05","MEM_04","MEM_02","MEM_15","MEM_01",
         "MEM_12","MEM_07","MEM_09","MEM_06"]
nonill_subjs = ["MEM_08","MEM_10","MEM_11"]
subjs = ["MEM_01","MEM_02","MEM_03"]


# load the epos
epos = []
for sub in subjs:
    epo = mne.read_epochs("{}{}-analysis-epo.fif".format(proc_dir,sub))
    epo.interpolate_bads()  # on sensor level, this makes sense
    epos.append(epo)
# get layout for plotting later
layout = mne.find_layout(epo.info)
mag_names = [epo.ch_names[p] for p in mne.pick_types(epo.info, meg=True)]
layout.names = mag_names

# # do the GA Evoked (break,cont, and difference cont-break)
# # get lists and Evoked-containers started
# contevs = [epos[0]['cont'].average()]
# breakevs = [epos[0]['break'].average()]
# diffevs = [contevs[0].copy()]
# diffevs[0].data = contevs[0].data - breakevs[0].data
# diffevs[0].comment = 'contrast cont-break'
# # then loop through remaining epos for averaging
# for epo in epos[1:]:
#     contev = epo['cont'].average()
#     breakev = epo['break'].average()
#     diffev = contev.copy()
#     diffev.data = contev.data - breakev.data
#     diffev.comment = 'contrast cont-break'
#     contevs.append(contev)
#     breakevs.append(breakev)
#     diffevs.append(diffev)
# # calc GAs and plot
# GA_cont = mne.grand_average(contevs)
# GA_cont.plot_joint()
# GA_break = mne.grand_average(breakevs)
# GA_break.plot_joint()
# GA_diff = mne.grand_average(diffevs)
# GA_diff.plot_joint()

# calculate TFRs per subject
freqs = np.arange(3,47,1)
n_cycles = 7
cont_TFRs = []
break_TFRs = []
diff_TFRs = []
for epo in epos:
    cont_TFR = mne.time_frequency.tfr_morlet(epo['cont'], freqs, n_cycles, use_fft=False, return_itc=False, decim=1, n_jobs=6, picks=None, zero_mean=True, average=True, output='power')
    cont_TFR.apply_baseline((None,0),mode='percent')
    cont_TFRs.append(cont_TFR)
    break_TFR = mne.time_frequency.tfr_morlet(epo['break'], freqs, n_cycles, use_fft=False, return_itc=False, decim=1, n_jobs=6, picks=None, zero_mean=True, average=True, output='power')
    break_TFR.apply_baseline((None,0),mode='percent')
    break_TFRs.append(break_TFR)
    diff_TFR = cont_TFR.copy()
    diff_TFR.data = cont_TFR.data - break_TFR.data
    diff_TFRs.append(diff_TFR)
GA_cont_TFR = mne.grand_average(cont_TFRs)
GA_cont_TFR.save("{}GA_MEM01-03_cont-tfr.h5".format(proc_dir))
GA_cont_TFR.plot_topo(baseline=None,mode=None,layout=layout,fig_facecolor='white',font_color='black')
GA_break_TFR = mne.grand_average(break_TFRs)
GA_break_TFR.save("{}GA_MEM01-03_break-tfr.h5".format(proc_dir))
GA_break_TFR.plot_topo(baseline=None,mode=None,layout=layout,fig_facecolor='white',font_color='black')
GA_diff_TFR = mne.grand_average(diff_TFRs)
GA_diff_TFR.save("{}GA_MEM01-03_diff_C-B-tfr.h5".format(proc_dir))
GA_diff_TFR.plot_topo(baseline=None,mode=None,layout=layout,fig_facecolor='white',font_color='black',vmin=-1,vmax=1)

# # re-plotting with different time or freq boundaries
# GA_diff_TFR.plot_topo(baseline=None,mode=None,layout=layout,fig_facecolor='white',font_color='black',tmin=None,tmax=5.0,fmin=5,fmax=35,vmin=-1,vmax=1)
# # or try a joint plot for 'peak tiles with title
#GA_cont_TFR.plot_joint(timefreqs={(1, 10): (0.1, 2)},baseline=None,mode=None,title="GA - TFR response Negative-Positive")  # set favorite topo peaks here, value tuple sets windows centered on time and freq
