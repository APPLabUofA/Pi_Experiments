# Open world EEG

## General

Completely self-contained  
Goals start indoors and move outside
Pi is running everything - a tablet recording 
Visor = LEDs + safety glasses

Prototype 1 
Visor + button + EEG
Compare the latencies

A given trial consist of:
1. random delay period, then
2. 1 second flash, then
1 second of 


## Experiment 1
### Visor + button + EEG

### Task 1:  indoor, sitting down, fixation cross (otherwise blank screen)
Visor blink, two conditions (1 w/o response, 1 w/ resp) * should get comparable P3 w/o

pilot - 1000 trials 

study - 500 trials each condition (1 w/o response, 1 w/ resp)  - ~12 participants 

#### Jon_Blink.py

### Task 2:  indoor, sitting down, fixation cross  + MP4 Video File (Task 2)
Visor blink, two conditions (1 w/o response, 1 w/ resp) * should get comparable P3 w/o
Video in background either a busy scene or a park scene (w/o kids)
Test 24-30 fps on the pi + viewpixx monitor
Try custom build - Ask Kyle at this point - Custom build ($300-$400) vs. Premade (20,000-50,000)

#### Scripts
#### OpenCv_Pi_Visor.py
Trigger the video stream with markers of distinguishable stimuli as it enters the peripheral and focal view

#### MP4_Convert.txt (Terminal Command)
taking the ~250 fps video stream, reducing it to ~ 24 fps and embedding/drawing a fixation cross in the center, marking frames with onset triggers and triggering stimuli within the video (50 hours of work) - Using OpenCV/FFMPEG/pygame

#### Open Questions
- Decide w/w/o audio (Task 2.5)
- Relate Task 1 and Task 2 and the interference based on extraneous video stream oddballs
(break down the identification of vehicles into 10 major categories and correlate with EEG principle components)
- These tasks allow us to decide whether to continue with button response and/or focuses of  attention to certain aspects of the environment, or just free wandering

## Experiment 2
Visor + button + EEG + MP4 Video File + Eye Tracking (Home made rig?)

### Task 1: Task 2 + eye tracking (w/ w/o fixation cross)
Preliminary 1 - just eye tracking plus video
Preliminary 2 - + EEG
regression of eye movement + eye blink - based on eye tracking

GoPro instead of ViewPixx (still indoors)
## Experiment 3
Visor + button + EEG + MP4 Video File + Eye Tracking (Home made rig?) + Binocular external video stream (3D Mapping)
Outside walking
Depth Perception Test?

### Task 1: Walk/Bike down sask drive /across the river (in different contexts)
