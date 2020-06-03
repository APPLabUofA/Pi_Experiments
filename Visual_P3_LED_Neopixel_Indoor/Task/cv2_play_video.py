import cv2
import numpy as np
import time

file_name = "/home/pi/research_experiments/Experiments/Visual_P3_LED_Neopixel_Indoor/Task/Bike_Video.mp4"
window_name = "window"
interframe_wait_ms = 24

cap = cv2.VideoCapture(file_name)
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

cv2.namedWindow(window_name, cv2.WINDOW_FULLSCREEN)
cv2.setWindowProperty(window_name, cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)

start_exp = time.time()

while (time.time() - start_exp <= 10):
    ret, frame = cap.read()
    if not ret:
        print("Reached end of video, exiting.")
        break

    cv2.imshow(window_name, frame)
    if cv2.waitKey(interframe_wait_ms) & 0x7F == ord('q'):
        print("Exit requested.")
        break

cap.release()
cv2.destroyAllWindows()
