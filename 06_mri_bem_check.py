import mne


# setup freesurfer subjects directory
subj_dir = "/home/cora/freesurfer/subjects/"

# list of subjects to be processed
subjs = ["ARG62","BAE51","BEL67","BEU80","BHH31","CUI27","DAP32","ECN26","EEC27","EIP04",
         "ELL12","ENC34","EON82","GAG65","GIR89","HAI64","HAL50","HHH42","LAF32","MAM73",
         "MAU06","NAL22","NAO26","NEB26","NIC98","NIP84","NLF76","NNE17","NOR76","OEE52",
         "RLL12","RTB16","RWB50","SAN53","SON62","UVC22","WAI40","WAM42","ZIT18"]
# subjs = ["CUI27","RWB50","SAN53"]
# subjs = ["CUI27"]

for sub in subjs:
    mne.viz.plot_bem(subject=sub, subjects_dir=subj_dir, brain_surfaces='white', orientation='coronal')



# SUMMARY:
# OK = ["ARG62","BAE51","BEL67","BEU80","BHH31","DAP32","ECN26","EEC27","EIP04",
#       "ELL12","ENC34","EON82","GAG65","GIR89","HAI64","HAL50","HHH42","LAF32","MAM73",
#       "MAU06","NAL22","NAO26","NEB26","NIC98","NIP84","NLF76","NNE17","NOR76","OEE52",
#       "RLL12","RTB16","SON62","UVC22","WAI40","WAM42","ZIT18"]
# unsure_careful = ["RWB50","SAN53"]
# careful = {"RWB50":"CAT_07","SAN53":("CAT_11","TSM_03","akut")}
# BAD = ["CUI27"]
# bad = {"CUI27":"CEM_15"}
