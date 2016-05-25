def preprocess_ICA_fif_to_ts(fif_file, ECG_ch_name, EoG_ch_name, l_freq, h_freq):
    # ------------------------ Import stuff ------------------------ #
    import os
    import mne
    import sys
    from mne.io import Raw
    from mne.preprocessing import ICA
    from mne.preprocessing import create_ecg_epochs, create_eog_epochs
    from nipype.utils.filemanip import split_filename as split_f
    from reportGen import generateReport
    import pickle

    subj_path, basename, ext = split_f(fif_file)
    # -------------------- Delete later ------------------- #
    subj_name = subj_path[-5:]
    results_dir = subj_path[:-6]
    # results_dir += '2016'
    subj_path = results_dir + '/' + subj_name
    if not os.path.exists(subj_path):
        try:
            os.makedirs(subj_path)
        except OSError:
            sys.stderr.write('ica_preproc: problem creating directory: ' + subj_path)
    ########################################################
    # Read raw
    #   If None the compensation in the data is not modified. If set to n, e.g. 3, apply
    #   gradient compensation of grade n as for CTF systems (compensation=3)
    print(fif_file)
    print(EoG_ch_name)
    #  ----------------------------- end Import stuff ----------------- #
    # EoG_ch_name = "EOG061, EOG062"

    # ------------- Load raw ------------- #
    raw = Raw(fif_file, preload=True)
    # select sensors
    select_sensors = mne.pick_types(raw.info, meg=True, ref_meg=False, exclude='bads')
    picks_meeg = mne.pick_types(raw.info, meg=True, eeg=True, exclude='bads')

    # filtering
    raw.filter(l_freq=l_freq, h_freq=h_freq, picks=picks_meeg, method='iir', n_jobs=1)

    # if ECG_ch_name == 'EMG063':
    if ECG_ch_name in raw.info['ch_names']:
        raw.set_channel_types({ECG_ch_name: 'ecg'})  # Without this files with ECG_ch_name = 'EMG063' fail
        # ECG_ch_name = 'ECG063'
    if EoG_ch_name == 'EMG065,EMG066,EMG067,EMG068':   # Because ica.find_bads_eog... can process max 2 EoG channels
        EoG_ch_name = 'EMG065,EMG067'                 # it won't fail if I specify 4 channels, but it'll use only first
                                                      # EMG065 and EMG066 are for vertical eye movements and
                                                      # EMG067 and EMG068 are for horizontal

    # print rnk
    rnk = 'N/A'
    # 1) Fit ICA model using the FastICA algorithm
    # Other available choices are `infomax` or `extended-infomax`
    # We pass a float value between 0 and 1 to select n_components based on the
    # percentage of variance explained by the PCA components.
    reject = dict(mag=10e-12, grad=10000e-13)
    flat = dict(mag=0.1e-12, grad=1e-13)
    # check if we have an ICA, if yes, we load it
    ica_filename = os.path.join(subj_path, basename + "-ica.fif")
    raw_ica_filename = os.path.join(subj_path, basename + "_ica_raw.fif")
    info_filename = os.path.join(subj_path, basename + "_info.pickle")
    # if os.path.exists(ica_filename) == False:
    ica = ICA(n_components=0.99, method='fastica')  # , max_iter=500
    ica.fit(raw, picks=select_sensors, reject=reject, flat=flat)  # decim = 3,
    # has_ICA = False
    # else:
    #     has_ICA = True
    #     ica = read_ica(ica_filename)
    #     ica.exclude = []
    # ica.labels_ = dict() # to avoid bug; Otherwise it'll throw an exception

    ica_sources_filename = subj_path + '/' + basename + '_ica_timecourse.fif'

    # if not os.path.isfile(ica_sources_filename):
    icaSrc = ica.get_sources(raw, add_channels=None, start=None, stop=None)
    icaSrc.save(ica_sources_filename, picks=None, tmin=0, tmax=None, buffer_size_sec=10,
                drop_small_buffer=False, proj=False, fmt='single', overwrite=True, split_size='2GB', verbose=None)
    icaSrc = None
    # if has_ICA == False:
    # ica.save(ica_filename)
    # return
    # 2) identify bad components by analyzing latent sources.
    # generate ECG epochs use detection via phase statistics

    # check if ECG_ch_name is in the raw channels
    # import ipdb; ipdb.set_trace()
    if ECG_ch_name in raw.info['ch_names']:
        ecg_epochs = create_ecg_epochs(raw, tmin=-.5, tmax=.5, picks=select_sensors, ch_name=ECG_ch_name)
    # if not  a synthetic ECG channel is created from cross channel average
    else:
        ecg_epochs = create_ecg_epochs(raw, tmin=-.5, tmax=.5, picks=select_sensors)
    # ICA for ECG artifact
    # threshold=0.25 come defualt
    ecg_inds, ecg_scores = ica.find_bads_ecg(ecg_epochs, method='ctps', threshold=0.25)
    # if len(ecg_inds) > 0:
    ecg_evoked = ecg_epochs.average()
    ecg_epochs = None    # ecg_epochs use too much memory
    n_max_ecg = 3
    ecg_inds = ecg_inds[:n_max_ecg]
    ica.exclude += ecg_inds
    n_max_eog = 4
    # import pdb; pdb.set_trace()
    if set(EoG_ch_name.split(',')).issubset(set(raw.info['ch_names'])):
        eog_inds, eog_scores = ica.find_bads_eog(raw, ch_name=EoG_ch_name)
        eog_inds = eog_inds[:n_max_eog]
        eog_evoked = create_eog_epochs(raw, tmin=-.5, tmax=.5, picks=select_sensors, ch_name=EoG_ch_name).average()
    else:
        eog_inds = eog_scores = eog_evoked = []
    # ------------------------------------------------------ #
    # This is necessary. Otherwise line
    # will through an exception
    if not eog_inds:
        eog_inds = None
    # ------------------------------------------------------ #
    generateReport(raw=raw, ica=ica, subj_name=subj_name, subj_path=subj_path, basename=basename,
                   ecg_evoked=ecg_evoked, ecg_scores=ecg_scores, ecg_inds=ecg_inds, ECG_ch_name=ECG_ch_name,
                   eog_evoked=eog_evoked, eog_scores=eog_scores, eog_inds=eog_inds, EoG_ch_name=EoG_ch_name)

    sfreq = raw.info['sfreq']
    raw = None  # To save memory
            
    # save ICA solution
    print ica_filename

    # ------------------------- Generate log ------------------------ #
    f = open(subj_path + '/' + basename + '_ica.log', 'w')
    f.write('Data rank after SSS: ' + str(rnk) + '\n')
    f.write('Sampling freq: ' + str(sfreq) + '\n')
    f.write('ECG exclude suggested: ' + str(ecg_inds) + '\n')
    f.write('EOG exclude suggested: ' + str(eog_inds) + '\n')
    f.write('\n')
    f.write('ECG exclude final: ' + str(ecg_inds) + '\n')
    f.write('EOG exclude final: ' + str(eog_inds) + '\n')
    f.write('Muscles exclude: []' + '\n')
    f.close()
    # ------------------------ end generate log ---------------------- #
    with open(info_filename, 'wb') as f:
        pickle.dump(ecg_inds, f)
        pickle.dump(ecg_scores, f)
        pickle.dump(eog_inds, f)
        pickle.dump(eog_scores, f)
    # -------------------- Save ICA solution ------------------------- #
    ica.save(ica_filename)

    return raw_ica_filename, sfreq


if __name__ == '__main__':
    # subj_name = 'R0010'
    # subj_name = 'K0021'
    # subj_name = 'R0035'
    subj_name = 'R0003'
    fif_file = '/net/server/data/home/meg/DMALT/aut_rs/MEG2016/' + subj_name + '/' + subj_name + '_rest_raw_tsss_mc_trans_eo.fif'
    # ECG_ch_name = 'ECG063'
    # ECG_ch_name = 'ECG063'
    ECG_ch_name = 'N/A'
    EoG_ch_name = 'EOG061,EOG062'
    # EoG_ch_name = 'N/A'
    # EoG_ch_name = 'EMG065,EMG067'
    l_freq = 0.1
    h_freq = 300
    ignore_exception = False
    preprocess_ICA_fif_to_ts(fif_file, ECG_ch_name, EoG_ch_name, l_freq, h_freq)

