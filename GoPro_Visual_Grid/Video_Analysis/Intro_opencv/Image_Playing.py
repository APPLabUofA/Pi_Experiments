# import numpy as np
# import cv2
# from matplotlib import pyplot as plt
#
# gray_img = cv2.imread('C:\Users\User\Desktop\people.jpg', cv2.IMREAD_GRAYSCALE)
# # cv2.imshow('People',gray_img)
# # img = cv.imread('C:\Users\User\Desktop\people.jpg',0)
#
# hist,bins = np.histogram(gray_img,256,[0,256])
#
# cdf = hist.cumsum()
# cdf_normalized = cdf * float(hist.max()) / cdf.max()
# plt.plot(cdf_normalized, color = 'b')
# plt.hist(gray_img,256,[0,256], color = 'r')
# plt.xlim([0,256])
# plt.legend(('cdf','histogram'), loc = 'upper left')
# plt.show()


import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
img = cv.imread('wC:\Users\User\Desktop\people.jpg',0)
hist,bins = np.histogram(img,256,[0,256])
cdf = hist.cumsum()
cdf_normalized = cdf * float(hist.max()) / cdf.max()
plt.plot(cdf_normalized, color = 'b')
plt.hist(img,256,[0,256], color = 'r')
plt.xlim([0,256])
plt.legend(('cdf','histogram'), loc = 'upper left')
plt.show()