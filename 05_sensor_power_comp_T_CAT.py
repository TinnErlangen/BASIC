## Explore Sensor-Level Data
## Compare Conditions with Cluster-Permutation T-Test

import mne
import numpy as np
import random
import matplotlib.pyplot as plt

plt.ioff()

# define file locations
proc_dir = "D:/TSM_test/CAT_proc/"
fig_dir = "D:/TSM_test/CAT_proc/plot/tinn-zahl/"
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

## we want to compare Alpha Power between 'tinn' and 'zahl' in a group statistic and plot

# data container for group stat analysis
Diff_all = []

# for each subject
for sub in subjs:

    # read in epo file for CAT (run 2)
    epo = mne.read_epochs("{}{}_2-epo.fif".format(proc_dir,sub))
    # interpolate bad channels for group stats
    epo.interpolate_bads()

    # 1st optional way to equalize event counts No. 1 - mne function (can only cut from the end)
    # use only one of the 2 options !
    # epo.equalize_event_counts([conds,method='truncate')

    # get data for different conditions
    tinn = epo['tinn']
    zahl = epo['zahl']

    # second option for equalizing trial counts -- random drops
    # use only one of the 2 options !
    len_diff = len(tinn.events)-len(zahl.events)
    if len_diff > 0:
        drops = random.sample(range(len(tinn.events)),k=len_diff)
        drops.sort(reverse=True)
        for drop in drops:
            tinn.drop([drop])
    if len_diff < 0:
        drops = random.sample(range(len(zahl.events)),k=abs(len_diff))
        drops.sort(reverse=True)
        for drop in drops:
            zahl.drop([drop])

    # calculate the alpha PSDs for each condition
    # the psds array will have the shape (epochs,channels,frequencies)
    tinn_psds, tinn_freqs = mne.time_frequency.psd_multitaper(tinn,fmin = 1,fmax = 40,bandwidth =1)
    zahl_psds, zahl_freqs = mne.time_frequency.psd_multitaper(zahl,fmin = 1,fmax = 40,bandwidth =1)
    diff_psds = tinn_psds - zahl_psds

    # make spatio-temporal cluster T-test
    # set parameters
    threshold = None
    # get channel connectivity for cluster permutation test
    adjacency, ch_names = mne.channels.find_ch_adjacency(epo.info, ch_type='mag')

    # MNE uses a 1sample T-test, i.e. one first subtracts the conditions as above, then tests against zero
    # needed data form: X = array of shape observations x times/freqs x locs/chans
    # so we rearrange the psd arrays accordingly, swapping the chan and freq dimensions
    diff_X = np.transpose(diff_psds,(0,2,1))
    Diff_all.append(diff_X)

    # t_obs, clusters, cluster_pv, H0 = mne.stats.spatio_temporal_cluster_1samp_test(diff_X, threshold=threshold, n_permutations=1024,
    #                                                                                tail=0, adjacency=adjacency, n_jobs=4, step_down_p=0,
    #                                                                                t_power=1, out_type='indices')
    #
    # # now explore and plot the clusters
    # # get indices of good clusters
    # good_cluster_inds = np.where(cluster_pv < .05)[0]   # it's a tuple, with [0] we grab the array therein
    # # if there are any, do more...
    # if good_cluster_inds.any():
    #     # then loop over clusters
    #     for i_clu, clu_idx in enumerate(good_cluster_inds):
    #         # unpack cluster information, get unique indices
    #         freq_inds, ch_inds = clusters[clu_idx]
    #         ch_inds = np.unique(ch_inds)
    #         freq_inds = np.unique(freq_inds)
    #
    #         # get topography for T stat (mean over cluster freqs)
    #         t_map = t_obs[freq_inds, ...].mean(axis=0)
    #         # create spatial mask for plotting (setting cluster channels to "True")
    #         mask = np.zeros((t_map.shape[0], 1), dtype=bool)
    #         mask[ch_inds, :] = True
    #         # plot average test statistic and mark significant sensors
    #         t_evoked = mne.EvokedArray(t_map[:, np.newaxis], epo.info, tmin=0)
    #         fig = t_evoked.plot_topomap(times=0, mask=mask, cmap='bwr',
    #                                     vmin=np.min, vmax=np.max,scalings=1.0,
    #                                     units="T_val", time_format= "",
    #                                     title="Subject {}\nT-Cluster {}\nFrequencies {}-{}".format(sub,
    #                                     i_clu, int(tinn_freqs[freq_inds[0]]), int(tinn_freqs[freq_inds[-1]])),
    #                                     mask_params=dict(markersize=4),
    #                                     size = 6, show=False)
    #         fig.savefig("{d}{s}_T-cluster_{f1}_to_{f2}_topo.png".format(d=fig_dir,s=sub,f1=int(tinn_freqs[freq_inds[0]]),f2=int(tinn_freqs[freq_inds[-1]])))


# CLUSTER PERMUTATION GROUP STATS OVER SUBJECTS
# find sign. diffs between conditions in frequencies X channels clusters

# prep the data for the permutation function:
# average over epochs for each subject
Diff_avs = [np.mean(x, axis=0) for x in Diff_all]
# and make an array with subjects as first dimension (observations)
X_Diff_avs = np.array(Diff_avs)

# set parameters for permutation test
threshold = None
# get channel connectivity for cluster permutation test
adjacency, ch_names = mne.channels.find_ch_adjacency(epo.info, ch_type='mag')

t_obs, clusters, cluster_pv, H0 = mne.stats.spatio_temporal_cluster_1samp_test(X_Diff_avs, threshold=threshold, n_permutations=1024,
                                                                               tail=0, adjacency=adjacency, n_jobs=4, step_down_p=0,
                                                                               t_power=1, out_type='indices')

# now explore and plot the clusters
# get indices of good clusters
good_cluster_inds = np.where(cluster_pv < .05)[0]   # it's a tuple, with [0] we grab the array therein
# if there are any, do more...
if good_cluster_inds.any():
    # then loop over clusters
    for i_clu, clu_idx in enumerate(good_cluster_inds):
        # unpack cluster information, get unique indices
        freq_inds, ch_inds = clusters[clu_idx]
        ch_inds = np.unique(ch_inds)
        freq_inds = np.unique(freq_inds)

        # get topography for T stat (mean over cluster freqs)
        t_map = t_obs[freq_inds, ...].mean(axis=0)
        # create spatial mask for plotting (setting cluster channels to "True")
        mask = np.zeros((t_map.shape[0], 1), dtype=bool)
        mask[ch_inds, :] = True
        # plot average test statistic and mark significant sensors
        t_evoked = mne.EvokedArray(t_map[:, np.newaxis], epo.info, tmin=0)
        fig = t_evoked.plot_topomap(times=0, mask=mask, cmap='bwr',
                                    vmin=np.min, vmax=np.max,scalings=1.0,
                                    units="T_val", time_format= "",
                                    title="Group Statistics\nT-Cluster {}\nFrequencies {}-{}".format(i_clu, int(tinn_freqs[freq_inds[0]]), int(tinn_freqs[freq_inds[-1]])),
                                    mask_params=dict(markersize=4),
                                    size = 6, show=False)
        fig.savefig("{d}GA_T-cluster_{f1}_to_{f2}_topo.png".format(d=fig_dir,f1=int(tinn_freqs[freq_inds[0]]),f2=int(tinn_freqs[freq_inds[-1]])))


## additional code to explore differences in spec. freq bands, even if no clusters found
## we just define freq bands and plot the mean t-values (CondA - CondB) over the group

# set up a dictionary defining your bands of interest, and assigning the indices (pointing to the freqs in tinn_freqs/zahl_freqs) of the boundaries you want
# note: the indices are not frequencies in Hz, but grab the right values for freq bands in the data (Hz can be looked up in tinn_freqs)
fois = {"Theta":(2,4), "Alpha_low":(5,7), "Alpha_high": (7,11), "Beta_low":(12,19), "Beta_high":(20,29), "Gamma":(29,38)}

for band, bounds in fois.items():
    t_map = t_obs[bounds[0]:bounds[1]+1, ...].mean(axis=0)
    # plot average test statistic and mark significant sensors
    t_evoked = mne.EvokedArray(t_map[:, np.newaxis], epo.info, tmin=0)
    fig = t_evoked.plot_topomap(times=0, cmap='bwr',
                                vmin=-2, vmax=2,scalings=1.0,   # notice that we use constant scaling for better comparison
                                units="T_val", time_format= "",
                                title="Group Difference T-Value Plot\n{} band - {} to {} Hz".format(band, int(tinn_freqs[bounds[0]])+1, int(tinn_freqs[bounds[1]])+1),
                                mask_params=dict(markersize=4),
                                size = 6, show=False)
    fig.savefig("{d}GA_T-vals_{f1}_to_{f2}_Hz_topo.png".format(d=fig_dir,f1=int(tinn_freqs[bounds[0]])+1,f2=int(tinn_freqs[bounds[1]])+1))
