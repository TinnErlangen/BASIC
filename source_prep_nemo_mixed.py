## PREPARE BEM-Model and Source Space(s) - Surface, Mixed, and/or Volume

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
# sub_dict = {"NEM_26":"ENR41"}

## prep fsaverage

# build BEM model for fsaverage (as boundary for source space creation)
bem_model = mne.make_bem_model("fsaverage", subjects_dir=mri_dir, ico=5, conductivity=[0.3])
bem = mne.make_bem_solution(bem_model)
mne.write_bem_solution("{dir}fsaverage-bem.fif".format(dir=meg_dir),bem)
mne.viz.plot_bem(subject="fsaverage", subjects_dir=mri_dir, brain_surfaces='white', orientation='coronal')

# build fs_average mixed 'oct6' with limbic source space & save (to use as morph target later)
labels_limb = ['Left-Thalamus-Proper','Left-Caudate','Left-Putamen','Left-Pallidum','Left-Hippocampus','Left-Amygdala',
              'Right-Thalamus-Proper','Right-Caudate','Right-Putamen','Right-Pallidum','Right-Hippocampus','Right-Amygdala']
fs_src = mne.setup_source_space("fsaverage", spacing='oct6', surface="white", subjects_dir=mri_dir, n_jobs=6)
fs_limb_src = mne.setup_volume_source_space("fsaverage", mri="aseg.mgz", pos=5.0, bem=bem, volume_label=labels_limb, subjects_dir=mri_dir,add_interpolator=True,verbose=True)
fs_src += fs_limb_src
# print out the number of spaces and points
n = sum(fs_src[i]['nuse'] for i in range(len(fs_src)))
print('the fs_src space contains %d spaces and %d points' % (len(fs_src), n))
fs_src.plot(subjects_dir=mri_dir)
# save the mixed source space
fs_src.save("{}fsaverage_oct6_mix-src.fif".format(meg_dir), overwrite=True)
del fs_src
# create another volume source space, with limbic structures as single volume (for later cluster stats)
fs_limb_vol = mne.setup_volume_source_space("fsaverage", mri="aseg.mgz", pos=5.0, bem=bem, volume_label=labels_limb, subjects_dir=mri_dir, add_interpolator=True, single_volume=True, verbose=True)
fs_limb_vol.save("{}fsaverage_limb-src.fif".format(meg_dir), overwrite=True)
## prep subjects

labels_limb = ['Left-Thalamus-Proper','Left-Caudate','Left-Putamen','Left-Pallidum','Left-Hippocampus','Left-Amygdala',
              'Right-Thalamus-Proper','Right-Caudate','Right-Putamen','Right-Pallidum','Right-Hippocampus','Right-Amygdala']

for meg,mri in sub_dict.items():

    # build BEM model from MRI, save and plot, along with sensor alignment
    bem_model = mne.make_bem_model(mri, subjects_dir=mri_dir, ico=5, conductivity=[0.3])
    bem = mne.make_bem_solution(bem_model)
    mne.write_bem_solution("{dir}{meg}-bem.fif".format(dir=meg_dir,meg=meg),bem)
    mne.viz.plot_bem(subject=mri, subjects_dir=mri_dir, brain_surfaces='white', orientation='coronal')
    # load trans-file and plot coregistration alignment (for run 3)
    trans = "{dir}{mri}_{meg}-trans.fif".format(dir=trans_dir,mri=mri,meg=meg)
    info = mne.io.read_info("{}{}_3-epo.fif".format(preproc_dir,meg))
    mne.viz.plot_alignment(info, trans, subject=mri, dig='fiducials', meg=['helmet', 'sensors'], eeg=False, subjects_dir=mri_dir, surfaces='head-dense', bem=bem)

    # build the mixed source spaces for the subjects, combining 'oct6' surface spaces with volume spaces of selected limbic structures
    src = mne.setup_source_space(mri, spacing='oct6', surface="white", subjects_dir=mri_dir, n_jobs=8)  ## uses 'oct6' as default, i.e. 4.9mm spacing appr.
    limb_src = mne.setup_volume_source_space(mri, mri="aseg.mgz", pos=5.0, bem=bem, volume_label=labels_limb, subjects_dir=mri_dir,add_interpolator=True,verbose=True)
    src += limb_src
    # print number of spaces and points, save
    n = sum(src[i]['nuse'] for i in range(len(src)))
    print('the src space contains %d spaces and %d points' % (len(src), n))
    # save the mixed source space
    src.save("{}{}_oct6_mix-src.fif".format(meg_dir,meg), overwrite=True)
    # save as nifti and plot
    nii_fname = "{}{}-mixed-src.nii".format(meg_dir,meg)
    src.export_volume(nii_fname, mri_resolution=True, overwrite=True)
    plotting.plot_img(nii_fname, cmap='nipy_spectral')
    plotting.show()
    del src



# plot alignment again with forward :) - will show dipole orientations
