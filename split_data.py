def split_fif_into_eo_ec(fif_file, lCondStart, lCondEnd, first_samp, cond):
  # import mne
  import os
  from nipype.utils.filemanip import split_filename as split_f
  from mne.io import Raw
  subj_path, basename, ext = split_f(fif_file)
  # raw1 = raw.crop(tmin=10, tmax=30)
  # print("I did smth")
# --------------- Delete later ----------------------- #
  subj_name = subj_path[-5:]
  results_dir = subj_path[:-6]
  results_dir += '2016'
  subj_path = results_dir + '/' + subj_name
  if not os.path.exists(subj_path):
      os.makedirs(subj_path)
########################################################

  print(fif_file)
  Raw_fif = Raw(fif_file, preload=True)
  # first_samp_time = Raw_fif.index_as_time(Raw_fif.first_samp)
  lRaw_cond = []
  # print("I did smth")

  if cond == 'eo':
    eo_ec_split_fif = subj_path + '/' + basename + '_eo'
  elif cond == 'ec':
    eo_ec_split_fif = subj_path + '/' + basename + '_ec'

  for i in range(len(lCondStart)):
    tmin = lCondStart[i] - first_samp
    tmax = lCondEnd[i] - first_samp
    # To make sure, that my eo-ec time intervals are inside the recording
    if i == 0:
      tmin += 0.5
    if i == range(len(lCondStart))[-1]:
      tmax -= 0.5
    ####################################
    # print("tmin = ")
    # print(tmin)
    # print("tmax = ")
    # print(tmax)
    fif_cropped = Raw_fif.crop(tmin=tmin, tmax=tmax)
    cropped_filename = eo_ec_split_fif + '_' + str(i) + ext
    fif_cropped.save(cropped_filename, overwrite=True)
    lRaw_cond.append(fif_cropped)

  Raw_cond = lRaw_cond[0]
  Raw_cond.append(lRaw_cond[1:])

  print(eo_ec_split_fif)
  eo_ec_split_fif = eo_ec_split_fif + ext
  Raw_cond.save(eo_ec_split_fif, overwrite=True)
  return eo_ec_split_fif
  # return Raw_ec_name


def merge_fif_from_eo_ec(Subj_ID):
  from mne.io import Raw
  import pandas as pd
  from table_handling import get_eo_ec_by_name
  from params import main_path
  Subj_ID_ec = Subj_ID + ' CLOSED'
  Subj_ID_eo = Subj_ID + ' OPEN'
  eo_ec_table_fname = main_path + 'Aut_gamma_EO_EC_Timing.xls'
  suffix_open = '_rest_open_raw_tsss_mc_trans.fif'
  suffix_closed = '_rest_closed_raw_tsss_mc_trans.fif'
  suffix_merged = '_rest_raw_tsss_mc_trans.fif'
  filename_ec = main_path + 'MEG/' + Subj_ID + '/' + Subj_ID + suffix_closed
  filename_eo = main_path + 'MEG/' + Subj_ID + '/' + Subj_ID + suffix_open
  filename_merged = main_path + 'MEG/' + Subj_ID + '/' + Subj_ID + suffix_merged

  if Subj_ID[0] == 'K':
    sheetname = 'Control'
  elif Subj_ID[0] == 'R':
    sheetname = 'ASD'

  eo_ec_table = pd.read_excel(eo_ec_table_fname, skiprows=[1], sheetname=sheetname)
  idx_Subj_ID_ec = eo_ec_table.Subj_ID == Subj_ID_ec
  idx_Subj_ID_eo = eo_ec_table.Subj_ID == Subj_ID_eo
  first_samp_ec = eo_ec_table[idx_Subj_ID_ec]['#f'].get_values()[0]
  first_samp_eo = eo_ec_table[idx_Subj_ID_eo]['#f'].get_values()[0]

  raw_eo = Raw(filename_eo)
  raw_ec = Raw(filename_ec)
  ec_length = round(raw_ec.times[-1], 0)
  raw_ec.append(raw_eo)

  raw_ec.save(filename_merged, overwrite=True)
  # lCondStart, lCondEnd, first_samp, cond = \
  #   get_eo_ec_by_name(Subj_ID_ec, 'ec')
  lCondStart_eo, lCondEnd_eo, _, _ = \
    get_eo_ec_by_name(Subj_ID_eo, 'eo')

  lCondStart_eo = [time + ec_length - first_samp_eo + first_samp_ec for time in lCondStart_eo]
  lCondEnd_eo = [time + ec_length - first_samp_eo + first_samp_ec for time in lCondEnd_eo]
  print 'EO start times : {}'.format(lCondStart_eo)
  print 'EO end times : {}'.format(lCondEnd_eo)
  print 'Merged file length: {} seconds'.format(round(raw_ec.times[-1], 0))

  return
  # import pandas as pd


def generate_figures_for_report(report, epochsHpass,
                                rawHpass, events,
                                half_ep_length, ep_length, iEp, picks):
  # -------------------------------------------------- #
  import numpy as np
  from mne import Epochs
  fig_topo = epochsHpass[iEp].plot_psd_topomap(
      bands=[(100, 200, 'Highpass')], show=False)
  bad_event_time = rawHpass.index_as_time(
      events[0, iEp] - rawHpass.first_samp)
  # raw_grad = raw.pick_types(meg='mag')
  sfreq = rawHpass.info['sfreq']
  # import pdb; pdb.set_trace()
  # ------------------------------ #
  draw_events = np.copy(events.T[iEp - 1:iEp + 2:2, :])
  draw_events[0, 0] += half_ep_length * sfreq
  draw_events[-1, 0] -= half_ep_length * sfreq
  draw_events[0, 2] = 0
  draw_events[-1, 2] = 0
  # ------------------------------ #
  # draw_events[0]
  draw_epoch = Epochs(rawHpass, events=events[
                      :, iEp:iEp + 1].T, picks=picks, event_id=0, tmin=-ep_length, tmax=ep_length)
  # import pdb; pdb.set_trace()
  # , hline=[baseline_std *  1e15, -baseline_std *  1e15])
  fig_av = draw_epoch.average().plot(show=False)

  section_title = 'Event time (seconds): ' + str(bad_event_time)
  raw_caption = "Raw signal near the event"
  topo_caption = "Topography of muscle event detected at " + \
      str(bad_event_time)
  grads_caption = "Averaged signal (gradiometers)"
  mags_caption = "Averaged signal (magnetometers)"
  sensors_caption = 'Raw signal near ' + str(bad_event_time) + ' seconds'
  report.add_figs_to_section([fig_topo, fig_av],
                             captions=[topo_caption, sensors_caption],
                             section=section_title)
  return


def split_fif_into_epochs(fif_file, ep_length, isRemoveMuscleEpochs=False):
  """
  Split fif_file into epochs of ep_length. Removes epochs
  with muscle activity if isRemoveMuscleEpochs is set to True.
  Args:
          fif_file
          ep_length
          isRemoveMuscleEpochs
  """
  # ---------------- Imports ---------------------------------#
  import os
  import numpy as np
  import mne
  from mne.io import Raw
  from nipype.utils.filemanip import split_filename as split_f
  # --------------------------------------------------------- #
  ep_length = float(ep_length)
  subj_path, basename, ext = split_f(fif_file)
  # path = '/media/karim/79DE901F11ABED4C/Dimitriy/resting_data/MEG/K0017/'
  raw = Raw(fif_file, preload=True)
  sfreq = raw.info['sfreq']
  half_ep_length = ep_length / 2.
  first_time = half_ep_length
  last_time = raw.times[-1]
  event_times = np.arange(first_time, last_time, ep_length)
  event_idx = raw.time_as_index(event_times) + raw.first_samp
  events = np.array([event_idx, np.zeros(event_idx.shape),
                     np.ones(event_idx.shape)], dtype=np.int)
  picks = mne.pick_types(
      raw.info, meg=True, eeg=False, stim=False, eog=False)

  # Remove epoch if its amplitude goes more then stdThreshold STDs above
  # baseline
  bad_epochs_count = 0
  if isRemoveMuscleEpochs:
    from split_data import generate_figures_for_report
    from mne.report import Report
    report = Report()
    report_filename = basename + '_muscle_' + '.html'
    rawHpass = raw.copy()
    rawHpass.filter(l_freq=100, h_freq=None)
    rawHpassPicks = mne.pick_types(
        rawHpass.info, meg='mag', eeg=False, stim=False, eog=False)
    stdThreshold = 4.
    maxThreshold = 6.
    # print("Before epochs")

    epochsHpass = mne.Epochs(rawHpass, events.T, picks=rawHpassPicks,
                             event_id=1, tmin=-half_ep_length, tmax=half_ep_length,
                             reject=None, baseline=None, flat=dict(mag=1e-14), preload=True)
    # print("After epochs")

    ep_data = epochsHpass.get_data()
    baseline_std = 5e-14
    badChThreshold_std = 15
    badChThreshold_max = 50

    for iEp in range(len(ep_data[:, -1, -1])):
      std_ep = ep_data[iEp, :, :].std(axis=1)
      # import pdb; pdb.set_trace()
      max_ep = ep_data[iEp, :, :].max(axis=1)
      if len(std_ep[std_ep > baseline_std * stdThreshold]) > badChThreshold_std or len(max_ep[max_ep > baseline_std * maxThreshold]) > badChThreshold_max:

          # print std_ep[std_ep > baseline_std * std_ep]
          bad_epochs_count += 1
          events[2, iEp] = 0
          # import pdb; pdb.set_trace()
          # print len(std_ep[std_ep > baseline_std * std_ep])
          print "Number of contaminated channels: ", len(std_ep[std_ep > baseline_std * stdThreshold]) + len(max_ep[max_ep > baseline_std * maxThreshold])
          generate_figures_for_report(
              report, epochsHpass, rawHpass, events, half_ep_length, ep_length, iEp, picks)

    report.save(report_filename, open_browser=False, overwrite=True)

  # Set events for epochs
  # Need to add raw.first_samp because otherwise it drops out
  # epochs with times less than raw.first_samp (see epochs.py: _get_epoch_from_disk)
  # import pdb; pdb.set_trace()
  epochs = mne.Epochs(raw, events.T, picks=picks, proj=False, event_id=1,
                      tmin=-half_ep_length, tmax=half_ep_length,
                      reject=None, baseline=None, preload=True)
  np_epochs = epochs.get_data()
  epochs_file = os.path.abspath(basename + '_epochs.npy')
  np.save(epochs_file, np_epochs)
  return epochs, epochs_file, np_epochs, bad_epochs_count


if __name__ == "__main__":
  Subj_ID = 'K0014'
  merge_fif_from_eo_ec(Subj_ID)
  # merge_fif_from_eo_ec(filename_eo, first_samp_eo, filename_ec, first_samp_ec)
  # filename = \
  # '/home/karim/aut_rs/MEG/R0018/R0018_rest_raw_tsss_mc-ica_raw-eo.fif'
  # raw = Raw(filename, preload=True)
  # epochs, epochs_file, np_epochs, bad_epochs_count = split_fif_into_epochs(
  #     filename, ep_length=1., isRemoveMuscleEpochs=True)


# import mne
# from mne.io import Raw
# import numpy as np
# file_name = \
#   '/home/karim/aut_rs/MEG/R0018/R0018_rest_raw_tsss_mc-ica_raw-ec.fif'
# file_name = \
#   '/home/karim/aut_rs/MEG/R0016/R0016_rest_raw_tsss_mc-ica_raw-ec.fif'
# raw = Raw(file_name, preload=True)
# raw.info['first_samp']=0.
# Highpass-filter raw data
# raw.filter(l_freq=100, h_freq=None)
# raw.filter(l_freq=2, h_freq=300)
# raw_grad = raw.pick_types(meg='mag')
# data,times = raw_grad[:,:]
# std_ep = data[:,:1200].std(axis = 1)
# m = data.mean(axis = 1)
# print(std_raw)
# ep_length=1.
# std_threshold = 4
# event_times = np.arange(1.,raw.times[-1],ep_length)
# event_idx = raw.time_as_index(event_times)

# events = np.array([event_idx,
#            np.zeros(event_idx.shape),
#            np.ones(event_idx.shape)])
# picks = mne.pick_types(raw.info, meg='mag', eeg=False,
#                        stim=False, eog=False, ecg=False)
# epochs = mne.Epochs(raw,events.T, picks=picks, event_id = 1,
#                     tmin=-ep_length/2.,tmax=ep_length/2.,
#                     reject=None,baseline=None,
#                     flat=dict( mag=1e-14), preload=True)
# ep_data = epochs.get_data()
# bad_ch_count=0
# baseline_std = 5e-14


# for iEp in range(len(ep_data[:,-1,-1])):
# for iCh in range(len(ep_data[-1,:,-1]))
#   std_ep = ep_data[iEp,:,:].std(axis=1)
# print(std_ep.shape)
# mean_ep = ep_data[iEp,:,:].mean(axis=1)
#   if len(std_ep[std_ep > std_threshold * std_raw]):
#     print(len(std_ep[std_ep > std_threshold * baseline_std]))
#     print(epochs.events[iEp,0] / 300 )
#     print('\n')
# .plot_psd_topomap()
# epochs[iEp].plot_psd_topomap( bands = [(100, 300, 'Muscle topography')])#.savefig('h_gamma_k.png',dpi=600,bbox_inches='tight')
# print(std_ep)
# epochs.plot_psd_topomap( bands = [(2, 4, 'Delta'), (4, 8, 'Theta'), (8, 12, 'Alpha'), (15, 30, 'Beta'), (30, 60, 'Gamma'), (60,90, 'High gamma')])
