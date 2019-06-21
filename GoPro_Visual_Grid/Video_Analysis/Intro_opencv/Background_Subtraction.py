import numpy as np
import cv2

alpha = 0.999
isFirstTime = True
cap = cv2.VideoCapture(0)
while (True):
    # Capture frame-by-frame
    ret, frame = cap.read()  # ret = 1 if the video is captured; frame is the image
    frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)

    # create background
    if isFirstTime==True:
       bg_img=frame
       isFirstTime=False
    else:
       bg_img = dst = cv2.addWeighted(frame,(1-alpha),bg_img,alpha,0)
    # the above code is the same as:
    fgmask = bg_img.apply(frame)

    # create foreground
    fg_img=cv2.subtract(frame,bg_img)
    fg_img = cv2.absdiff(frame, bg_img)

    # Display the resulting image
    cv2.imshow('Video Capture', frame)
    cv2.imshow('Background', bg_img)
    cv2.imshow('Foreground', fgmask)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # press q to quit
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()