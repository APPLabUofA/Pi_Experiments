# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import mne
#from mne.time_frequency import induced_power
from scipy import io
import pylab as pl
import numpy as np

filename = "M:\\Data\\VR_P3\\037_visual_nhs.vhdr"

raw = mne.io.read_raw_brainvision(filename)

start, stop = raw.time_as_index([100, 115])

data, times = raw[:, start:stop]

print(data.shape)
print(times.shape)

events = mne.find_events(raw, stim_channel = 'STI 014')

print(events[:5])

event_id = dict(stand = 85, targ = 255)
tmin = -0.2
tmax = 1.0

picks = mne.pick_types(raw.info, meg=False, eeg=True, eog=False, stim=False)

baseline = (None, 0)

epochs = mne.Epochs(raw, events, event_id, tmin, tmax, proj=True, picks=picks,
                    baseline=baseline, preload=False)

print(epochs)

epochs_data = epochs['targ'].get_data()
print(epochs_data.shape)

io.savemat('epochs_data.mat', dict(epochs_data=epochs_data), oned_as='row')
epochs.save('sample-epo.fif')

evoked = epochs['targ'].average()
print(evoked)

evoked.plot()

max_in_each_epoch = [e.max() for e in epochs['aud_l']]
print(max_in_each_epoch[:4])


n_cycles = 2  # number of cycles in Morlet wavelet
frequencies = np.arange(7, 30, 3)  # frequencies of interest
Fs = raw.info['sfreq']  # sampling in Hz
times = epochs.times

power, phase_lock = induced_power(epochs_data, Fs=Fs, frequencies=frequencies, n_cycles=2, n_jobs=1)

# baseline corrections with ratio
power /= np.mean(power[:, :, times < 0], axis=2)[:, :, None]

print(power.shape)
print(phase_lock.shape)

ch_idx = 145  # select a channel to show

pl.subplots_adjust(0.1, -0.05, 0.96, 0.94, 0.2, 0.63)
pl.subplot(3, 1, 1)
pl.plot(times, evoked.data[ch_idx, :])
pl.title('Evoked response (%s)' % evoked.ch_names[ch_idx])
pl.xlabel('time (s)')
pl.ylabel('Magnetic Field (fT/cm)')
pl.xlim(times[0], times[-1])

pl.subplot(3, 1, 2)
pl.imshow(20 * np.log10(power[ch_idx]), extent=[times[0], times[-1],
          frequencies[0], frequencies[-1]], aspect='auto', origin='lower')
pl.xlabel('Time (s)')
pl.ylabel('Frequency (Hz)')
pl.title('Induced power (%s)' % evoked.ch_names[ch_idx])
pl.colorbar()

pl.subplot(3, 1, 3)
pl.imshow(phase_lock[ch_idx], extent=[times[0], times[-1],
          frequencies[0], frequencies[-1]], aspect='auto', origin='lower')
pl.xlabel('Time (s)')
pl.ylabel('Frequency (Hz)')
pl.title('Phase-lock (%s)' % evoked.ch_names[ch_idx])
pl.colorbar()