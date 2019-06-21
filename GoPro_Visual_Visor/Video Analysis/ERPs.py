

# %% Create New Native EEG events - creating new epochs
#http://predictablynoisy.com/mne-python/auto_tutorials/plot_creating_data_structures.html#tut-creating-data-structures
#http://predictablynoisy.com/mne-python/auto_tutorials/plot_object_epochs.html
add_eeg_events = 'no'
if add_eeg_events == 'yes':
    mne.io.RawArray.add_events(raw,Targ_Std_fin.values, stim_channel=None, replace=False)
    stim_data = Targ_Std_fin.values
    info = mne.create_info(['STI'], raw.info['sfreq'], ['stim'])
    stim_raw = mne.io.RawArray(stim_data, info)
    raw.add_channels([stim_raw], force_update_info=True)