import numpy as np
import cv2
import math

# -------- Read and process image --------
# Read
img = cv2.imread('lane-2.jpg')
# Grayscale
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# Smooth
img_gray = cv2.GaussianBlur(img_gray, (59,59), 0)

# -------- Mask irrelevant part (top one-third?) of the image --------
# # Create the mask base (all black)
# mask = np.zeros(img_gray.shape, dtype='uint8')
# # Draw a white, filled rectangle on bottom of the mask image
# height, width = img_gray.shape
# cv2.rectangle(mask, (0, int(height/3)), (width-1, height-1), (255, 255, 255), -1)
# cv2.imwrite('mask.jpg', mask)
# # Apply mask to the image
# img_gray = cv2.bitwise_and(img_gray, img_gray, mask=mask)

# -------- Binarize image (to B/W) --------
ret, img_thresh = cv2.threshold(img_gray, 60, 255, cv2.THRESH_BINARY_INV)
img_thresh = 255 - img_thresh

# -------- Line detection --------
# Get contours
img_thresh, img_contours, hierarchy = cv2.findContours(img_thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(img, img_contours, -1, (0,255,0), 3)
print(hierarchy)
cv2.imwrite('contours.jpg', img)
# TODO: Use HoughLines to extract track lines from contour?