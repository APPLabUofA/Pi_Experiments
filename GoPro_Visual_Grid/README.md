# GoPro_Grid_Pi

End Goal
biking outside - remote, controlled stim (lights), no eye tracking needed because this is focused around the visual P3 task

End Results
- (2) Pi3(s) [two-way communication]
- (1) Iphone [can hold a charge while providing a local WAP HUB for several hours]
- EEG Cap [active]
- Vamp
- Button for response with state monitoring

## Experiment 1
 1 Pi - lots of cords 

[Pi 3 B+, both on the way]

### Experiment 2
2 Pi - wired

### Experiment 3 
Pis talking through ethernet

### Experiment 4
Pis talking through WAP HUB (Iphone?)

no-button

Static Pi IP

### Experiment 5 
WAP w/ button + state monitoring/updates

- Pi1 turns on pin of Pi2 to indicate target or standard
- Pi2 only responds to button press if state is on (target) - works as long as jitter maxes within reasonable time - can’t not have responses recorded past ~ 50 ms

### Prototype 6
Add GoPro + everything together

Triggering - for each event Pi1 pings Pi2 immediately before LED and again immediately after trigger sent. Account for variability in distance

## Experimental Procedure
Syncing Recordings
Start EEG 
Start GoPro
Start Experiment (Turn grid all red & send trigger to amp via Pi1 to Pi2 link (with Pings))
Experiment is a simple visual oddball of green standards and blue targets (press button)
End Experiment (in the same fashion)


## Analysis 

**Base Video Processing Components** (OpenCV)
- Trim Start
- Gaussian Blur
- Thresholding 
- Compression/Contraction
*Outputs*
- List of [frame + start event trigger] (where the max[index] = corresponds with the last EEG event)
- List of [frame + end event trigger]
- List of [frame + trigger state] (0 B + G channels below thresholds, 1 above B channel threshold, 2 above R channel threshold
	- Eventually will output an ~[-1,1] video epoch to be the raw input for deep learning
	
V1
- Basic Geometric classifiers (cv2.PolyApprox)
	- Once contour is identified --> constructing into separate channels RGB
	- using dynamic thresholding of Blue and Green channels ratioed to background lighting (RBG Channeling)
	
V2
- Basic Object Contour Tracking (Motion Detection by Image Difference)
**and**
- Basic Geometric classifiers (cv2.PolyApprox) within bounded contours (circles)
**or**
- Hough Circle Detection

V3
- Background/Foreground separation
- Object Tracking
- Perspective Transformation
- Occlusion Procedure
v4
 - Object specific YOLOv3 Classifications

**Combining EEG and Video Components**
- Deep Learning with multimodal inputs of EEG and video YOLOv3 outputs

## Software
Python
- opencv

VLC

FFMPEG
	
## VLC Pre-Preprocessing for finding the start_eeg & approx. trial_start from frame by frame video
(Can interface with ffmpeg)
View>Advanced Controls
Add Interface>Terminal

## Create a video version with embedded frame number
ffmpeg must be installed - 
inputs - ffmpeg.exe location (or set Environmental varaible PATH) & video location
outputs - save location
C:\\Users\\User\\ffmpeg-4.1-win64-static\\bin\\ffmpeg.exe -i ..\003_camera_p3.MP4 -vf "drawtext=fontfile=Arial.ttf: text='%{frame_num}': start_number=1: x=(w-tw)/2: y=h-(2*lh): fontcolor=black: fontsize=20: box=1: boxcolor=white: boxborderw=5" -c:a copy ..\003_camera_p3_imbedded.MP4
