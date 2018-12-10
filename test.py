import cv2
import numpy as np
import math
import line_grouping

img = cv2.imread('lane-2.jpg')
img2 = cv2.imread('lane-2.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

cv2.imwrite('gray.jpg', gray)

high_thresh, thresh_im = cv2.threshold(
    gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
lowThresh = 0.5 * high_thresh

edges = cv2.Canny(gray, 300, 500)
dilated = cv2.dilate(edges, np.ones((4, 4), dtype=np.uint8))
cv2.imwrite('canny.jpg', dilated)

# Mask
mask = np.zeros(dilated.shape, dtype='uint8')
# Draw white rectangle
height, width = dilated.shape
cv2.rectangle(mask, (0, int(height/2.5)), (width-1, int(height-(height/5))), (255, 255, 255), -1)
# Apply mask to the image
dilated = cv2.bitwise_and(dilated, dilated, mask=mask)

minLineLength = 100
maxLineGap = 10
lines = cv2.HoughLinesP(
    dilated,
    rho=1,
    theta=np.pi / 180,
    threshold=250,
    minLineLength=400,
    maxLineGap=20)
for line in lines:
    for x1, y1, x2, y2 in line:
        cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
cv2.imwrite('hough.jpg', img)


# merge lines

# ------------------
# prepare
_lines = []
for _line in line_grouping.get_lines(lines):
    _lines.append([(_line[0], _line[1]), (_line[2], _line[3])])

# sort
_lines_x = []
_lines_y = []
for line_i in _lines:
    orientation_i = math.atan2(
        (line_i[0][1]-line_i[1][1]), (line_i[0][0]-line_i[1][0]))
    if (abs(math.degrees(orientation_i)) > 45) and abs(math.degrees(orientation_i)) < (90+45):
        _lines_y.append(line_i)
    else:
        _lines_x.append(line_i)

_lines_x = sorted(_lines_x, key=lambda _line: _line[0][0])
_lines_y = sorted(_lines_y, key=lambda _line: _line[0][1])

merged_lines_x = line_grouping.merge_lines_pipeline_2(_lines_x)
merged_lines_y = line_grouping.merge_lines_pipeline_2(_lines_y)

merged_lines_all = []
merged_lines_all.extend(merged_lines_x)
merged_lines_all.extend(merged_lines_y)
print("process groups lines", len(_lines), len(merged_lines_all))


for line in merged_lines_all:
    cv2.line(img2, (line[0][0], line[0][1]),
             (line[1][0], line[1][1]), (0, 0, 255), 6)
'''
for line in merged_lines_all:
    for x1, y1, x2, y2 in line:
        cv2.line(img2, (x1, y1), (x2, y2), (0, 255, 0), 2)
'''
cv2.imwrite('merged.jpg', img2)
