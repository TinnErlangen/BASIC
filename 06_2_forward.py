## PREPARE Forward Model for Mixed Source Space

import mne
import numpy as np
from nilearn import plotting

## remember: BRA52, ((FAO18, WKI71 - excl.)) have fsaverage MRIs (originals were defective)

preproc_dir = "G:/TSM_test/NEM_proc/"
trans_dir = "G:/TSM_test/NEM_proc/" # enter your special trans file folder here
meg_dir = "G:/TSM_test/NEM_proc/"
mri_dir = "G:/freesurfer/subjects/"
sub_dict = {"NEM_14":"FIN23"}
# sub_dict = {"NEM_26":"ENR41"}

# load the fsaverage source space for computing and saving source morph from subjects
fs_src = mne.read_source_spaces("{}fsaverage_oct6_mix-src.fif".format(meg_dir))

for meg,mri in sub_dict.items():
    # read source space and BEM solution (conductor model) that have been saved
    trans = "{dir}{mri}_{meg}-trans.fif".format(dir=trans_dir,mri=mri,meg=meg)
    src = mne.read_source_spaces("{dir}{meg}-oct6-src.fif".format(dir=meg_dir,meg=meg))
    bem = mne.read_bem_solution("{dir}{meg}-bem.fif".format(dir=meg_dir,meg=meg))
    # load and prepare the MEG data
    epo_info = mne.io.read_info("{dir}{sub}_3-raw.fif".format(dir=preproc_dir,sub=meg))     # use your -epo.fif file
    # build forward model from MRI and BEM  - for each experimental block
    fwd = mne.make_forward_solution(epo_info, trans=trans, src=src, bem=bem, meg=True, eeg=False, mindist=3.0, n_jobs=8)
    # # build averaged forward model for all blocks/conditions
    # fwd = mne.average_forward_solutions([fwd_2,fwd_4], weights=None)     # in case you need to average forwards from several runs
    mne.write_forward_solution("{dir}{meg}-fwd.fif".format(dir=meg_dir,meg=meg),fwd,overwrite=True)

    # get info on dipoles and plot (optional)
    leadfield = fwd['sol']['data']
    print("Leadfield size : %d sensors x %d dipoles" % leadfield.shape)
    mne.viz.plot_alignment(epo_info, trans, subject=mri, dig=False, fwd=fwd, src=fwd['src'], eeg=False, subjects_dir=mri_dir, surfaces='white', bem=bem)

    # compute and save source morph to fsaverage for later group analyses
    morph = mne.compute_source_morph(fwd['src'],subject_from=mri,subject_to="fsaverage",subjects_dir=mri_dir,src_to=fs_src)  ## it's important to use fwd['src'] to account for discarded vertices
    morph.save("{}{}_fs-morph.h5".format(meg_dir,meg))
