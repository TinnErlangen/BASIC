## Power analyses

import mne
import numpy as np
mne.viz.set_3d_backend('pyvista')

## remember: BRA52, ((FAO18, WKI71 - excl.)) have fsaverage MRIs (originals were defective)


proc_dir = "D:/NEMO_analyses_new/proc/"
mri_dir = "D:/freesurfer/subjects/"
sub_dict = {"NEM_10":"GIZ04","NEM_11":"WOO07","NEM_12":"TGH11","NEM_14":"FIN23","NEM_15":"KIL13",
           "NEM_16":"KIO12","NEM_17":"DEN59","NEM_18":"SAG13","NEM_20":"PAG48","NEM_22":"EAM11",
           "NEM_23":"FOT12","NEM_24":"BII41","NEM_26":"ENR41","NEM_27":"HIU14","NEM_28":"WAL70",
           "NEM_29":"KIL72","NEM_31":"BLE94","NEM_34":"KER27","NEM_35":"MUN79","NEM_36":"BRA52_fa"}  ## order got corrected
excluded = {"NEM_30":"DIU11","NEM_32":"NAG83","NEM_33":"FAO18_fa","NEM_37":"EAM67","NEM_19":"ALC81","NEM_21":"WKI71_fa"}
# sub_dict = {"NEM_10":"GIZ04"}

# the frequency bands used in dictionary form & freq_band bounds for averaging CSDs
freqs = {"theta":list(np.arange(3,8)),"alpha":list(np.arange(8,14)),"beta_low":list(np.arange(14,22)),
         "beta_high":list(np.arange(22,31)),"gamma":list(np.arange(31,47))}
freq_tup = tuple(freqs.keys())
freqs_g = {"gamma_high":list(np.arange(65,96,2))}
fmins = [3, 8, 14, 22, 31]
fmaxs = [7, 13, 21, 30, 46]
# the conditions
conditions = {'rest':'rest', 'tonbas':['tonbas','tonrat'], 'pic_n':'negative/pics', 'pic_p':'positive/pics',
              'ton_n':['negative/r1','negative/r2','negative/s1','negative/s2'], 'ton_p':['positive/r1','positive/r2','positive/s1','positive/s2']}
conds = list(conditions.keys())

## PREP PARAMETERS for Power Group Analyses
threshold = 2.861     ## choose initial T-threshold for clustering; based on p-value of .05 or .01 for df = (subj_n-1); with df=19 - 2.093, or 2.861
cond_a = 'ton_n_part4'      ## specifiy the conditions to contrast
cond_b = 'ton_p_part4'
# list for collecting stcs for group average for plotting
all_diff = []
# list for data arrays for permutation t-test on source
X_diff_s = []   # container for surface data
X_diff_v = []   # container for limbic volume data

## POWER analyses

# load fsaverage source space to morph to; prepare fsaverage adjacency matrices for cluster permutation analyses (1 surface, 1 volume)
fs_src = mne.read_source_spaces("{}fsaverage_oct6_mix-src.fif".format(proc_dir))
fs_lh = fs_src.pop(0)
fs_rh = fs_src.pop(0)
fs_surf = [fs_lh]+[fs_rh]
adjacency_s = mne.spatial_src_adjacency(fs_surf)
fs_surf_vertices = [s['vertno'] for s in fs_surf]
fs_vol = mne.read_source_spaces("{}fsaverage_limb-src.fif".format(proc_dir))
adjacency_v = mne.spatial_src_adjacency(fs_vol)
fs_limb_vertices = [s['vertno'] for s in fs_vol]
fs_src = mne.read_source_spaces("{}fsaverage_oct6_mix-src.fif".format(proc_dir))  # have to reload after popping

## prep subject STCs, make Diff_STC and morph to 'fsaverage' -- collect for group analysis
for meg,mri in sub_dict.items():
    epo = mne.read_epochs("{}{}-epo.fif".format(proc_dir,meg))
    fwd = mne.read_forward_solution("{}{}-fwd.fif".format(proc_dir,meg))
    # load filters for DICS beamformer
    filters = mne.beamformer.read_beamformer('{}{}-gamma-dics.h5'.format(proc_dir,meg))
    # load CSDs for conditions to compare, apply filters
    csd_a = mne.time_frequency.read_csd("{}{}_{}-gamma-csd.h5".format(proc_dir,meg,cond_a))
    csd_b = mne.time_frequency.read_csd("{}{}_{}-gamma-csd.h5".format(proc_dir,meg,cond_b))
    stc_a, freqs_a = mne.beamformer.apply_dics_csd(csd_a.mean(65,95),filters)
    stc_b, freqs_b = mne.beamformer.apply_dics_csd(csd_b.mean(65,95),filters)
    # calculate the difference between conditions
    stc_diff = (stc_a - stc_b) / stc_b
    # morph diff to fsaverage
    morph = mne.read_source_morph("{}{}_fs_mix-morph.h5".format(proc_dir,meg))
    stc_fs_diff = morph.apply(stc_diff)
    all_diff.append(stc_fs_diff)
    X_diff_s.append(stc_fs_diff.surface().data.T)
    X_diff_v.append(stc_fs_diff.volume().data.T)

# create STC grand average for plotting
stc_sum = all_diff.pop()
for stc in all_diff:
    stc_sum = stc_sum + stc
GA_stc_diff = stc_sum / len(sub_dict)
# plot difference on fsaverage mixed source space
# brain = GA_stc_diff.plot(subjects_dir=mri_dir,subject='fsaverage',surface='white',hemi='both',src=fs_src)
# brain.add_annotation('aparc', borders=1, alpha=0.9)

# now do cluster permutation analysis on all frequencies
X_diff_s = np.array(X_diff_s)
X_diff_v = np.array(X_diff_v)

print("Performing cluster analysis on :  gamma high")
print("Contrasting: {}  vs.  {}".format(cond_a,cond_b))
print("Looking for surface clusters")
# Xs = X_diff_s[:,i,:]
# Xs = np.expand_dims(Xs,axis=1)
t_obs, clusters, cluster_pv, H0 = clu = mne.stats.spatio_temporal_cluster_1samp_test(X_diff_s, n_permutations=1024, threshold = threshold, tail=0, adjacency=adjacency_s, n_jobs=6, step_down_p=0.05, t_power=1, out_type='indices')
# get significant clusters and plot
print(cluster_pv)
good_cluster_inds = np.where(cluster_pv < 0.05)[0]
if len(good_cluster_inds):
    stc_clu_summ = mne.stats.summarize_clusters_stc(clu, p_thresh=0.05, tstep=0.001, tmin=0, subject='fsaverage', vertices=fs_surf_vertices)  # vertices must be given here !!
    brain = stc_clu_summ.plot(subjects_dir=mri_dir,subject='fsaverage',surface='white',hemi='both',time_viewer=True,show_traces=False)
else:
    print("No sign. clusters found")
print("Looking for limbic volume clusters")
# Xv = X_diff_v[:,i,:]
# Xv = np.expand_dims(Xv,axis=1)
t_obs, clusters, cluster_pv, H0 = clu = mne.stats.spatio_temporal_cluster_1samp_test(X_diff_v, n_permutations=1024, threshold = threshold, tail=0, adjacency=adjacency_v, n_jobs=6, step_down_p=0.05, t_power=1, out_type='indices')
print(cluster_pv)
# # get significant clusters and plot
# good_cluster_inds = np.where(cluster_pv < 0.05)[0]
# if len(good_cluster_inds):
#     stc_clu_summ = mne.stats.summarize_clusters_stc(clu, p_thresh=0.05, tstep=0.001, tmin=0, subject='fsaverage', vertices=fs_limb_vertices)  # vertices must be given here !!
#     brain = stc_clu_summ.plot(subjects_dir=mri_dir,subject='fsaverage',surface='white',hemi='both',time_viewer=True,show_traces=False)
# else:
#     print("No sign. clusters found")
