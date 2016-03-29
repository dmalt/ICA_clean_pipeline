def generateReport(raw, ica, subj_name, subj_path, basename,
                   ecg_evoked, ecg_scores, ecg_inds, ECG_ch_name,
                   eog_evoked, eog_scores, eog_inds, EoG_ch_name):
    from mne.report import Report
    import numpy as np
    import os
    report = Report()

    ICA_title = 'Sources related to %s artifacts (red)'
    is_show = False # visualization

    # --------------------- Generate report for ECG ---------------------------------------- #
    fig1 = ica.plot_scores(
        ecg_scores, exclude=ecg_inds, title=ICA_title % 'ecg', show=is_show)
    # Pick the five largest ecg_scores and plot them
    show_picks = np.abs(ecg_scores).argsort()[::-1][:5]

    # Plot estimated latent sources given the unmixing matrix.

    # topoplot of unmixing matrix columns
    fig3 = ica.plot_components(
        show_picks, title=ICA_title % 'ecg', colorbar=True, show=is_show)

    

    # plot ECG sources + selection
    fig4 = ica.plot_sources(ecg_evoked, exclude=ecg_inds, show=is_show)
    fig = [fig1, fig3, fig4]
    report.add_figs_to_section(fig, captions=['Scores of ICs related to ECG',
                                              'TopoMap of ICs (ECG)',
                                              'Time-locked ECG sources'], section='ICA - ECG for ' + subj_name)
    # ----------------------------------- end generate report for ECG ------------------------------- #


    fig6 = ica.plot_scores(
        eog_scores, exclude=eog_inds, title=ICA_title % 'eog', show=is_show)
    report.add_figs_to_section(fig6, captions=['Scores of ICs related to EOG'],
                               section='ICA - EOG')

    # check how many EoG ch we have
    # --------------------------------- Generate report for EoG --------------------------------------------- #
    rs = np.shape(eog_scores)
    if len(rs) > 1:
        rr = rs[0]
        show_picks = [np.abs(eog_scores[i][:]).argsort()[::-1][:5]
                      for i in range(rr)]
        for i in range(rr):
            fig8 = ica.plot_components(show_picks[i][:], title=ICA_title % 'eog',
                                       colorbar=True, show=is_show)  # ICA nel tempo
            fig = [fig8]
            report.add_figs_to_section(fig, captions=['Scores of ICs related to EOG'],
                                       section='ICA - EOG')
    else:
        show_picks = np.abs(eog_scores).argsort()[::-1][:5]
        fig8 = ica.plot_components(
            show_picks, title=ICA_title % 'eog', colorbar=True, show=is_show)
        fig = [fig8]
        report.add_figs_to_section(fig, captions=['TopoMap of ICs (EOG)', ],
                                   section='ICA - EOG')
       # -------------------- end generate report for EoG -------------------------------------------------------- #

    report_filename = os.path.join(subj_path, basename + "-report.html")
    print '******* ' + report_filename
    report.save(report_filename, open_browser=False, overwrite=True)
