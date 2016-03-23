import sys, os
import getpass

test = True

data_type = 'fif'
main_path = '/net/server/data/home/meg/DMALT/aut_rs/'
data_path = os.path.join(main_path,"MEG")
MEG_elec_coords_file = os.path.join(data_path,"correct_channel_coords.txt")
MEG_elec_names_file  = os.path.join(data_path,"correct_channel_names.txt")

l_freq = 0.1
h_freq = 300

is_ICA = True 

subject_ids = ["R0036"]
sessions = ["01"]
### set sbj dir path, i.e. where the FS folfers are
sbj_dir   =  os.path.join(main_path,"FSF")
correl_analysis_name = "aut_rs_pipeline" + "_" + data_type  + "_" + str(epoch_window_length).replace('.','_')


if test == True:
    correl_analysis_name = correl_analysis_name + '_test'
