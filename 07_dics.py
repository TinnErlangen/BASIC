## Compute DICS filters and

import mne
import numpy as np

## remember: BRA52, ((FAO18, WKI71 - excl.)) have fsaverage MRIs (originals were defective)


proc_dir = "D:/NEMO_analyses_new/proc/"
mri_dir = "D:/freesurfer/subjects/"
sub_dict = {"NEM_10":"GIZ04","NEM_11":"WOO07","NEM_12":"TGH11","NEM_14":"FIN23","NEM_15":"KIL13",
           "NEM_16":"KIO12","NEM_17":"DEN59","NEM_18":"SAG13","NEM_20":"PAG48","NEM_22":"EAM11",
           "NEM_23":"FOT12","NEM_24":"BII41","NEM_26":"ENR41","NEM_27":"HIU14","NEM_28":"WAL70",
           "NEM_29":"KIL72","NEM_31":"BLE94","NEM_34":"KER27","NEM_35":"MUN79","NEM_36":"BRA52_fa"}  ## order got corrected
excluded = {"NEM_30":"DIU11","NEM_32":"NAG83","NEM_33":"FAO18_fa","NEM_37":"EAM67","NEM_19":"ALC81","NEM_21":"WKI71_fa"}
# sub_dict = {"NEM_10":"GIZ04"}

# ## FIRST ROUND
# # the frequency bands used in dictionary form
# freqs = {"theta":list(np.arange(3,8)),"alpha":list(np.arange(8,14)),"beta_low":list(np.arange(14,22)),
#          "beta_high":list(np.arange(22,31)),"gamma":list(np.arange(31,47))}
# freqs_g = {"gamma_high":list(np.arange(65,96,2))}
# fmins = [3, 8, 14, 22, 31]
# fmaxs = [7, 13, 21, 30, 46]
#
#
# for meg,mri in sub_dict.items():
#     epo = mne.read_epochs("{}{}-epo.fif".format(proc_dir,meg))
#     fwd = mne.read_forward_solution("{}{}-fwd.fif".format(proc_dir,meg))
#     # calculate filters for lower freq bands
#     csd = mne.time_frequency.read_csd("{}{}-csd.h5".format(proc_dir,meg))
#     filters = mne.beamformer.make_dics(epo.info,fwd,csd.mean(fmins,fmaxs),pick_ori='max-power',reduce_rank=False,depth=1.0,inversion='single')
#     filters.save('{}{}-dics.h5'.format(proc_dir,meg))
#     # calculate filters for high gamma freq band
#     csd_g = mne.time_frequency.read_csd("{}{}-gamma-csd.h5".format(proc_dir,meg))
#     filters_g = mne.beamformer.make_dics(epo.info,fwd,csd_g.mean(65,95),pick_ori='max-power',reduce_rank=False,depth=1.0,inversion='single')
#     filters_g.save('{}{}-gamma-dics.h5'.format(proc_dir,meg))


## REDOING FILTERS FOR NEW FREQ BANDS AFTER TFR EXPLORATION
# frequencies = [[4.], [5.,6.], [7.,8.], [9.,10.,11.,12.,13.], [14.,15.,16.,17.,18.,19.,20.], [21.,22.,23.,24.,25.,26.,27.,28.,29.,30.,31.],[32.,33.,34.,35.,36.,37.,38.,39.,40.,41.,42.,43.,44.,45.,46.]]
frequencies = [[4.,5.], [5.,6.,7.], [7.,8.,9.], [9.,10.,11.,12.,13.,14.], [14.,15.,16.,17.,18.,19.,20.,21.], [21.,22.,23.,24.,25.,26.,27.,28.,29.,30.,31.,32.],[32.,33.,34.,35.,36.,37.,38.,39.,40.,41.,42.,43.,44.,45.,46.]]
freqs = {"theta_low":list(np.arange(4,5)),"theta_high":list(np.arange(5,7)),"alpha_low":list(np.arange(7,9)),"alpha_high":list(np.arange(9,14)),
         "beta_low":list(np.arange(14,21)),"beta_high":list(np.arange(21,32)),"gamma":list(np.arange(32,47))}
fmins = [4, 5, 7, 9, 14, 21, 32]
fmaxs = [5, 7, 9, 14, 21, 32, 46]


for meg,mri in sub_dict.items():
    epo = mne.read_epochs("{}{}-epo.fif".format(proc_dir,meg))
    fwd = mne.read_forward_solution("{}{}-fwd.fif".format(proc_dir,meg))
    # calculate filters for lower freq bands
    csd = mne.time_frequency.read_csd("{}{}-csd.h5".format(proc_dir,meg))
    filters = mne.beamformer.make_dics(epo.info,fwd,csd.mean(fmins,fmaxs),pick_ori='max-power',reduce_rank=False,depth=1.0,inversion='single')
    filters.save('{}{}-new-dics.h5'.format(proc_dir,meg))
