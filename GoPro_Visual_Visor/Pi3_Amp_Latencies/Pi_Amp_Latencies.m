ccc

trials = 250;
blocks = 1;

%%%Now we will go through the EEG file and determine our latencies%%%
filepath = ['M:\Data\GoPro_Visor\Pi_Amp_Latency_Test'];
filename = ['testing_visor_pi_012.vhdr'];

[ALLEEG EEG CURRENTSET ALLCOM] = eeglab;
EEG = pop_loadbv(filepath, filename, [], []);
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 0,'setname','timingtest','gui','off');

start_trigger = ALLEEG(1).event(2).latency;
EEG_latencies = zeros(1,trials);
EEG_latencies = [];
EEG_latency = 0;

% for i_event = 3:(length(ALLEEG(1).event)-1)
%     if EEG.event(i_event).type(4) == '1' || EEG.event(i_event).type(4) == '2'
%         EEG_latencies(1,i_event-2) = (EEG(1).event(i_event).latency - start_trigger)/ALLEEG.srate;
%         EEG_latencies(2,i_event-2) = EEG.event(i_event).type(4);
%     else
%         EEG_latencies(i_event-2) = 0;
%     end
% end

% Tigger Meanings
% 1 Standard Onset 
% 2 Target Onset
% 3 Standard Response
% 4 Target Response
% 5 Standard Offset
% 6 Target Offset
% 10 Block Start
% 11 Block End
% 12 Experiment Start
% 13 Experiment End

for i_event = 3:(length(ALLEEG(1).event)-1) % skips the first two and the last 1
    if ALLEEG(1).event(i_event).type(4) == '1' || ALLEEG(1).event(i_event).type(4) == '2' % only adds the onset of standards and targets to a list called latency
        EEG_latency = (ALLEEG(1).event(i_event).latency - start_trigger)/ALLEEG.srate;
        EEG_latencies(county) = EEG_latency;
    end
end

%%%now let's load the times recorded by the pi%%%
%%%need to subtract 5 from these since there is 5 seconds before
%%%the red LEDs, indicating the start, are turned on%%%
% % % trig_type,trig_time, delay_length, trial_resp, jitter_length, first_light_difference, second_light_difference
pi_recorded_times = readcsv('C:\Users\User\Documents\GitHub\GoPro_Visor_Pi\Pi3_Amp_Latencies\Pi_Time_Data\011_visual_p3_gopro_visor.csv',1,0,[1,0,6,trials]);

%%% pi_recorded_times = pi_recorded_times - 5;
pi_type = pi_recorded_times(1,:); % trig type - 1 is standard 2 is target
pi_latency = pi_recorded_times(2,:); % trig time latency
pi_delay = pi_recorded_times(3,:); % delay length
pi_resp = pi_recorded_times(4,:); % trial resp
pi_jitter = pi_recorded_times(5,:); % jitter length
pi_start_stop = pi_recorded_times(6,:); % resp_latency
all_latencies(1,:) = EEG_latencies;
all_latencies(2,:) = pi_latency;

conditions = {'EEG','Pi Times'};

%%%plot the latency of both pi and amp
figure;hold on;
colours = ['k','b'];

plot(all_latencies(i_plot,:),[1:trials],'color',colours(i_plot));
    
xlabel('Time (Seconds)');ylabel('Trial');legend('EEG','Pi Times');
hold off;

%%%now let's plot each of our difference latencies%%%
conditions = {'EEG - Pi Times'};

figure;hold on;
colours = ['k','b'];

plot(all_latencies(1,:)-all_latencies(2,:),[1:trials],'color',colours(i_plot));

%%% GoPro linear regression 
%%%mdl = LinearModel.fit(all_latencies(2,:),all_latencies(1,:),'linear'); %%% confirm what's a happen!
mdl = fitlm(all_latencies(2,:),all_latencies(1,:),'linear'); %%% confirm what's a happen! - transforming the pi times to the eeg times

xlabel('Time (Seconds)');ylabel('Trial');legend('EEG - Pi Times');
hold off;




