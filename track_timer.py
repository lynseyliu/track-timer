import track_lanes
import get_intersect
import numpy as np
import cv2
from yolo_cv import YoloCV
import argparse
from datetime import datetime

parser = argparse.ArgumentParser(description='Track timer')
parser.add_argument('--mode', default='full', help='start, finish, or full')
parser.add_argument('--runners', default=1, type=int, help='number of runners')
args = parser.parse_args()

#cap = cv2.VideoCapture('images/test-start.mp4')
#cap = cv2.VideoCapture('images/finish-lane1and2.mp4')
cap = cv2.VideoCapture('images/test.mov')

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

started = False
finished = False
waiting = False
startTime = 0
waitTime = 10 #seconds
totalTime = 0

numRunners = args.runners
if args.mode == 'start':
    started = False
elif args.mode == 'finish':
    started = True
    finished = False
elif args.mode == 'full':
    started = False
    finished = False

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
        try:
            currentPredictedBoxes = yoloCVObj.getPrediction(frame)
            print(currentPredictedBoxes)
        except:
            break

    for box in currentPredictedBoxes:
        yoloCVObj.draw_prediction(frame, round(box['x']), round(
            box['y']), round(box['x'] + box['w']), round(box['y'] + box['h']), box['class_id'])

    # Draw all the other lines
    for line in trackLanes:
        x1 = line[0][0]
        y1 = line[0][1]
        x2 = line[1][0]
        y2 = line[1][1]
        cv2.line(frame, (x1, y1),
                 (x2, y2), (0, 0, 255), 6)

    # Draw the startLine
    cv2.line(frame, (startLine[0][0], startLine[0][1]),
             (startLine[1][0], startLine[1][1]), (0, 255, 255), 6)

    if started and (datetime.now() - startTime).total_seconds() > waitTime:
        waiting = False

    if not waiting:
        # Detect bounding box intersection with startLine
        for box in currentPredictedBoxes:
            if get_intersect.box_line(box, startLine) != False:
                p = get_intersect.box_line(box, startLine)
                cv2.circle(frame, (int(p[0]), int(p[1])), 5, (0, 255, 0), thickness=5, lineType=8, shift=0)
                if not started:
                    started = True
                    startTime = datetime.now()
                    waiting = True
                elif not finished:
                    totalTime = datetime.now() - startTime
                    finished = True
                    #cv2.putText(frame, 'Finish', (10, 500), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4, cv2.LINE_AA)

    # Display the resulting frame
    try:
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        count += 1
    except:
        break

    # Write out the video frame here
    # out.write(frame)

if args.mode == 'full':
    minutes = int(totalTime.total_seconds() / 60)
    seconds = totalTime.total_seconds() - (minutes * 60)
    milliseconds = int(totalTime.microseconds / 1000)
    print("Total time is " + str(minutes) + ":" + str(seconds) + "." + str(milliseconds))

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
