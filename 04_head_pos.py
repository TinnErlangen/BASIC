# this script is part of step 4 - epoching; it checks how much the head position of subjects changed between runs &
# gives out a warning for the subjects whose head moved more than 5mm --> check terminal output for that warning!
# produces plots for each subject, showing head position for all runs color coded in two coordinate systems
# use this to identify problematic subjects, for which appending runs could produce bad results, esp. for source localization
import mne
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import distance_matrix
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# define your processing directory, subject list and runs
proc_dir = "D:/XXX_analyses/proc/"
subjs = ["XXX_01","XXX_02",]
runs = ["1","2","3","4"]    # adjust
plot = True

# colors are defined for plotting the head position in different runs; adjust number to your count of runs;
# tuples contain RGB values, e.g. (1,0,0) denotes "red"; adjust to your liking
colors = [(1,0,0),(0,1,1),(0,1,0),(0,0,1)]

pos = np.zeros((len(subjs),len(runs),3))
plane_norms = np.zeros((len(subjs),len(runs),3))
dist_mat = np.zeros((len(subjs),len(runs),len(runs)))
cos_mat = np.zeros((len(subjs),len(runs),len(runs)))
for sub_idx,sub in enumerate(subjs):
    if plot:
        fig = plt.figure()
        pos_ax = fig.add_subplot(1,2,1,projection="3d")
        pos_ax.set_xlim((-0.005,0.005))
        pos_ax.set_ylim((-0.005,0.005))
        pos_ax.set_zlim((-0.005,0.005))
        rot_ax = fig.add_subplot(1,2,2,projection="3d")
        rot_ax.set_xlim((-1,1))
        rot_ax.set_ylim((-1,1))
        rot_ax.set_zlim((-1,1))
    for run_idx,run in enumerate(runs):
        epo_name = "{dir}{sub}_{run}_ica-epo.fif".format(dir=proc_dir,
                                                             sub=sub, run=run)
        epo = mne.read_epochs(epo_name)
        dev_head_t = epo.info["dev_head_t"]
        head_dev_t = mne.transforms.invert_transform(dev_head_t)
        # distance
        pos[sub_idx,run_idx] = mne.transforms.apply_trans(dev_head_t,
                                                          np.array([0,0,0]))
        # angle
        fid_points = np.array([epo.info["dig"][idx]["r"] for idx in range(3)])
        fid_points_dev = mne.transforms.apply_trans(head_dev_t,fid_points)
        plane_norms[sub_idx,run_idx] = np.cross(fid_points_dev[0,]-fid_points_dev[1,],
                                                fid_points_dev[2,]-fid_points_dev[1,])
        plane_norms[sub_idx,run_idx] /= np.linalg.norm(plane_norms[sub_idx,run_idx])
        if plot:
            rot_ax.quiver(0,0,0,*plane_norms[sub_idx,run_idx],alpha=0.2,
                          color=colors[run_idx])
    if plot:
        pos_centred = pos[sub_idx,] - np.mean(pos[sub_idx,],axis=0)
        pos_ax.scatter(pos_centred[:,0],pos_centred[:,1],zs=pos_centred[:,2],
                       c=colors,alpha=0.2)

    dist_mat[sub_idx,] = distance_matrix(pos[sub_idx,],pos[sub_idx,])
    cos_mat[sub_idx,] = cosine_similarity(plane_norms[sub_idx,])
    if np.max(dist_mat[sub_idx,]>0.005):
        print("Warning: Subject {} produced a distance of more than 5mm".
              format(sub,run))
plt.show()
