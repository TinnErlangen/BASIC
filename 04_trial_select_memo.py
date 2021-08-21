import mne
import numpy as np
import random

# setup directories
beh_dir = "C:/Users/kimca/Documents/MEMO_analyses_BA/behav/"
proc_dir = "C:/Users/kimca/Documents/MEMO_analyses_BA/proc/"

# subjects list
subjs = ["MEM_14","MEM_13","MEM_03","MEM_05","MEM_04","MEM_02","MEM_15","MEM_01",
         "MEM_12","MEM_07","MEM_09","MEM_06"]
nonill_subjs = ["MEM_08","MEM_10","MEM_11"]
subjs = ["MEM_01","MEM_02","MEM_03"]

# dictionaries needed to read and write old/new conditions/triggers for epochs
tone_id = {'4000_b': 120, '7000_b': 140, '5500_b': 160, '8500_b': 180}
trig_id = {v: k for k,v in tone_id.items()}
event_id = {'4000_b/cont/sure': 121, '4000_b/cont/unsure': 122,'4000_b/break/unsure': 123, '4000_b/break/sure': 124,
            '7000_b/cont/sure': 141, '7000_b/cont/unsure': 142,'7000_b/break/unsure': 143, '7000_b/break/sure': 144,
            '5500_b/cont/sure': 161, '5500_b/cont/unsure': 162,'5500_b/break/unsure': 163, '5500_b/break/sure': 164,
            '8500_b/cont/sure': 181, '8500_b/cont/unsure': 182,'8500_b/break/unsure': 183, '8500_b/break/sure': 184}

for sub in subjs:
    # load the epoched data
    epo = mne.read_epochs("{}{}_3-epo.fif".format(proc_dir,sub))
    # load the ratings.txt and collect the ratings for target trials (break sounds only)
    beh_trials = []
    with open("{}MEMO_{}.txt".format(beh_dir,sub[-2:]),"r") as file:
        lines = file.readlines()
        del lines[:4]    # delete the header line "Subject recorded...", column headings, and 2 practice trials (!)
        x_lines = [l.split() for l in lines]    # get "words" as list per line
        for l in x_lines:
            beh_trials.append((l[1],l[3]))      # collect trigger and rating as tuple
    # then look into epoch drop log (containing all original trials) to delete dropped epochs from beh_trials
    # for this, you need some tricks:
    droplog = np.array([len(x) for x in epo.drop_log])
    drop_ixs = list(np.where(droplog != 0) [0])
    new_beh_trials = [x for (i,x) in enumerate(beh_trials) if i not in drop_ixs]
    # then check that n_epochs and n_beh_trials match
    if len(epo) != len(new_beh_trials):
        print("\n\n\nWARNING! Epochs and Ratings do not match! Check for error!\n\n\n")
    # to get the ratings into the epoch labels, we have to build a new epochs file
    # from rewriting the event triggers and providing a new event_id dictionary (see event_id at the top)
    # we first need to extraxt the events array and make a list for looping:
    events = list(epos.events)
    for ev,rat in zip(events,new_beh_trials):
        # check that triggers match, then add the rating value to the trigger value to yield the new event id
        if int(rat[0]) == ev[-1]:
            ev[-1] = ev[-1] + int(rat[1])
    events = np.array(events)
    # now we gotta load the -ica-raw.fif once more, to make a new epochs object
    raw = mne.io.Raw("{}{}_3_ica-raw.fif".format(proc_dir,sub))
    # make sure to use the exact epoching parameters like in the other script (baseline etc.) !!!
    new_epo = mne.Epochs(raw,events,event_id=event_id,baseline=(-0.1,0),tmin=-0.1,tmax=5,picks=['meg'])
    # then, copy the epochs, and select them into 30 break (all sure, then random unsure) and 30 cont (all sure, then random unsure)
    sel_epo = new_epo.copy()

    # get "sures" in each category and their numbers
    b_sures = sel_epo["break/sure"]
    n_b_sures = len(b_sures)
    c_sures = sel_epo["cont/sure"]
    n_c_sures = len(c_sures)
    # then get "unsures" and how many are needed to fill up 30, then randomly select
    b_unsures = sel_epo["break/unsure"]
    n_b_rest = 30 - n_b_sures
    # b_rest = random.sample(b_unsures,n_b_rest)  # see if random.sample works with epochs; it does with lists...
    # if it doesn't work, get a list of indices to drop (! n_b_drop = len(b_unsures) - n_b_rest), and drop them from b_unsures
    # to yield b_rest

    c_unsures = sel_epo["cont/unsure"]
    n_c_rest = 30 - n_c_sures
    c_rest = random.sample(c_unsures,n_c_rest)

    # then concatenate epochs to analysis set
    sel_epo = mne.concatenate_epochs(b_sures,b_rest,c_sures,c_rest)
    sel_epo.save("{}{}-analysis-epo.fif".format(proc_dir,sub))
