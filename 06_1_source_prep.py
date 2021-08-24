## PREPARE BEM-Model and Source Space(s) - Surface, Mixed, and/or Volume

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

## prep fsaverage

# build BEM model for fsaverage (as boundary for source space creation) --- only needed for volume or mixed source spaces
bem_model = mne.make_bem_model("fsaverage", subjects_dir=mri_dir, ico=5, conductivity=[0.3])
bem = mne.make_bem_solution(bem_model)
mne.write_bem_solution("{dir}fsaverage-bem.fif".format(dir=meg_dir),bem)
mne.viz.plot_bem(subject="fsaverage", subjects_dir=mri_dir, brain_surfaces='white', orientation='coronal')

# build fs_average mixed 'oct6' surface source space & save (to use as morph target later)
fs_src = mne.setup_source_space("fsaverage", spacing='oct6', surface="white", subjects_dir=mri_dir, n_jobs=6)
# print out the number of spaces and points
n = sum(fs_src[i]['nuse'] for i in range(len(fs_src)))
print('the fs_src space contains %d spaces and %d points' % (len(fs_src), n))
fs_src.plot(subjects_dir=mri_dir)
# save the surface source space
fs_src.save("{}fsaverage_oct6_mix-src.fif".format(meg_dir), overwrite=True)
del fs_src


## prep subjects

for meg,mri in sub_dict.items():

    # build BEM model from MRI, save and plot, along with sensor alignment
    bem_model = mne.make_bem_model(mri, subjects_dir=mri_dir, ico=5, conductivity=[0.3])
    bem = mne.make_bem_solution(bem_model)
    mne.write_bem_solution("{dir}{meg}-bem.fif".format(dir=meg_dir,meg=meg),bem)
    mne.viz.plot_bem(subject=mri, subjects_dir=mri_dir, brain_surfaces='white', orientation='coronal')
    # load trans-file and plot coregistration alignment
    trans = "{dir}{mri}_{meg}-trans.fif".format(dir=trans_dir,mri=mri,meg=meg)
    info = mne.io.read_info("{}{}_3-raw.fif".format(preproc_dir,meg))       # use your -epo.fif here
    mne.viz.plot_alignment(info, trans, subject=mri, dig='fiducials', meg=['helmet', 'sensors'], eeg=False, subjects_dir=mri_dir, surfaces='head-dense', bem=bem)

    # build the surface source space for the subjects, with 'oct6' spacing
    src = mne.setup_source_space(mri, spacing='oct6', surface="white", subjects_dir=mri_dir, n_jobs=8)  ## uses 'oct6' as default, i.e. 4.9mm spacing appr.
    # print number of spaces and points, save
    n = sum(src[i]['nuse'] for i in range(len(src)))
    print('the src space contains %d spaces and %d points' % (len(src), n))
    # save the mixed source space
    src.save("{}{}-oct6-src.fif".format(meg_dir,meg), overwrite=True)
    # plot the source space with points
    src.plot()
    mne.viz.plot_alignment(info, trans, subject=mri, dig='fiducials', meg=['helmet', 'sensors'], eeg=False, subjects_dir=mri_dir, surfaces='head-dense', bem=bem, src=src)
