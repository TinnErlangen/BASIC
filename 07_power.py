## Power analyses

import mne
import numpy as np
mne.viz.set_3d_backend('pyvista')

# set directories
proc_dir = "E:/TEMO_analyses/proc/"
mri_dir = "E:/freesurfer/subjects/"
acute = {"CAT_06":"ECN26","CAT_11":"SAN53","CAT_12":"NAO26","CAT_20":"ENC34"}
sub_dict = {"CAT_03":"IAU64_fa","CAT_05":"ZAA66_fa","CAT_07":"RWB50","CAT_09":"BEU80",
            "CAT_10":"MAU06","CAT_13":"BTE00_fa","CAT_14":"GIR89","CAT_16":"WAM42",
            "CAT_18":"EIP04","CAT_21":"MAM73","CAT_22":"AIR46","CAT_23":"RIN08_fa",
            "CAT_24":"NIP84","CAT_25":"ELL12","CAT_26":"NLF76","CAT_27":"UVC22",
            "CAT_28":"AOE32_fa","CAT_29":"SAT06_fa"}
# sub_dict = {"CAT_06":"ECN26"}

# the freq bands for the DICS filters
freqs = {"theta_low":list(np.arange(4,5)),"theta_high":list(np.arange(5,7)),"alpha_low":list(np.arange(7,9)),"alpha_high":list(np.arange(9,14)),
         "beta_low":list(np.arange(14,21)),"beta_high":list(np.arange(21,32)),"gamma":list(np.arange(32,47))}
fmins = [4, 5, 7, 9, 14, 21, 32]
fmaxs = [5, 7, 9, 14, 21, 32, 46]
freq_tup = tuple(freqs.keys())


## PREP PARAMETERS for Power Group Analyses
threshold = 2.898     ## choose initial T-threshold for clustering; based on p-value of .05 or .01 for df = (subj_n-1); with df=17 = 2.11, or 2.898
cond_a = 'att'      ## specifiy the conditions to contrast
cond_b = 'temo'
# fmin = 8.0
# fmax= 12.0
# list for collecting stcs for group average for plotting
all_diff = []
# list for data arrays for permutation t-test on source
X_diff = []

## POWER analyses

# load fsaverage source space to morph to; prepare fsaverage adjacency matrix for cluster permutation analyses
fs_src = mne.read_source_spaces("{}fsaverage_oct6-src.fif".format(proc_dir))
adjacency = mne.spatial_src_adjacency(fs_src)

## prep subject STCs, make Diff_STC and morph to 'fsaverage' -- collect for group analysis
for meg,mri in sub_dict.items():
    # load info and forward
    epo3_info = mne.io.read_info("{}{}_3_temo-epo.fif".format(proc_dir,meg))
    fwd = mne.read_forward_solution("{}{}_temo-fwd.fif".format(proc_dir,meg))
    # # load 'big' CSD for common filters
    # csd = mne.time_frequency.read_csd("{}{}_temo-csd.h5".format(proc_dir,meg))
    # # prep filters and save them
    # filters = mne.beamformer.make_dics(epo3_info,fwd,csd.mean(fmins,fmaxs),pick_ori='max-power',reduce_rank=False,depth=1.0,inversion='single')
    # filters.save('{}{}_temo-dics.h5'.format(proc_dir,meg))
    # del csd
    # load filters for DICS beamformer
    filters = mne.beamformer.read_beamformer('{}{}_temo-dics.h5'.format(proc_dir,meg))
    # load CSDs for conditions to compare, apply filters
    csd_a = mne.time_frequency.read_csd("{}{}_temo_{}-csd.h5".format(proc_dir,meg,cond_a))
    csd_b = mne.time_frequency.read_csd("{}{}_temo_{}-csd.h5".format(proc_dir,meg,cond_b))
    stc_a, freqs_a = mne.beamformer.apply_dics_csd(csd_a.mean(fmins,fmaxs),filters)
    stc_b, freqs_b = mne.beamformer.apply_dics_csd(csd_b.mean(fmins,fmaxs),filters)
    # calculate the difference between conditions
    stc_diff = (stc_a - stc_b) / stc_b
    # morph diff to fsaverage
    # morph = mne.read_source_morph("{}{}_temo_fs_oct6-morph.h5".format(proc_dir,meg))
    morph = mne.compute_source_morph(stc_diff,subject_from=mri,subject_to="fsaverage",subjects_dir=mri_dir,src_to=fs_src)
    stc_fs_diff = morph.apply(stc_diff)
    all_diff.append(stc_fs_diff)
    X_diff.append(stc_fs_diff.data.T)

# create STC grand average for plotting
stc_sum = all_diff.pop()
for stc in all_diff:
    stc_sum = stc_sum + stc
GA_stc_diff = stc_sum / len(sub_dict)
# plot GA difference on fsaverage
brain = GA_stc_diff.plot(subjects_dir=mri_dir,subject='fsaverage',surface='white',hemi='both',time_viewer=True,src=fs_src,show_traces=False)
brain.add_annotation('aparc', borders=1, alpha=0.9)

# now do cluster permutation analysis on all frequencies
X_diff = np.array(X_diff)
for i,freq in enumerate(freq_tup):
    print("Performing cluster analysis on :  {}".format(freq))
    print("Contrasting: {}  vs.  {}".format(cond_a,cond_b))
    X = X_diff[:,i,:]
    X = np.expand_dims(X,axis=1)
    t_obs, clusters, cluster_pv, H0 = clu = mne.stats.spatio_temporal_cluster_1samp_test(X, n_permutations=1024, threshold = threshold, tail=0, adjacency=adjacency, n_jobs=4, step_down_p=0.05, t_power=1, out_type='indices')
    # get significant clusters and plot
    good_cluster_inds = np.where(cluster_pv < 0.05)[0]
    if len(good_cluster_inds):
        stc_clu_summ = mne.stats.summarize_clusters_stc(clu, p_thresh=0.05, tstep=0.001, tmin=0, subject='fsaverage', vertices=fs_src)
        brain = stc_clu_summ.plot(subjects_dir=mri_dir,subject='fsaverage',surface='white',hemi='both',time_viewer=True,show_traces=False,colormap='coolwarm')       # if plotting problems, try adding: clim={'kind':'value','pos_lims':(0,0.0005,0.01)}
    else:
        print("No sign. clusters found")
