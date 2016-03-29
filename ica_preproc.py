def preprocess_ICA_fif_to_ts(fif_file, ECG_ch_name, EoG_ch_name, l_freq, h_freq):
    # ------------------------ Import stuff ------------------------ #
    import os
    import numpy as np
    import mne
    from mne.io import Raw	
    from mne.preprocessing import ICA, read_ica
    from mne.preprocessing import create_ecg_epochs, create_eog_epochs
    from mne.report import Report
    from nipype.utils.filemanip import split_filename as split_f
    
    report = Report()

    subj_path,basename,ext = split_f(fif_file)
    ##################### Delete later #####################
    subj_name = subj_path[-5:]
    results_dir = subj_path[:-6]
    results_dir += '2016'
    subj_path = results_dir + '/' + subj_name
    if not os.path.exists(subj_path):
        os.makedirs(subj_path)
    ########################################################
    ### Read raw
    #   If None the compensation in the data is not modified. If set to n, e.g. 3, apply   
    #   gradient compensation of grade n as for CTF systems (compensation=3)
    print(fif_file)
    print(EoG_ch_name)
    #  ----------------------------- end Import stuff ----------------- #
    # EoG_ch_name = "EOG061, EOG062"

    # ------------- Load raw ------------- #
    raw = Raw(fif_file, preload=True)
    ### select sensors                                         
    select_sensors = mne.pick_types(raw.info, meg=True, ref_meg= False, exclude='bads')
    picks_meeg     = mne.pick_types(raw.info, meg=True, eeg=True, exclude='bads')
 
    ### filtering 
    raw.filter(l_freq = l_freq, h_freq = h_freq, picks = picks_meeg, method='iir', n_jobs=1)

    # if ECG_ch_name == 'EMG063':
    raw.set_channel_types({ECG_ch_name: 'ecg'})  # Without this files with ECG_ch_name = 'EMG063' fail                                     
        # ECG_ch_name = 'ECG063'
    if EoG_ch_name =='EMG065,EMG066,EMG067,EMG068':   # Because ica.find_bads_eog... can process max 2 EoG channels
        EoG_ch_name = 'EMG065,EMG067'                 # it won't fail if I specify 4 channels, but it'll use only first
                                                      # EMG065 and EMG066 are for vertical eye movements and 
                                                      # EMG067 and EMG068 are for horizontal
    
    #print rnk
    rnk = 'N/A'


    ### 1) Fit ICA model using the FastICA algorithm
    # Other available choices are `infomax` or `extended-infomax`
    # We pass a float value between 0 and 1 to select n_components based on the
    # percentage of variance explained by the PCA components.
    ICA_title = 'Sources related to %s artifacts (red)'
    is_show = False # visualization
    reject = dict(mag=10e-12, grad=10000e-13)
    flat = dict(mag=0.1e-12, grad=1e-13)
    # check if we have an ICA, if yes, we load it
    ica_filename = os.path.join(subj_path, basename + "-ica.fif")  
    raw_ica_filename = os.path.join(subj_path, basename + "_ica_raw.fif")  
    # if os.path.exists(ica_filename) == False:
    ica = ICA(n_components=0.99, method='fastica') # , max_iter=500
    ica.fit(raw, picks=select_sensors, reject=reject, flat=flat) # decim = 3, 
    # has_ICA = False
    # else:
    #     has_ICA = True
    #     ica = read_ica(ica_filename)
    #     ica.exclude = []
    #     ica.labels_ = dict() # to avoid bug; Otherwise it'll throw an exception

    ica_sources_filename = subj_path + '/' + basename + '_ica_timecourse.fif'

    # if not os.path.isfile(ica_sources_filename):
    icaSrc = ica.get_sources(raw, add_channels=None, start=None, stop=None)
    icaSrc.save(ica_sources_filename, picks=None, tmin=0, tmax=None, buffer_size_sec=10,
                drop_small_buffer=False, proj=False, fmt='single', overwrite=True, split_size='2GB', verbose=None)
    icaSrc = None
    # if has_ICA == False:
    #     ica.save(ica_filename)
    # return
    ### 2) identify bad components by analyzing latent sources.
    # generate ECG epochs use detection via phase statistics
    
    n_max_eog = 4
    
    # check if ECG_ch_name is in the raw channels
    if ECG_ch_name in raw.info['ch_names']:
        ecg_epochs = create_ecg_epochs(raw, tmin=-.5, tmax=.5, picks=select_sensors, ch_name=ECG_ch_name)
    # if not  a synthetic ECG channel is created from cross channel average
    else:
        ecg_epochs = create_ecg_epochs(raw, tmin=-.5, tmax=.5, picks=select_sensors)
    ### ICA for ECG artifact 
    # threshold=0.25 come defualt
    ecg_inds, scores = ica.find_bads_ecg(ecg_epochs, method='ctps', threshold=0.25)
    # if len(ecg_inds) > 0:
    ecg_evoked = ecg_epochs.average()    
    ecg_epochs = None    # ecg_epochs use too much memory
    
    # --------------------- Generate report for ECG ---------------------------------------- #
    fig1 = ica.plot_scores(scores, exclude=ecg_inds, title=ICA_title % 'ecg', show=is_show)
    show_picks = np.abs(scores).argsort()[::-1][:5] # Pick the five largest scores and plot them

    # Plot estimated latent sources given the unmixing matrix.

    # topoplot of unmixing matrix columns
    fig3 = ica.plot_components(show_picks, title=ICA_title % 'ecg', colorbar=True, show=is_show)

    n_max_ecg = 3
    ecg_inds = ecg_inds[:n_max_ecg]
    ica.exclude += ecg_inds

    fig4 = ica.plot_sources(ecg_evoked, exclude=ecg_inds, show=is_show)  # plot ECG sources + selection
    fig = [fig1, fig3, fig4]
    report.add_figs_to_section(fig, captions=['Scores of ICs related to ECG',
                                              'TopoMap of ICs (ECG)', 
                                              'Time-locked ECG sources'], section = 'ICA - ECG for ' + subj_name)  
    # ----------------------------------- end generate report for ECG ------------------------------- #

    
    eog_inds, scores = ica.find_bads_eog(raw, ch_name=EoG_ch_name)

    # ------------------------------------------------------ # 
    # This is necessary. Otherwise line 
    # will through an exception
    eog_inds = eog_inds[:n_max_eog]
    if not eog_inds:
        eog_inds = None
    # ------------------------------------------------------ #

    fig6 = ica.plot_scores(scores, exclude=eog_inds, title=ICA_title % 'eog', show=is_show)
    report.add_figs_to_section(fig6, captions=['Scores of ICs related to EOG'], 
                       section = 'ICA - EOG')
                       
    # check how many EoG ch we have
    # --------------------------------- Generate report for EoG --------------------------------------------- #
    rs = np.shape(scores)
    if len(rs)>1:
        rr = rs[0]
        show_picks = [np.abs(scores[i][:]).argsort()[::-1][:5] for i in range(rr)]
        for i in range(rr):
            fig8 = ica.plot_components(show_picks[i][:], title=ICA_title % 'eog',
                                       colorbar=True, show=is_show) # ICA nel tempo
            fig = [fig8]
            report.add_figs_to_section(fig, captions=['Scores of ICs related to EOG'],
                                        section = 'ICA - EOG')    
    else:
        show_picks = np.abs(scores).argsort()[::-1][:5]                                  
        fig8 = ica.plot_components(show_picks, title=ICA_title % 'eog', colorbar=True, show=is_show) 
        fig = [fig8]            
        report.add_figs_to_section(fig, captions=['TopoMap of ICs (EOG)',],
                                        section = 'ICA - EOG') 
       # -------------------- end generate report for EoG -------------------------------------------------------- #
    sfreq = raw.info['sfreq']
    raw = None # To save memory

    report_filename = os.path.join(subj_path,basename + "-report.html")
    print '******* ' + report_filename
    report.save(report_filename, open_browser=False, overwrite=True)
            
    ### save ICA solution  
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
    return raw_ica_filename, sfreq


if __name__ == '__main__':
    # subj_name = 'R0010'
    # subj_name = 'K0021'
    subj_name = 'R0035'
    fif_file = '/net/server/data/home/meg/DMALT/aut_rs/MEG/' + subj_name + '/' + subj_name + '_rest_raw_tsss_mc_trans_eo.fif'
    # ECG_ch_name = 'ECG063'
    ECG_ch_name = 'ECG063'
    # EoG_ch_name = 'EOG061,EOG062'
    EoG_ch_name = 'EMG065,EMG067'
    l_freq = 0.1
    h_freq = 300
    ignore_exception = False
    preprocess_ICA_fif_to_ts(fif_file, ECG_ch_name, EoG_ch_name, l_freq, h_freq)

