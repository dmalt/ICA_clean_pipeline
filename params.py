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

# subject_ids = ["K0003"]
# subject_ids = ["K0021"]
subject_ids=[
"K0004", "K0010", "K0015", "K0020", "K0025", "K0030", "K0035", "K0040", "K0051", "K1010", "K1015", "K1020", "R0003", "R0008", "R0013", "R0018", "R0024", "R0029", "R0035", "R0040", "R0051", "R0062", 
"K0005", "K0011", "K0016", "K0021", "K0026", "K0031", "K0036", "K0041", "K1011", "K1016", "K1021", "R0004", "R0009", "R0014", "R0020", "R0025", "R0030", "R0036", "R0046", "R0052",  
"K0001", "K0006", "K0012", "K0017", "K0022", "K0027", "K0032", "K0037", "K0042", "K1012", "K1017", "R0005", "R0010", "R0015", "R0021", "R0026", "R0032", "R0037", "R0047", "R0055",  
"K0002", "K0008", "K0013", "K0018", "K0023", "K0028", "K0033", "K0038", "K0049", "K1013", "K1018", "R0001", "R0006", "R0011", "R0016", "R0022", "R0027", "R0033", "R0038", "R0049", "R0056",  
"K0003", "K0009", "K0014", "K0019", "K0024", "K0029", "K0034", "K0039", "K0050", "K1014", "K1019", "R0002", "R0007", "R0012", "R0017", "R0023", "R0028", "R0034", "R0039", "R0050", "R0060",  ]
sessions = ["01"]
### set sbj dir path, i.e. where the FS folfers are
sbj_dir   =  os.path.join(main_path,"FSF")
# correl_analysis_name = "mypipeline" + "_" + data_type  + "_" + str(epoch_window_length).replace('.','_')
correl_analysis_name = "mypipeline"


if test == True:
    correl_analysis_name = correl_analysis_name + '_test'
