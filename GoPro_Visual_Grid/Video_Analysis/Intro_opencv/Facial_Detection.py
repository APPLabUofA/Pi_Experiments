import numpy as np
import cv2

folder = 'C:/Users/eredm/PycharmProjects/GoPro/venv/Lib/site-packages/cv2/data/'
face_casc = cv2.CascadeClassifier(folder + 'haarcascade_frontalface_default.xml')
eye_casc = cv2.CascadeClassifier(folder + 'haarcascade_eye.xml')

color = (0, 255, 0)
thickness = 3

cap = cv2.VideoCapture(0)
while (True):
    # Capture frame-by-frame
    ret, frame = cap.read()  # ret = 1 if the video is captured; frame is the image

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    faces = face_casc.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3)

    img = frame  # default if face is not found
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + w]
        # img=cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness) # box for face
        eyes = eye_casc.detectMultiScale(roi_gray)
        for (x_eye, y_eye, w_eye, h_eye) in eyes:
            center = (int(x_eye + 0.5 * w_eye), int(y_eye + 0.5 * h_eye))
            radius = int(0.3 * (w_eye + h_eye))
            img = cv2.circle(roi_color, center, radius, color, thickness)
            # img=cv2.circle(frame,center,radius,color,thickness)

    # Display the resulting image
    #cv2.imshow('Face Detection Harr', img)
    cv2.imshow('Original', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # press q to quit
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()