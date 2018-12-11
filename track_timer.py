import track_lanes
import numpy as np
import cv2
from yolo_cv import YoloCV

cap = cv2.VideoCapture('images/test-start.mp4')
#cap = cv2.VideoCapture('images/finish-lane1and2.mp4')

# The following code is for saving a video of the current setup
'''rate = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print('Frame Rate')
print(rate)

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'MPEG')
out = cv2.VideoWriter('images/output_tracklines.avi',
                      fourcc, rate, (width, height))
'''

tracklanes = []
startLine = []
count = 0
yoloCVObj = YoloCV()

currentPredictedBoxes = []
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Open the image and get the track lanes
    # img = cv2.imread('images/lane-2.jpg')

    # get the tracklanes for the image if this is our first frame, otherwise
    # we don't need to regenerate them and can just use the old ones
    if(count < 1):
        trackLanes = track_lanes.get_track_lanes(frame)

        # get the startLine from the list and then remove
        startLine = trackLanes[0]
        del trackLanes[0]

    # write the final image
    #cv2.imwrite('images/merged_video.jpg', frame)
    if(count % 3 == 0):
        currentPredictedBoxes = yoloCVObj.getPrediction(frame)
        print(currentPredictedBoxes)

    for box in currentPredictedBoxes:
        yoloCVObj.draw_prediction(frame, round(box['x']), round(
            box['y']), round(box['x'] + box['w']), round(box['y'] + box['h']), box['class_id'])

    # draw the startLine
    cv2.line(frame, (startLine[0][0], startLine[0][1]),
             (startLine[1][0], startLine[1][1]), (0, 255, 255), 6)

    # draw all the other lines
    for line in trackLanes:
        x1 = line[0][0]
        y1 = line[0][1]
        x2 = line[1][0]
        y2 = line[1][1]
        cv2.line(frame, (x1, y1),
                 (x2, y2), (0, 0, 255), 6)

    # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    count += 1

    # Write out the video frame here
    # out.write(frame)

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
