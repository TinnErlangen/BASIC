## PREPARE Forward Model for Mixed Source Space

import mne
import numpy as np
from nilearn import plotting

## remember: BRA52, ((FAO18, WKI71 - excl.)) have fsaverage MRIs (originals were defective)

preproc_dir = "D:/NEMO_analyses_new/preproc/"
trans_dir = "D:/NEMO_analyses_new/trans_files/"
meg_dir = "D:/NEMO_analyses_new/proc/"
mri_dir = "D:/freesurfer/subjects/"
sub_dict = {"NEM_10":"GIZ04","NEM_11":"WOO07","NEM_12":"TGH11","NEM_14":"FIN23","NEM_15":"KIL13",
           "NEM_16":"KIO12","NEM_17":"DEN59","NEM_18":"SAG13","NEM_20":"PAG48","NEM_22":"EAM11",
           "NEM_23":"FOT12","NEM_24":"BII41","NEM_26":"ENR41","NEM_27":"HIU14","NEM_28":"WAL70",
           "NEM_29":"KIL72","NEM_31":"BLE94","NEM_34":"KER27","NEM_35":"MUN79","NEM_36":"BRA52_fa"}  ## order got corrected
excluded = {"NEM_30":"DIU11","NEM_32":"NAG83","NEM_33":"FAO18_fa","NEM_37":"EAM67","NEM_19":"ALC81","NEM_21":"WKI71_fa"}
# sub_dict = {"NEM_11":"WOO07",}

# load the fsaverage source space for computing and saving source morph from subjects
fs_src = mne.read_source_spaces("{}fsaverage_oct6_mix-src.fif".format(meg_dir))

for meg,mri in sub_dict.items():
    # read source space and BEM solution (conductor model) that have been saved
    trans = "{dir}{mri}_{meg}-trans.fif".format(dir=trans_dir,mri=mri,meg=meg)
    src = mne.read_source_spaces("{dir}{meg}_oct6_mix-src.fif".format(dir=meg_dir,meg=meg))
    bem = mne.read_bem_solution("{dir}{meg}-bem.fif".format(dir=meg_dir,meg=meg))
    # load and prepare the MEG data
    rest_info = mne.io.read_info("{dir}{sub}_1-epo.fif".format(dir=preproc_dir,sub=meg))
    ton_info = mne.io.read_info("{dir}{sub}_2-epo.fif".format(dir=preproc_dir,sub=meg))
    epo_a_info = mne.io.read_info("{dir}{sub}_3-epo.fif".format(dir=preproc_dir,sub=meg))
    epo_b_info = mne.io.read_info("{dir}{sub}_4-epo.fif".format(dir=preproc_dir,sub=meg))
    # build forward model from MRI and BEM  - for each experimental block
    fwd_rest = mne.make_forward_solution(rest_info, trans=trans, src=src, bem=bem, meg=True, eeg=False, mindist=5.0, n_jobs=8)
    # mne.write_forward_solution("{dir}{meg}_1-fwd.fif".format(dir=meg_dir,meg=meg),fwd_rest,overwrite=True)
    fwd_ton = mne.make_forward_solution(ton_info, trans=trans, src=src, bem=bem, meg=True, eeg=False, mindist=5.0, n_jobs=8)
    # mne.write_forward_solution("{dir}{meg}_2-fwd.fif".format(dir=meg_dir,meg=meg),fwd_ton,overwrite=True)
    fwd_a = mne.make_forward_solution(epo_a_info, trans=trans, src=src, bem=bem, meg=True, eeg=False, mindist=5.0, n_jobs=8)
    # mne.write_forward_solution("{dir}{meg}_3-fwd.fif".format(dir=meg_dir,meg=meg),fwd_a,overwrite=True)
    fwd_b = mne.make_forward_solution(epo_b_info, trans=trans, src=src, bem=bem, meg=True, eeg=False, mindist=5.0, n_jobs=8)
    # mne.write_forward_solution("{dir}{meg}_4-fwd.fif".format(dir=meg_dir,meg=meg),fwd_b,overwrite=True)
    # build averaged forward model for all blocks/conditions
    fwd = mne.average_forward_solutions([fwd_rest,fwd_ton,fwd_a,fwd_b], weights=None)
    mne.write_forward_solution("{dir}{meg}-fwd.fif".format(dir=meg_dir,meg=meg),fwd,overwrite=True)

    # get info on dipoles and plot (optional)
    leadfield = fwd['sol']['data']
    print("Leadfield size : %d sensors x %d dipoles" % leadfield.shape)
    # mne.viz.plot_alignment(epo_a_info, trans, subject=mri, dig=False, fwd=fwd, src=fwd['src'], eeg=False, subjects_dir=mri_dir, surfaces='white', bem=bem)

    # compute sensitivity map values, and exclude dipoles <0.15

    # compute and save source morph to fsaverage for later group analyses
    morph = mne.compute_source_morph(fwd['src'],subject_from=mri,subject_to="fsaverage",subjects_dir=mri_dir,src_to=fs_src)  ## it's important to use fwd['src'] to account for discarded vertices
    morph.save("{}{}_fs_mix-morph.h5".format(meg_dir,meg))
