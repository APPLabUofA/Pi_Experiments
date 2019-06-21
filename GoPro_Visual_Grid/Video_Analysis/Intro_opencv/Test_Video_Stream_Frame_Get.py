# import numpy as np
import cv2

cap = cv2.VideoCapture('003_camera_p3.MP4')  # video_name is the video being called
cap.set(1, 1000)  # Where frame_no is the frame you want
ret, frame = cap.read()  # Read the frame
cv2.imshow('window_name', frame)  # show frame on window

# amount_of_frames = cap.get(cv2.CV_CAP_PROP_FRAME_COUNT)

while True:
    ch = 0xFF & cv2.waitKey(1)  # Wait for a second
    if ch == 27:
        break


# start_eeg = 652;
# door_closed = 4800;
# start_flash = 8897;

