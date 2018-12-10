import track_lanes
import cv2

# Open the image and get the track lanes
img = cv2.imread('images/lane-2.jpg')
trackLanes = track_lanes.get_track_lanes(img)

# get the startLine from the list and then remove
startLine = trackLanes[0]
del trackLanes[0]

# draw the startLine
cv2.line(img, (startLine[0][0], startLine[0][1]),
         (startLine[1][0], startLine[1][1]), (0, 255, 255), 6)

# draw all the other lines
for line in trackLanes:
    x1 = line[0][0]
    y1 = line[0][1]
    x2 = line[1][0]
    y2 = line[1][1]
    cv2.line(img, (x1, y1),
             (x2, y2), (0, 0, 255), 6)

# write the final image
cv2.imwrite('images/merged.jpg', img)
