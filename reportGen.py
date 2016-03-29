def generateReport(raw, ica, subj_name, subj_path, basename,
                   ecg_evoked, ecg_scores, ecg_inds, ECG_ch_name,
                   eog_evoked, eog_scores, eog_inds, EoG_ch_name):
    from mne.report import Report
    import numpy as np
    import os
    import HTML
    report = Report()

    ICA_title = 'Sources related to %s artifacts (red)'
    is_show = False # visualization

    File_length = str(round(raw.times[-1], 0))
    # report.add_htmls_to_section(htmls=name_html, captions='File path', section='General')
    name_html =  '<h4 style="text-align:left;"> Path:  ' + subj_path + '/' + basename + '.fif' + '</h4>'
    ex_comps_table = [['', 'ICs to exclude'],['ECG', ecg_inds], ['EOG', eog_inds]]
    ex_comps_html = '<h4>' + HTML.table(ex_comps_table) + '</h4>'
    File_length_html = '<h4 style="text-align:left;">' + 'File length: ' + File_length + ' seconds' + '</h4>'
    report.add_htmls_to_section(htmls=name_html + File_length_html + ex_comps_html, captions='General info', section='General info')
    # --------------------- Generate report for ECG ---------------------------------------- #
    fig1 = ica.plot_scores(
        ecg_scores, exclude=ecg_inds, title=ICA_title % 'ecg', show=is_show)
    # Pick the five largest ecg_scores and plot them
    show_picks = np.abs(ecg_scores).argsort()[::-1][:5]

    # Plot estimated latent sources given the unmixing matrix.

    # topoplot of unmixing matrix columns
    fig2 = ica.plot_components(
        show_picks, title=ICA_title % 'ecg', colorbar=True, show=is_show)

    

    # plot ECG sources + selection
    fig3 = ica.plot_sources(ecg_evoked, exclude=ecg_inds, show=is_show)
    fig = [fig1, fig2, fig3]
    report.add_figs_to_section(fig, captions=['Scores of ICs related to ECG',
                                              'TopoMap of ICs (ECG)',
                                              'Time-locked ECG sources'], section='ICA - ECG')
    # ----------------------------------- end generate report for ECG ------------------------------- #


    fig4 = ica.plot_scores(
        eog_scores, exclude=eog_inds, title=ICA_title % 'eog', show=is_show)
    report.add_figs_to_section(fig4, captions=['Scores of ICs related to EOG'],
                               section='ICA - EOG')

    # check how many EoG ch we have
    # --------------------------------- Generate report for EoG --------------------------------------------- #
    rs = np.shape(eog_scores)
    if len(rs) > 1:
        rr = rs[0]
        show_picks = [np.abs(eog_scores[i][:]).argsort()[::-1][:5]
                      for i in range(rr)]
        for i in range(rr):
            fig5 = ica.plot_components(show_picks[i][:], title=ICA_title % 'eog',
                                       colorbar=True, show=is_show)  # ICA nel tempo
            fig = [fig5]
            report.add_figs_to_section(fig, captions=['Scores of ICs related to EOG'],
                                       section='ICA - EOG')
    else:
        show_picks = np.abs(eog_scores).argsort()[::-1][:5]
        fig5 = ica.plot_components(
            show_picks, title=ICA_title % 'eog', colorbar=True, show=is_show)
        fig = [fig5]
        report.add_figs_to_section(fig, captions=['TopoMap of ICs (EOG)', ],
                                   section='ICA - EOG')
       # -------------------- end generate report for EoG -------------------------------------------------------- #
    fig9 = ica.plot_sources(eog_evoked, exclude=eog_inds, show=is_show)  # plot EOG sources + selection
    # fig10 = ica.plot_overlay(eog_evoked, exclude=eog_inds, show=is_show)  # plot EOG cleaning

    # fig = [fig9, fig10]
    fig = [fig9]
    report.add_figs_to_section(fig, captions=['Time-locked EOG sources'], section = 'ICA - EOG')
    # import ipdb; ipdb.set_trace()
    IC_nums = range(ica.n_components_)
    fig = ica.plot_components(picks=IC_nums, show=False)
    report.add_figs_to_section(fig, captions=['All IC topographies'], section='ICA - muscles')

    psds = []
    captions_psd = []
    ica_src = ica.get_sources(raw)
    for iIC in IC_nums:
        fig = ica_src.plot_psd(tmax=None, picks=[iIC], fmax=140, show=False)
        fig.set_figheight(3)
        fig.set_figwidth(5)
        psds.append(fig)
        captions_psd.append('IC #' + str(iIC))
    # report.add_slider_to_section(figs=psds, captions=captions_psd, title='', section='ICA - muscles')
    report.add_figs_to_section(figs=psds, captions=captions_psd, section='ICA - muscles')
    report_filename = os.path.join(subj_path, basename + "-report.html")
    print '******* ' + report_filename
    report.save(report_filename, open_browser=False, overwrite=True)


if __name__ == '__main__':

    generateReport(raw=raw, ica=ica, subj_name=subj_name, subj_path=subj_path, basename=basename,
                   ecg_evoked=ecg_evoked, ecg_scores=ecg_scores, ecg_inds=ecg_inds, ECG_ch_name=ECG_ch_name,
                   eog_evoked=eog_evoked, eog_scores=eog_scores, eog_inds=eog_inds, EoG_ch_name=EoG_ch_name)