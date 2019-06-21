# -*- coding: utf-8 -*-
import numpy as np
import mne
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression

# %% Define Variables
par = 3
diff_outlier = 0 # 0 = off, 1 == on - automatically take out outliers in jitter between camera and eeg 
outlier_def = 10 # number seconds of required jitter in order to be automatically disregarded

# %% Load in the Camera timing form the temporary workspace or cvs file for the participant you are working with
# If you want to work with group data - refer to Group_Figures.py
df1 = pd.read_csv((r'M:\Data\GoPro_Visor\Experiment_1\Video_Times\Dataframe_df1a_00' + str(par)) + '.csv', sep=',') # pilot
#df1 = np.insert(df2,0,[0],axis = 0) #shift data one row down from the top so we don't miss the first event on o
#df1 = pd.DataFrame(df1) 
#df1.columns = ['Frame', 'Event'] # name columns - may need to add ['Adj_Index']
#df1 = df1.reset_index() #moves the index over - #df1 = df1.reset_index() # may need a second one to recalibrate index to index_0
#df1 = df1.drop(columns='index')

# %% If you still need to stitch together videos use the following template to process

#Load old data if being used

#df1b = pd.read_csv((r'C:\Users\User\Desktop\export_dataframe_df1b_00' + str(par) + '.csv'), sep=',') # 
#df1b.columns = ['Frame', 'Event'] # name columns - may need to add ['Adj_Index']
#df1b = df1b.drop([0,0],axis=0) # df1.iloc[1:,] also works
#df1b = df1b.reset_index() #moves the index over - #df1 = df1.reset_index() # may need a second one to recalibrate index to index_0
#df1b = df1b.drop(columns='index')
#df1b.iloc[1:,]

# %% To ensure event labeling accurate load in the data from the pi - Might have to turn events into a dataframe to fit in
#pi_times = pd.read_csv((r'M:\Data\GoPro_Visor\Experiment_1\Pi_Times\\00' + str(par) + '_visual_p3_gopro_visor.csv'), sep=',') # pilot
pi_times = np.genfromtxt((r'M:\Data\GoPro_Visor\Experiment_1\Pi_Times\\00' + str(par) + '_visual_p3_gopro_visor.csv'), delimiter=',')
pi_times = pi_times[0,:]
pi_times = np.delete(pi_times,(0,4))
pi_times = pi_times.astype(int)

#temp_diff = df1.diff() # take the difference vertically to find the time gap between each event
#df1 = df1.drop(temp_diff[10 > temp_diff.Time < 0.5].index) # This will get rid of double detections (events within 0.2 seconds of each other)

# Add into the camera time dataframe
df1['Event_pi'] = pi_times[0:len(df1.index)]
df1 = df1.drop(df1[(df1.Event_pi == 3)|(df1.Event_pi == np.nan)|(df1.Event_pi == 4)].index) # With the first event aligned - drop any event 3's according to the pi_times
df1 = df1.drop([0]) # With the first event aligned - drop any event 3's according to the pi_times
df1 = df1.reset_index() # resets index after removing events
df1 = df1.drop(columns='index')

# Take out any remain outliers
temp_diff = df1.diff() # take the difference vertically to find the time gap between each event
df1 = df1.drop(temp_diff[(temp_diff.Time < 1.5)].index) # |((temp_diff.Time[2:-1] > 3)&(temp_diff.Time[2:1] < 7)) # This will get rid of double detections (events within 0.2 seconds of each other)
df1 = df1.reset_index() #moves the index over - #df1 = df1.reset_index() # may need a second one to recalibrate index to index_0
df1 = df1.drop(columns='index')
# %% Load in EEG times

filename = 'M:\Data\GoPro_Visor\Experiment_1\EEG_Data\\00' + str(par) + '_GoPro_Visor_Eye_Pi.vhdr' # pilot
raw = mne.io.read_raw_brainvision(filename, preload=True)
#raw.add_events = Targ_Std_fin.values
df2 = mne.find_events(raw) # outputs a numpy.ndarray
df2 = np.insert(df2,0,[0],axis = 0) #shift data one row down from the top so we don't miss the first event on o
df2 = pd.DataFrame(data=df2[1:,1:], index=df2[1:,0], columns=df2[0,1:])   # change to a pandas DataFrame
df2 = df2.reset_index() 
df2.columns = ['eeg_times', 'Empty', 'Event_Type'] # name columns
df2 = df2.drop(columns='Empty') # get rid of empty column
# align the MNE database event timings from the first target
df2['eeg_times'] = (df2['eeg_times'] - df2['eeg_times'][0]) * 0.001 # subtract all from start trigger (beginning of the first red flash) + convert to seconds

criteria_1 = df2['Event_Type'] == 1 
criteria_2 =  df2['Event_Type'] == 2
criteria_all = criteria_1 | criteria_2 # either/or event defined above
df2 = df2[criteria_all]
df2 = df2.reset_index() # resets index after removing events
df2 = df2.drop(columns='index')



# %% Plotting (Latency/Difference, Raw/Transformed(all point, 2-point, long-tailed), scatter/line/historgrams)

# %% RAW CAMERA TIMES
# Combine EEG and Camera Times/Events into one dataset
df3 = df1.join(df2) # join eeg_times to pi_times
df3 = df3.reset_index()
df3['Difference'] = df3['eeg_times'] - df3['Time']
df3 = df3.drop(columns='index')
df3 = df3.dropna()

##if diff_outlier == 1 # # Need to take out an outlier? Remember to reset indices
#temp_df_diff = df3.diff()
#df3 = df3.drop(df3.Difference[(abs(df3.Difference) > 5)].index) # if there are still a few outliers - take them out with the following line
#df3 = df3.reset_index()
#df3 = df3.drop(columns='index')
##df3 = df3.drop(columns='level_0')
#df3.eeg_times = df3.eeg_times.shift(-1) # if the start is offset - push it up and drop the misalinged
#
## Manual Adjust
#df3['eeg_times'][247:-2] = df3['eeg_times'][249::]
##    df3 = np.append(df3, np.zeros((3,6)), axis=0)
#df3 = np.insert(df2,0,[0],axis = 0) #shift data one row down from the top so we don't miss the first event on o
#df3 = df3.dropna()
#df3 = df3.reset_index()
#    


# any remaining offset are missed frames
# find the remaining offsets and readjust to the mean
#df3['Difference'][248:-1].index = df3['Difference'][248:-1].index+1

#Targ_Std_fin = df1.drop(Targ_Std_diff[Targ_Std_diff.Time < 0.2].index)

# Latency plot
plt.close('all')
plt.figure(0)
plt.plot(df3['Time'], df3['index'], 'k--', label='Pi Times')
plt.plot(df3['eeg_times'], df3['index'], 'ko', label='EEG Times')
plt.xlabel('Latency (Seconds)')
plt.ylabel('Trial Number')
plt.title('Trial Number vs Latency -  Par_00{}'.format(par))
legend = plt.legend(loc='upper center', shadow=True, fontsize='x-large')
legend.get_frame().set_facecolor('C0')
plt.show()

# Difference plot
plt.figure(1)
plt.plot(df3['Difference'], df3['index'], label='EEG - Pi')
legend = plt.legend(loc='upper left', shadow=True, fontsize='x-large')
plt.xlabel('Latency (Seconds)')
plt.ylabel('Trial Number')
plt.title('Trial Number vs Difference - Par_00{}'.format(par))
plt.show()

# Histogram Plots
# Event Latency
# EEG
df3['EEG Times (s)'] = df3['eeg_times']
plt.figure(figsize=(15,10))
plt.tight_layout()
plt.title('EEG Event Latency Distribution - Par_00{}'.format(par))
plt.ylabel('Number of Trials')
sns.distplot(df3['EEG Times (s)'])
# Camera
df3['Camera Times (s)'] = df3['Time']
plt.figure(figsize=(15,10))
plt.tight_layout()
plt.title('Camera Event Latency Distribution - Par_00{}'.format(par))
plt.ylabel('Number of Trials')
sns.distplot(df3['Camera Times (s)'])
# Difference
plt.figure(figsize=(15,10))
plt.tight_layout()
plt.title('EEG-Camera Difference Distribution - Par_00{}'.format(par))
plt.ylabel('Number of Trials')
sns.distplot(df3['Difference'])




# %% ## Transforms - LinearRegression().fit(X, y) X=Training data (camera times), y=Target Values (eeg times)

# %% ## All Point Transform 

# Prep Data
trials = 434
df4 = df3.copy() # copy DataFrame 
df4 = df4.values # convert from Pandas DataFrame to a numpy structure
df4 = np.append(df4, np.zeros((trials,3)), axis=1)
X1 = df4[:,1].reshape(-1,1)
y1 = df4[:,4].reshape(-1,1)

#Equate and Test Regression
model1 = LinearRegression()
reg =  model1.fit(X1,y1) # From the pi times we are predicting the eeg times
reg.score(df4[:,1].reshape(-1,1), df4[:,4].reshape(-1,1))
df4[:,6] = df4[:,1]*reg.coef_ + reg.intercept_  # eeg times = camera_times X slope of 
df4[:,7] = df4[:,4]-df4[:,6]
# 1:index , 2:pi times, 3:pi events, 1:eeg_times, 2:eeg_trig 5:difference, 6:transformed difference, 7:difference between original difference and transformed difference

# All Point Transform 
# Difference plots
# Line Plot
plt.figure(123)
plt.plot(df4[:,7], df4[:,0])
#plt.plot(df4[:,10], df4[:,0]) #plot the magnitude of the difference 
#plt.plot(df3['Difference'], df3['level_0'], label='EEG - Pi') # plot untransformed
plt.legend('EEG - Pi', ncol=2, loc='upper left'); #  scalex=True, scaley=True if not using a custom xticks arguement
plt.xlabel('Latency (miliseconds)')
plt.ylabel('Trial Number')
plt.title('Trial Number vs Transformed Difference - Par_00{}'.format(par))
#plt.xlim([-0.00001, 0.00001])
plt.show()

# Distribution
plt.figure(figsize=(15,10))
plt.tight_layout()
plt.title('EEG-Camera Difference Distribution - Par_00{}'.format(par))
plt.ylabel('Number of Trials')
plt.xlabel('Difference (seconds)')
sns.distplot(df4[:,7], rug = True, rug_kws={'color': 'black'})





# %% Two Point Transform

# Prep Data - incl. construct Cap Structures
df5 = df3.copy() # copy DataFrame 
df5 = df5.values # convert from Pandas DataFrame to a numpy structure
df5 = np.append(df5, np.zeros((trials,3)), axis=1)
X2 = df5[:,1].reshape(-1,1) # pi_times first and last
y2 = df5[:,1].reshape(-1,1) # eeg first & last

#Equate and Test Regression
model1 = LinearRegression()
reg =  model1.fit(X,y) # From the pi times we are predicting the eeg times
reg.score(df5[:,1].reshape(-1,1), df5[:,3].reshape(-1,1))
df5[:,6] = df5[:,1]*reg.coef_ + reg.intercept_  # eeg times = camera_times X slope of 
df5[:,7] = df5[:,3]-df5[:,6]
# 1:index , 2:pi times, 3:pi events, 1:eeg_times, 2:eeg_trig 5:difference, 6:transformed difference, 7:difference between original difference and transformed difference


# All Point Transform 
# Difference plots
# Line Plot
plt.figure(123)
plt.plot(df4[:,7], df5[:,0])
#plt.plot(df4[:,10], df4[:,0]) #plot the magnitude of the difference 
#plt.plot(df3['Difference'], df3['level_0'], label='EEG - Pi') # plot untransformed
plt.legend('EEG - Pi', ncol=2, loc='upper left'); #  scalex=True, scaley=True if not using a custom xticks arguement
plt.xlabel('Latency (miliseconds)')
plt.ylabel('Trial Number')
plt.title('Trial Number vs Transformed Difference {}'.format(par))
#plt.xlim([-0.00001, 0.00001])
plt.show()

# Distribution
plt.figure(figsize=(15,10))
plt.tight_layout()
plt.title('EEG-Camera Difference Distribution - Par_00{}'.format(par))
plt.ylabel('Number of Trials')
plt.xlabel('Difference (seconds)')
sns.distplot(df5[:,7], rug = True, rug_kws={'color': 'black'})





# %% Transform based on a linear regression based off of a 10 event tail (ignoring event type)

# Prep Data - incl. construct Tail Structures
df6 = df3.copy() # copy DataFrame 
df6 = df6.values # convert from Pandas DataFrame to a numpy structure
df6 = np.append(df6, np.zeros((trials,3)), axis=1) 

1X3 = df6[0:10,3:5] # Pull out first 10 event from camera
2X3 = df6[190:-1,3:5] # Pull out first 10 event from camera

#1X3[:,1] = np.around(X3[:,1]), 
#1X3.astype(float) 
#2X3[:,1] = np.around(y3[:,1]), 
#2X3.astype(float)
#1X3 = 1X3.reshape(-1,1)
#2X3 = 2X3.reshape(-1,1)
X3 = np.concatenate(1X3, 2X3) # Combine first and last 10

1y3 = df6[0:10,3:5] # Pull out first 10 event from camera
2y3 = df6[190:-1,3:5] # Pull out first 10 event from camera

#1y3[:,1] = np.around(1y3[:,1]), 
#1y3.astype(float) 
#2y3[:,1] = np.around(2y3[:,1]), 
#2y3.astype(float)
#1y3 = 1y3.reshape(-1,1)
#2y3 = 2y3.reshape(-1,1)
y3 = np.concatenate(1y3, 2y3) # Combine first and last 10


#Equate and Test Regression
model1 = LinearRegression()
reg =  model1.fit(X3,y3) # From the pi times we are predicting the eeg times
reg.score(df6[:,1].reshape(-1,1), df6[:,3].reshape(-1,1))
df6[:,6] = df6[:,1]*reg.coef_ + reg.intercept_  # eeg times = camera_times X slope of 
df6[:,7] = df6[:,3]-df6[:,6]
# 1:index , 2:pi times, 3:pi events, 1:eeg_times, 2:eeg_trig 5:difference, 6:transformed difference, 7:difference between original difference and transformed difference


# All Point Transform 
# Difference plots
# Line Plot
plt.figure(123)
plt.plot(df4[:,7], df4[:,0])
#plt.plot(df4[:,10], df4[:,0]) #plot the magnitude of the difference 
#plt.plot(df3['Difference'], df3['level_0'], label='EEG - Pi') # plot untransformed
plt.legend('EEG - Pi', ncol=2, loc='upper left'); #  scalex=True, scaley=True if not using a custom xticks arguement
plt.xlabel('Latency (miliseconds)')
plt.ylabel('Trial Number')
plt.title('Trial Number vs Transformed Difference {}'.format(par))
#plt.xlim([-0.00001, 0.00001])
plt.show()

# Distribution
plt.figure(figsize=(15,10))
plt.tight_layout()
plt.title('EEG-Camera Difference Distribution - Par_00{}'.format(par))
plt.ylabel('Number of Trials')
plt.xlabel('Difference (seconds)')
sns.distplot(df4[:,7], rug = True, rug_kws={'color': 'black'})

#%% Comparison of Difference between EEG and Camera Times after each Type of Transforms and Raw
Raw_Diff_Sum = sum(abs(df3['Difference']))
All_Point_Sum = 
Two_Point_Sum = 
Ten_Tail_Sum = 

