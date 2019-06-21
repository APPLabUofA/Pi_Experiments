import numpy as np
import cv2
import time

def equalizeHistColor(frame):
    # equalize the histogram of color image
    img = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)  # convert to HSV
    img[:, :, 2] = cv2.equalizeHist(img[:, :, 2])  # equalize the histogram of the V channel
    return cv2.cvtColor(img, cv2.COLOR_HSV2RGB)  # convert the HSV image back to RGB format

#Booleans
Edge_Smooth_TF = True
colour_TF = False
File_type = True # changes data save structure if playing with contours or line finding = True, else False
# overlay_TF = True
# Thresholding_TF = True
# Contour_TF = True
Main_Action = 2 # 0 for overlay_TF, 1 for Thresholding_TF, , 2 for Contours_TF


# Define the file being loaded
Version = ''
Base_Name = 'output' #what we are saving new file as
Name_of_File = Base_Name + Version
format = '.avi'
fileName = Name_of_File + format

# Define the write function - name & video proerties
Version = '_007'
Base_Name = 'output' #what we are saving new file as
Name_of_File = Base_Name + Version
format = '.avi'
fileName_Write = Name_of_File + format  # change the file name if needed
imgSize=(640,480)
frame_per_second=30.0
if File_type == True:
    writer = cv2.VideoWriter(fileName_Write, cv2.VideoWriter_fourcc(*"MJPG"), frame_per_second,imgSize,False)
else:
    writer = cv2.VideoWriter(fileName_Write, cv2.VideoWriter_fourcc(*"MJPG"), frame_per_second, imgSize)

# Manipulation Variables,
kernelSize = 21
GB_Kernel = 21
# Edge Detection Parameter
parameter1=20
parameter2=60
intApertureSize=1

# Colours
custom_color_list = []
custom_color_list = ["COLOR_BGR2RGB", "COLOR_RGB2BGR", "COLOR_BGR2GRAY", "COLOR_RGB2GRAY", "COLOR_BGR2HSV", "COLOR_RGB2HSV",
 "COLOR_RGB2HLS", "COLOR_BGR2HLS", "COLOR_BGR2XYZ", "COLOR_RGB2XYZ", "COLOR_BGR2Lab", "COLOR_RGB2Luv"]
custom_color_type = 1 # 1-12 - look at elements in custom_color_list

## frame dimensions (x,y) & img dimensions (2x,2y)
scaling_factorx=1
scaling_factory=1
scaling_factor2x=1
scaling_factor2y=1
# Thresholding
threshold1=100
threshold2=200
# Contours
color=(255,0,0)
thickness=2


cap = cv2.VideoCapture('output.avi')  # load the video - input the name of the file we are pulling from - needs to be in same folder if in the 'filename.format' format
if Main_Action == 1:
    while (cap.isOpened()):  # play the video by reading frame by frame
        ret, frame = cap.read()
        if ret == True:
            # equalize the histogram of color image
            frame1 = equalizeHistColor(frame)
            gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (GB_Kernel, GB_Kernel), 0)

            # ret, mask = cv2.threshold(blur, threshold1, threshold2, cv2.THRESH_BINARY)
            ret, mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # ret, mask = cv2.threshold(blur,threshold1, threshold2,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            # mask = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,2)
            # mask = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.erode(mask, kernel, iterations=7)  # morphology erosion
            mask = cv2.dilate(mask, kernel, iterations=5)  # morphology dilation

            mask_inv = cv2.bitwise_not(mask)
            img = cv2.bitwise_and(frame1, frame1, mask=mask_inv)
            img = cv2.addWeighted(frame1, 0.1, img, 0.9, 0)
            # img=mask

            # Display the resulting image
            writer.write(img)  # save the frame into video file
            cv2.imshow('Original', frame)  # show the video
            cv2.imshow('New', img)
            if cv2.waitKey(1)& 0xFF == ord('q'):
                break
        else:
            print("ref != True")
            break
        # When everything done, release the capture
    writer.release()
    cap.release()
    cv2.destroyAllWindows()
elif Main_Action == 2:
    while (cap.isOpened()):  # play the video by reading frame by frame
        # Capture frame-by-frame
        ret, frame = cap.read()  # ret = 1 if the video is captured; frame is the image

        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # blur = cv2.GaussianBlur(gray,(21,21),0)
        ret, thresh = cv2.threshold(gray, 100, 150, cv2.THRESH_BINARY_INV)
        img1, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        if len(contours) != 0:
            c = max(contours, key=cv2.contourArea)  # find the largest contour
            x, y, w, h = cv2.boundingRect(c)  # get bounding box of largest contour
            img2=cv2.drawContours(frame, c, -1, color, thickness) # draw largest contour
            # img2 = cv2.drawContours(frame, contours, -1, color, thickness)  # draw all contours
            img3 = cv2.rectangle(img2, (x, y), (x + w, y + h), (0, 0, 255), 2)  # draw red bounding box in img

        # Display the resulting image
        cv2.imshow('Contour', img3)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # press q to quit
            break

    # When everything done, release the capture
    writer.release()
    cap.release()
    cv2.destroyAllWindows()
