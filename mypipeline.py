import nipype
print nipype.__version__

import nipype.interfaces.io as nio

from nipype.interfaces.utility import IdentityInterface, Function
import nipype.pipeline.engine as pe
from ica_preproc import preprocess_ICA_fif_to_ts


from params import main_path, data_path
from params import subject_ids, sessions

from params import l_freq, h_freq
from params import correl_analysis_name
# ------------- Dmalt ------------------- #
from table_handling import get_eo_ec_by_name
from split_data import split_fif_into_eo_ec
from table_handling import get_ECG_EOG_chnames_by_SubjID
# ---------------------------------------- #


# basic imports
# import sys,io,os,fnmatch,shutil

import matplotlib
matplotlib.use('PS')

# nibabel import
#import nibabel as nib

# nipype import
#from nipype import config
# config.enable_debug_mode()

import nipype
print nipype.__version__


def create_datasource_fif():

    datasource = pe.Node(interface=nio.DataGrabber(
        infields=['subject_id'], outfields=['fif_file']), name='datasource')
    datasource.inputs.base_directory = data_path
    datasource.inputs.template = '%s/%s%s'
    datasource.inputs.template_args = dict(
        fif_file=[['subject_id', 'subject_id', "_rest_raw_tsss_mc_trans.fif"]]
        # fif_file = [['subject_id', 'subject_id',"_rest_raw_tsss_mc.fif"]]
    )
    datasource.inputs.sort_filelist = True
    return datasource


def create_infosource_correct_ampl_by_band():

    from params import test
    print test
    infosource = pe.Node(interface=IdentityInterface(
        fields=['subject_id', 'sess_index']), name="infosource")

    if test == False:
        infosource.iterables = [
            ('subject_id', subject_ids), ('sess_index', sessions)]

    else:
        # test
        # test
        infosource.iterables = [('subject_id', subject_ids),  # ['K0002', 'K0002']
                                # ['balai','benba','casla','doble']
                                ('sess_index', ['01'])]   # ['01', '12']

    return infosource


def create_main_workflow_spectral_modularity():

    main_workflow = pe.Workflow(name=correl_analysis_name)
    main_workflow.base_dir = main_path

    print "main_path %s" % main_path

    # Info source
    infosource = create_infosource_correct_ampl_by_band()

    # Data source
    datasource = create_datasource_fif()
    main_workflow.connect(infosource, 'subject_id', datasource, 'subject_id')

    # preprocess
### ----------------------------- eo_ec_times node -----------------------------###
    eo_ec_times = pe.Node(interface=Function(input_names=["Subj_ID", "cond"], output_names=[
                          "lCondStart", "lCondEnd", "first_samp", "cond"], function=get_eo_ec_by_name), name="extract_eo_ec_times")
    eo_ec_times.iterables = ("cond", ["eo", "ec"])
    ECG_EOG_ch_names = pe.Node(interface=Function(input_names=["Subj_ID"], output_names=[
                               "ECG_name", "EOG_names"], function=get_ECG_EOG_chnames_by_SubjID), name='extract_ECG_EOG_ch_names')
    main_workflow.connect(infosource, "subject_id", eo_ec_times, "Subj_ID")
    main_workflow.connect(infosource, "subject_id",
                          ECG_EOG_ch_names, "Subj_ID")
#---------------------------------------------------------------------------------#

###--------------------- eo_ec_split node ---------------------------------------###
    eo_ec_split = pe.Node(interface=Function(input_names=["fif_file", "lCondStart", "lCondEnd", "first_samp", "cond"],
                                             output_names=["eo_ec_split_fif"],
                                             function=split_fif_into_eo_ec),
                          name="eo_ec_split")

    main_workflow.connect(datasource, 'fif_file', eo_ec_split, 'fif_file')
    main_workflow.connect(eo_ec_times, 'lCondStart', eo_ec_split, 'lCondStart')
    main_workflow.connect(eo_ec_times, 'lCondEnd', eo_ec_split, 'lCondEnd')
    main_workflow.connect(eo_ec_times, 'cond', eo_ec_split, 'cond')
    main_workflow.connect(eo_ec_times, 'first_samp', eo_ec_split, 'first_samp')
#----------------------------- end of eo_ec_split node --------------------------------------#

### ------------------------ preproc node ---------------------------------------#

    preproc = pe.Node(interface=Function(input_names=["fif_file", 'ECG_ch_name', 'EoG_ch_name', 'l_freq', 'h_freq'],
                                         # output_names =["raw_ica_filename", "ts_file","channel_coords_file","channel_names_file","sfreq"],
                                         output_names=[
        "raw_ica_filename", "sfreq"],
        function=preprocess_ICA_fif_to_ts), name='preproc')

    preproc.inputs.is_sensor_space = True

    preproc.inputs.l_freq = l_freq
    preproc.inputs.h_freq = h_freq

    main_workflow.connect(ECG_EOG_ch_names, "ECG_name", preproc, "ECG_ch_name")
    main_workflow.connect(ECG_EOG_ch_names, "EOG_names",
                          preproc, "EoG_ch_name")
    main_workflow.connect(eo_ec_split, 'eo_ec_split_fif', preproc, 'fif_file')

    # main_workflow.connect(datasource, 'fif_file',preproc, 'fif_file')

    return main_workflow

if __name__ == '__main__':

    # run pipeline:
    main_workflow = create_main_workflow_spectral_modularity()

    # run

    # main_workflow.write_graph(graph2use='colored')
    main_workflow.config['execution'] = {'remove_unnecessary_outputs': 'false'}
    main_workflow.run(plugin='MultiProc', plugin_args={'n_procs': 2})
