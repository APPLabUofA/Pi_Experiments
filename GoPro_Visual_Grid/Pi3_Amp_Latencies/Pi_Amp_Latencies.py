#import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np 
from sklearn.linear_model import LinearRegression
import mne

plt.close('all')

trials = 200;
#blocks = 1;

# # The only thing you need to change is going to be par (participant number) the rest will be dictated by dictionaries
par = "001"


# %% We will now load in the EEG data 
#### Now we will go through the EEG file and determine our latencies

# filename = 'M:\Data\GoPro_Visor\Pi_Amp_Latency_Test\\testing_visor_pi_' + par + '.vhdr' # pre-pilot
filename = 'M:\Data\GoPro_Grid\EEG_Data\\' + par + '_grid_test.vhdr' # pilot
raw = mne.io.read_raw_brainvision(filename)
df1 = mne.find_events(raw) # outputs a numpy.ndarray
df1 = np.insert(df1,0,[0],axis = 0) #shift data one row down from the top so we don't miss the first event on o
df1 = pd.DataFrame(data=df1[1:,1:], index=df1[1:,0], columns=df1[0,1:])   # change to a pandas DataFrame
df1 = df1.reset_index() 
df1.columns = ['eeg_times', 'Empty', 'Event_Type'] # name columns
df1 = df1.drop(columns='Empty') # get rid of empty column
df1['eeg_times'] = (df1['eeg_times'] - df1['eeg_times'][0]) # subtract all from start trigger

criteria_1 = df1['Event_Type'] == 253 
#criteria_2 =  df1['Event_Type'] == 255
#criteria_all = criteria_1 | criteria_2 # either/or event defined above
df1 = df1[criteria_1]
df1 = df1.reset_index() # resets index after removing events
df1 = df1.drop(columns='index')
## still need to minus all from the first event trigger before it gets deleted


# %% Here we extract thhe Pi times (imported as df2)
#df2 = pd.read_csv((r'C:\Users\User\Documents\GitHub\GoPro_Visor_Pi\Pi3_Amp_Latencies\Pi_Time_Data\014_visual_p3_gopro_visor.csv'), sep=',', header=None) # pre-pilot
#df2 = pd.read_csv((r'C:\Users\User\Documents\GitHub\GoPro_Visor_Pi\Pilot_Data\Experiment_1\Pi_Times\002_visual_p3_gopro_visor.csv'), sep=',', header=None) # pilot
df2 = pd.read_csv((r'M:\Data\GoPro_Grid\Pi_Times\001_test.csv'), sep=',', header=None) # pilot
#df2 = df2.T # transpose for plotting purposes
df2.columns = ['pi_onset_latency'] # name the coloumns
df2 = df2.apply(pd.to_numeric, args=('coerce',))  ## Convert to numeric
#df2= df2.dropna(thresh=2)
#criteria_1 = df2['pi_type'] == 1 
#criteria_2 =  df2['pi_type'] == 2
#criteria_all = criteria_1 | criteria_2
#df2 = df2[criteria_all] # Unalignable boolean Series provided as indexer (index of the boolean Series and of the indexed object do not match
# deal with this with the following - df2 = df2.reset_index()
df2['pi_onset_latency'] = df2['pi_onset_latency'] * 1000 # subtract all from start trigger

# %% 
df2 = df2.reset_index()

# %% 
#df_GoPro = pd.read_csv(())
#df2 = df2.T # transpose for plotting purposes
#df2.columns
# %%
# Combine the two into a single dataframe ? Nah, not for now
#all_onset_latencies = pd.concat([df1.assign(dataset='df1'), df2.assign(dataset='df2')])
df3 = df1.join(df2) # join eeg_times to pi_times
df3 = df3.reset_index()
df3['Difference'] = df3['eeg_times'] - df3['pi_onset_latency']
#%%
# Plotting 
# Latency plot
plt.close('all')
# matlibplot 
plt.figure(0)
plt.plot(df3['pi_onset_latency'], df3['level_0'], 'k--', label='Pi Times')
plt.plot(df3['eeg_times'], df3['level_0'], 'ko', label='EEG Times')
plt.xlabel('Latency (Miliseconds)')
# plt.ylabel('Trial Count')
legend = plt.legend(loc='upper center', shadow=True, fontsize='x-large')
legend.get_frame().set_facecolor('C0')
plt.show()

# Difference plot
plt.figure(1)
plt.plot(df3['Difference'], df3['level_0'], label='EEG - Pi')
legend = plt.legend(loc='upper right', shadow=True, fontsize='x-large')
plt.xlabel('Latency (Miliseconds)')
# plt.ylabel('Trial Count')
plt.show()

# %% ##Linear Transform
df4 = df3.copy() # copy DataFrame 
df4 = df4.values # convert from Pandas DataFrame to a numpy structure
#df4[:,12] = df4[:,1]-df4[:,5]
df4 = np.append(df4, np.zeros((trials,3)), axis=1)
# %% ## Transform the eeg_times to align with the Pi times - we then need to output each participant time as a single array
## loading it into each respective epoch dataframes as the updated times
## LinearRegression().fit(X, y) X=Training data (eeg_times), y=Target Values (pi_onset_latency)
reg =  LinearRegression().fit(df4[:,1].reshape(-1,1), df4[:,5].reshape(-1,1))
reg.score(df4[:,1].reshape(-1,1), df4[:,5].reshape(-1,1))

df4[:,6] = reg.intercept_ + df4[:,1]*reg.coef_
df4[:,7] = df4[:,1]-df4[:,5]
df4[:,8] = df4[:,5]-df4[:,6]
# %% ## Transformed Difference plot
plt.figure(2)
plt.plot(df4[:,6], df4[:,0])
#plt.plot(df4[:,10], df4[:,0]) #plot the magnitude of the difference 
#plt.plot(df3['Difference'], df3['level_0'], label='EEG - Pi') # plot untransformed
plt.legend('EEG - Pi', ncol=2, loc='upper left'); #  scalex=True, scaley=True if not using a custom xticks arguement
plt.xlabel('Latency (miliseconds)')
#plt.xlim([-0.001, 0, 0.001])
plt.show()





