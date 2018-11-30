import cv2
import numpy as np

img = cv2.imread('lane-2.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

cv2.imwrite('gray.jpg', gray)

high_thresh, thresh_im = cv2.threshold(
    gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
lowThresh = 0.5 * high_thresh

edges = cv2.Canny(gray, 200, 500)
dilated = cv2.dilate(edges, np.ones((3, 3), dtype=np.uint8))
cv2.imwrite('canny.jpg', dilated)

minLineLength = 100
maxLineGap = 10
lines = cv2.HoughLinesP(
    dilated,
    rho=6,
    theta=np.pi / 180,
    threshold=1000,
    minLineLength=400,
    maxLineGap=5)
for line in lines:
    for x1, y1, x2, y2 in line:
        cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
cv2.imwrite('hough.jpg', img)
