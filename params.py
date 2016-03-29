import sys, os
import getpass

test = True

data_type = 'fif'
main_path = '/net/server/data/home/meg/DMALT/aut_rs/'
data_path = os.path.join(main_path,"MEG")
MEG_elec_coords_file = os.path.join(data_path, "correct_channel_coords.txt")
MEG_elec_names_file  = os.path.join(data_path, "correct_channel_names.txt")

l_freq = 0.1
h_freq = 300

is_ICA = True 

# subject_ids = ["K0003"]
# subject_ids = ["K0021"]
subject_ids_all = [
"K0001", "K0002", "K0003", "K0004", "K0005", "K0006",          "K0008", "K0009", "K0010",
"K0011", "K0012", "K0013", "K0014", "K0015", "K0016", "K0017", "K0018", "K0019", "K0020",
"K0021", "K0022", "K0023", "K0024", "K0025", "K0026", "K0027", "K0028", "K0029", "K0030",
"K0031", "K0032", "K0033", "K0034", "K0035", "K0036", "K0037", "K0038", "K0039", "K0040",
"K0041", "K0042", "K0043", "K0044", "K0045", "K0046", "K0047", "K0048", "K0049", "K0050", 
"K0051",
"K1010", "K1011", "K1012", "K1013", "K1014", "K1015", "K1017", "K1018", "K1019", "K1020",
"K1021",
"R0001", "R0002", "R0003", "R0004", "R0005", "R0006", "R0007", "R0008", "R0009", "R0010",
"R0011", "R0012",          "R0014", "R0015", "R0016", "R0017", "R0018",          "R0020",
"R0021", "R0022", "R0023", "R0024", "R0025", "R0026", "R0027", "R0028", "R0029", "R0030",
"R0031", "R0032", "R0033", "R0034", "R0035", "R0036", "R0037", "R0038", "R0039", "R0040",
         "R0042",          "R0044", "R0046", "R0047",                   "R0049", "R0050",
"R0051", "R0052",                   "R0055", "R0056",                            "R0060",
"R0061", "R0062"
]
# subject_ids_all = ['K0021']
# subject_ids_all = ['R0012']
sessions = ["01"]

subject_ids_exclude_perm = ['K0009', 'K0023', 'R0025', 'R0027', 'R0013', 'R0049']

subject_ids_exclude_temp = ['K0014', 'K0020', 'K0002', 'K1010',
                            'R0030', 'R0037', 'R0047', 'K0033',
                            'R0050', 'K0001', 'R0032', 'K0008',
                            'K1016', 'R0002', 'K0043', 'K0044',
                            'K0045', 'K0046', 'K0047', 'K0048', 
                            'R0031', 'R0061', 'R0042', 'R0044', 
                            'R0046', 'R0005', 'R0004', 'K0017',
                            'R0006', 'R0026', 'R0003', 'K0004',
                            'K0003', 'K0006', 'K0039', 'R0007']

subject_ids = [x for x in subject_ids_all if x not in subject_ids_exclude_perm or x not in subject_ids_exclude_temp]
### set sbj dir path, i.e. where the FS folfers are
sbj_dir   =  os.path.join(main_path, "FSF")
# correl_analysis_name = "mypipeline" + "_" + data_type  + "_" + str(epoch_window_length).replace('.','_')
correl_analysis_name = "mypipeline"


if test == True:
    correl_analysis_name = correl_analysis_name + '_test'
