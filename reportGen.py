    from mne.report import Report
    report = Report()


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
            
    
