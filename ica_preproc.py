def preprocess_ICA_fif_to_ts(fif_file, ECG_ch_name, EoG_ch_name, l_freq, h_freq, down_sfreq, is_sensor_space):
    import os
    import numpy as np

    import mne
    from mne.io import Raw	
    from mne.preprocessing import ICA, read_ica
    from mne.preprocessing import create_ecg_epochs, create_eog_epochs, ssp
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
    # EoG_ch_name = "EOG061, EOG062"
    raw = Raw(fif_file, preload=True)
    ### select sensors                                         
    select_sensors = mne.pick_types(raw.info, meg=True, ref_meg= False, exclude='bads')
    picks_meeg     = mne.pick_types(raw.info, meg=True, eeg=True, exclude='bads')
    
    ### save electrode locations
    sens_loc = [raw.info['chs'][i]['loc'][:3] for i in select_sensors]
    sens_loc = np.array(sens_loc)

    channel_coords_file = os.path.abspath("correct_channel_coords.txt")
    np.savetxt(channel_coords_file ,sens_loc , fmt = '%s')

    ### save electrode names
    sens_names = np.array([raw.ch_names[pos] for pos in select_sensors],dtype = "str")

    channel_names_file = os.path.abspath("correct_channel_names.txt")
    np.savetxt(channel_names_file,sens_names , fmt = '%s')
 
    ### filtering + downsampling
    raw.filter(l_freq = l_freq, h_freq = h_freq, picks = picks_meeg, method='iir', n_jobs=1)

    # raw.resample(sfreq = down_sfreq, npad = 0)
    #rnk = raw.estimate_rank(tstart=30, tstop=60, picks=select_sensors)
    #print rnk
    rnk = 'N/A'
    ### 1) Fit ICA model using the FastICA algorithm
    # Other available choices are `infomax` or `extended-infomax`
    # We pass a float value between 0 and 1 to select n_components based on the
    # percentage of variance explained by the PCA components.
    ICA_title = 'Sources related to %s artifacts (red)'
    is_show = False # visualization
    reject = dict(mag=6e-12, grad=6000e-13)
    flat = dict(mag=0.1e-12, grad=1e-13)
    # check if we have an ICA, if yes, we load it
    ica_filename = os.path.join(subj_path, basename + "-ica.fif")  
    raw_ica_filename = os.path.join(subj_path, basename + "_ica_raw.fif")  
    if os.path.exists(ica_filename) == False:
    # if os.path.exists(ica_filename) == True:
       
        # ica = ICA(n_components=0.99, method='fastica') # , max_iter=500
        ica = ICA(n_components=0.99, method='fastica') # , max_iter=500
        #ica = ICA(n_components=rnk, method='fastica') # , max_iter=500
        ica.fit(raw, picks=select_sensors, reject=reject, decim=3, flat=flat) # decim = 3, 
        
        has_ICA = False
    else:
        has_ICA = True
        ica = read_ica(ica_filename)
        ica.exclude = []
        ica.labels_ = dict() # to avoid bug; Otherwise it'll throw an exception

    ica_sources_filename = subj_path + '/' + basename + '_ica_timecourse.fif'
    if not os.path.isfile(ica_sources_filename):
        icaSrc = ica.get_sources(raw, add_channels=None, start=None, stop=None)
        icaSrc.save(ica_sources_filename, picks=None, tmin=0, tmax=None, buffer_size_sec=10, drop_small_buffer=False, proj=False, fmt='single', overwrite=True, split_size='2GB', verbose=None)
        icaSrc = None

    if has_ICA == False:
        ica.save(ica_filename)
    # return
    ### 2) identify bad components by analyzing latent sources.
    # generate ECG epochs use detection via phase statistics
    

    # if we just have exclude channels we jump these steps
#    if len(ica.exclude)==0:
    
    n_max_eog = 4
    
    # check if ECG_ch_name is in the raw channels
    # import ipdb; ipdb.set_trace()
    final_log_filename = subj_path + '/' + basename + '_ica_final.log'
    if ECG_ch_name in raw.info['ch_names']:
        ecg_epochs = create_ecg_epochs(raw, tmin=-.5, tmax=.5, picks=select_sensors, ch_name = ECG_ch_name)
    # if not  a synthetic ECG channel is created from cross channel average
    else:
        ecg_epochs = create_ecg_epochs(raw, tmin=-.5, tmax=.5, picks=select_sensors)
    ### ICA for ECG artifact 
    # threshold=0.25 come defualt
    # import pdb; pdb.set_trace()
    ecg_inds, scores = ica.find_bads_ecg(ecg_epochs, method='ctps', threshold=0.25)
    # if len(ecg_inds) > 0:
    ecg_evoked = ecg_epochs.average()    
    ecg_epochs = None    # Consumes too much memory
    ecg_inds_log= []
    eog_inds_log = []
    muscle_inds_log = []
    if os.path.isfile(final_log_filename):
        final_log = open(final_log_filename, 'r')
        lines = final_log.readlines()
        final_log.close()
        import re
        
        inds = []
        for line in lines:
            # match = re.findall(r'(\[|,\s?)(\d*)(,\s?|\])', line)
            match = re.search(r'((EOG|ECG|Muscles)).*', line)
            if match:
                IC_type = match.group(1)
                exclude =  match.group()
                ICs = re.findall(r'\d+', exclude)
                if ICs:
                    print ICs
                    for entry in ICs:
                        inds.append(int(entry))
                    print inds

                    if IC_type == 'ECG':
                        ecg_inds_log = inds[:]
                    elif IC_type == 'EOG':
                        eog_inds_log = inds[:]
                    elif IC_type == 'Muscles':
                        muscle_inds_log = inds
                    inds = []
    if os.path.isfile(final_log_filename):
        ecg_inds = ecg_inds_log
    fig1 = ica.plot_scores(scores, exclude=ecg_inds, title=ICA_title % 'ecg', show=is_show)
    show_picks = np.abs(scores).argsort()[::-1][:5] # Pick the five largest scores and plot them

    # Plot estimated latent sources given the unmixing matrix.
    # ica.plot_sources(raw, show_picks, exclude=ecg_inds, title=ICA_title % 'ecg', show=is_show)
    # import pdb; pdb.set_trace()
    t_start = 0
    t_stop = 30 # take the fist 30s
    fig2 = ica.plot_sources(raw, show_picks, exclude=ecg_inds, title=ICA_title % 'ecg' + ' in 30s',
                            start = t_start, stop  = t_stop, show=is_show)
    # fig2.set_figheight(12)
    # fig2.set_figwidth(24)

    # topoplot of unmixing matrix columns
    fig3 = ica.plot_components(show_picks, title=ICA_title % 'ecg', colorbar=True, show=is_show)

    n_max_ecg = 3
    ecg_inds = ecg_inds[:n_max_ecg]
    ica.exclude += ecg_inds

    fig4 = ica.plot_sources(ecg_evoked, exclude=ecg_inds, show=is_show)  # plot ECG sources + selection
    fig5 = ica.plot_overlay(ecg_evoked, exclude=ecg_inds, show=is_show)  # plot ECG cleaning

    fig = [fig1, fig2, fig3, fig4, fig5]
    report.add_figs_to_section(fig, captions=['Scores of ICs related to ECG',
                                              'Time Series plots of ICs (ECG)',
                                              'TopoMap of ICs (ECG)', 
                                              'Time-locked ECG sources', 
                                              'ECG overlay'], section = 'ICA - ECG for ' + subj_name)  
    
    # check if EoG_ch_name is in the raw channels
    # if EoG_ch_name in raw.info['ch_names']:        
        ### ICA for eye blink artifact - detect EOG by correlation
    eog_inds, scores = ica.find_bads_eog(raw, ch_name=EoG_ch_name)
    if os.path.isfile(final_log_filename):
        if eog_inds:
            eog_inds = eog_inds_log
        else:
            eog_inds = None
        # print('Actually Ive found two Eog channels and they are')
        # print(EoG_ch_name)
    # else:
    #     eog_inds, scores = ica.find_bads_eog(raw)

    # if len(eog_inds) > 0:  
        
    fig6 = ica.plot_scores(scores, exclude=eog_inds, title=ICA_title % 'eog', show=is_show)
    report.add_figs_to_section(fig6, captions=['Scores of ICs related to EOG'], 
                       section = 'ICA - EOG')
                       
    # check how many EoG ch we have
    rs = np.shape(scores)
    if len(rs)>1:
        rr = rs[0]
        show_picks = [np.abs(scores[i][:]).argsort()[::-1][:5] for i in range(rr)]
        for i in range(rr):
            fig7 = ica.plot_sources(raw, show_picks[i][:], exclude=eog_inds, 
                                start = raw.times[0], stop  = raw.times[-1], 
                                title=ICA_title % 'eog',show=is_show)       
                                
            fig7.set_figheight(12)
            fig7.set_figwidth(24)
            fig8 = ica.plot_components(show_picks[i][:], title=ICA_title % 'eog', colorbar=True, show=is_show) # ICA nel tempo

            fig = [fig7, fig8]
            report.add_figs_to_section(fig, captions=['Scores of ICs related to EOG', 
                                             'Time Series plots of ICs (EOG)'],
                                        section = 'ICA - EOG')    
    else:
        show_picks = np.abs(scores).argsort()[::-1][:5]
        fig7 = ica.plot_sources(raw, show_picks, exclude=eog_inds, title=ICA_title % 'eog', show=is_show)  
        fig7.set_figheight(12)
        fig7.set_figwidth(24)                                  
        fig8 = ica.plot_components(show_picks, title=ICA_title % 'eog', colorbar=True, show=is_show) 
        fig = [fig7, fig8]            
        report.add_figs_to_section(fig, captions=['Time Series plots of ICs (EOG)',
                                                  'TopoMap of ICs (EOG)',],
                                        section = 'ICA - EOG') 
    
    eog_inds = eog_inds[:n_max_eog]
    # print(eog_inds)
    # print("Just before ica.exclude")

    ica.exclude += eog_inds
    if os.path.isfile(final_log_filename):
        ica.exclude += muscle_inds_log
    # print("Just after ica.exclude")

    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    # if EoG_ch_name in raw.info['ch_names']:
    eog_evoked = create_eog_epochs(raw, tmin=-.5, tmax=.5, picks=select_sensors, ch_name=EoG_ch_name).average()
    # else:
    #     eog_evoked = create_eog_epochs(raw, tmin=-.5, tmax=.5, picks=select_sensors).average()               
   
    fig9 = ica.plot_sources(eog_evoked, exclude=eog_inds, show=is_show)  # plot EOG sources + selection
    fig10 = ica.plot_overlay(eog_evoked, exclude=eog_inds, show=is_show)  # plot EOG cleaning

    fig = [fig9, fig10]
    report.add_figs_to_section(fig, captions=['Time-locked EOG sources',
                                              'EOG overlay'], section = 'ICA - EOG')

    # fig6.savefig('fig6.png', dpi=400, bbox_inches='tight')
    # fig7.savefig('fig7.png', dpi=400, bbox_inches='tight')
    # fig8.savefig('fig8.png', dpi=400, bbox_inches='tight')
    # fig9.savefig('fig9.png', dpi=400, bbox_inches='tight')
    # fig10.savefig('fig10.png', dpi=400, bbox_inches='tight')

    fig11 = ica.plot_overlay(raw, show=is_show)
    report.add_figs_to_section(fig11, captions=['Signal'], section = 'Signal quality') 
    report_filename = os.path.join(subj_path,basename + "-report.html")
    print '******* ' + report_filename
    report.save(report_filename, open_browser=False, overwrite=True)
        
        
    ### 3) apply ICA to raw data and save solution and report
    # check the amplitudes do not change
    raw_ica = ica.apply(raw, copy=True)
    raw_ica.save(raw_ica_filename, overwrite=True)
    sfreq = raw.info['sfreq']
    # raw = None;
    ### save ICA solution  
    print ica_filename
    

    # ### 4) save data
    # # data_noIca,times = raw[select_sensors,:]
    # data,times       = raw_ica[select_sensors,:]

    # print data.shape
    # # print raw.info['sfreq']

    # ts_file = os.path.abspath(basename +"_ica.npy")
    # np.save(ts_file,data)
    sfreq = raw.info['sfreq']
    f = open(subj_path + '/' + basename + '_ica.log', 'w')
    f.write('Data rank after SSS: ' + str(rnk) + '\n')
    f.write('Sampling freq: ' + str(sfreq) + '\n')
    f.write('ECG exclude ' + str(ecg_inds) + '\n')
    f.write('EOG exclude ' + str(eog_inds) + '\n')
    f.write('Muscles exclude ' + str(muscle_inds_log) + '\n')
    f.close()
    if is_sensor_space:
        # return raw_ica_filename, ts_file,channel_coords_file,channel_names_file,raw.info['sfreq']
        return raw_ica_filename, channel_coords_file,channel_names_file, sfreq
    else:
        return raw_ica, ts_file,channel_coords_file,channel_names_file,raw.info['sfreq']


if __name__ == '__main__':
    fif_file = '/net/server/data/home/meg/DMALT/aut_rs/MEG/R0036/R0036_rest_raw_tsss_mc_trans.fif'
    ECG_ch_name = 'ECG063'
    # EoG_ch_name = 'EOG061,EOG062'
    EoG_ch_name = 'EMG065,EMG066,EMG067,EMG068'
    down_sfreq = 300
    l_freq = 0.1
    h_freq = 300
    ignore_exception = False
    is_sensor_space = True
    preprocess_ICA_fif_to_ts(fif_file, ECG_ch_name, EoG_ch_name, l_freq, h_freq, down_sfreq, is_sensor_space)

