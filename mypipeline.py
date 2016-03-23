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
    



import nipype
print nipype.__version__

import nipype.interfaces.io as nio

from nipype.interfaces.utility import IdentityInterface,Function
import nipype.pipeline.engine as pe

def create_datasource_fif():
    
    datasource = pe.Node(interface=nio.DataGrabber(infields=['subject_id'],outfields=['fif_file']),name = 'datasource')
    datasource.inputs.base_directory = data_path
    datasource.inputs.template = '%s/%s%s'
    datasource.inputs.template_args = dict(
        fif_file = [['subject_id', 'subject_id',"_rest_raw_tsss_mc_trans.fif"]]
        )
    datasource.inputs.sort_filelist = True
    return datasource

def create_infosource_correct_ampl_by_band():

    from params import test
    print test
    infosource = pe.Node(interface=IdentityInterface(fields=['subject_id', 'sess_index']),name="infosource")
    
    if test == False:
        infosource.iterables = [('subject_id', subject_ids),('sess_index',sessions)]

    else:
        ### test 
        ### test 
        infosource.iterables = [('subject_id',  subject_ids), # ['K0002', 'K0002']
                                                                                    # ['balai','benba','casla','doble']
                                ('sess_index', ['01'])]   # ['01', '12']           
                                

    return infosource

def create_main_workflow_spectral_modularity():
    
    main_workflow = pe.Workflow(name=correl_analysis_name)
    main_workflow.base_dir = main_path
    
    print "main_path %s" % main_path
    
    ## Info source
    infosource = create_infosource_correct_ampl_by_band()
    
    ## Data source
    datasource = create_datasource_fif()
    main_workflow.connect(infosource, 'subject_id', datasource, 'subject_id') 
           
    
    #### preprocess
### ----------------------------- eo_ec_times node -----------------------------###
    eo_ec_times = pe.Node(interface=Function(input_names=["Subj_ID", "cond"], output_names=["lCondStart", "lCondEnd", "first_samp", "cond"], function=get_eo_ec_by_name), name="extract_eo_ec_times")
    eo_ec_times.iterables=("cond", ["eo", "ec"])
    ECG_EOG_ch_names = pe.Node(interface=Function(input_names=["Subj_ID"], output_names=["ECG_name", "EOG_names"], function=get_ECG_EOG_chnames_by_SubjID), name='extract_ECG_EOG_ch_names')
    main_workflow.connect(infosource, "subject_id", eo_ec_times, "Subj_ID")
    main_workflow.connect(infosource, "subject_id", ECG_EOG_ch_names, "Subj_ID")
#---------------------------------------------------------------------------------#

###--------------------- eo_ec_split node ---------------------------------------###
    eo_ec_split = pe.Node(interface=Function(input_names=["fif_file", "lCondStart", "lCondEnd", "first_samp","cond"],
                                             output_names=["eo_ec_split_fif"],
                                             function=split_fif_into_eo_ec),
                          name="eo_ec_split")

    #main_workflow.connect(datasource, 'fif_file', eo_ec_split, 'fif_file')
    main_workflow.connect(eo_ec_times, 'lCondStart', eo_ec_split, 'lCondStart')
    main_workflow.connect(eo_ec_times, 'lCondEnd', eo_ec_split, 'lCondEnd')
    main_workflow.connect(eo_ec_times, 'cond', eo_ec_split, 'cond')
    main_workflow.connect(eo_ec_times, 'first_samp', eo_ec_split, 'first_samp')
#----------------------------- end of eo_ec_split node --------------------------------------#

### ------------------------ preproc node ---------------------------------------#
    if is_ICA:
        if is_set_ICA_components:
            preproc = pe.Node(interface = Function(input_names = ["fif_file", 'n_comp_exclude', 'l_freq', 'h_freq', 'down_sfreq',
                                                                  'is_sensor_space'], 
                                               output_names =["ts_file","channel_coords_file","channel_names_file","sfreq"],
                                               function = preprocess_set_ICA_comp_fif_to_ts),name = 'preproc')                                            
            preproc.inputs.n_comp_exclude = n_comp_exclude
        else:
           preproc = pe.Node(interface = Function(input_names = ["fif_file", 'ECG_ch_name', 'EoG_ch_name','l_freq', 'h_freq', 'down_sfreq', 
                                                                 'is_sensor_space'], 
                                               # output_names =["raw_ica_filename", "ts_file","channel_coords_file","channel_names_file","sfreq"],
                                               output_names =["raw_ica_filename", "channel_coords_file","channel_names_file","sfreq"],
                                               function = preprocess_ICA_fif_to_ts), name = 'preproc')
           # Names of channels are now extracted from Aut_gamma_EO_EC_timing.xls table
           # preproc.inputs.ECG_ch_name = ECG_ch_name
           # preproc.inputs.EoG_ch_name = EoG_ch_name
       
        preproc.inputs.is_sensor_space = True
    else:
        preproc = pe.Node(interface = Function(input_names = ["fif_file", 'l_freq', 'h_freq', 'down_sfreq'], 
                                               output_names =["ts_file","channel_coords_file","channel_names_file","sfreq"],
                                               function = preprocess_fif_to_ts),name = 'preproc')

    # main_workflow.connect(eo_ec_split, 'Raw_ec_name', fif_to_ts, "fif_file")
    preproc.inputs.l_freq = l_freq
    preproc.inputs.h_freq = h_freq
    preproc.inputs.down_sfreq = down_sfreq
    
    main_workflow.connect(ECG_EOG_ch_names, "ECG_name", preproc, "ECG_ch_name")
    main_workflow.connect(ECG_EOG_ch_names, "EOG_names", preproc, "EoG_ch_name")
    main_workflow.connect(preproc, 'raw_ica_filename', eo_ec_split, 'fif_file')


    main_workflow.connect(datasource, 'fif_file',preproc, 'fif_file')
     
    return main_workflow

if __name__ == '__main__':
	main()