import track_lanes
import get_intersect
import numpy as np
import cv2
from yolo_cv import YoloCV
import argparse
import time

parser = argparse.ArgumentParser(description='Track timer')
parser.add_argument('--mode', default='full', help='start, finish, or full')
parser.add_argument('--runners', default=1, type=int, help='number of runners')
args = parser.parse_args()

# cap = cv2.VideoCapture('images/test-start.mp4')
# cap = cv2.VideoCapture('images/finish-lane1and2.mp4')
cap = cv2.VideoCapture('images/full-lap-1.mp4')
# cap = cv2.VideoCapture('images/test-finish-same-time.mp4')
#cap = cv2.VideoCapture('images/test-finish-single-runner.mp4')


# The following code is for saving a video of the current setup
rate = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print('Frame Rate')
print(rate)

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'MPEG')
out = cv2.VideoWriter('images/output_full_lap.avi',
                      fourcc, rate, (width, height))

trackLanes = []
startLine = []
startLine_intersectionPoints = []
intersectPointsSorted = []

count = 0
yoloCVObj = YoloCV()

started = False
finished = False
startFrame = 0
waitFrames = 20 * cv2.CAP_PROP_FPS  # 20 seconds
totalFrames = 0

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
        trackLanesResult = track_lanes.get_track_lanes(frame)
        trackLanes = trackLanesResult['track_lines']
        startLine_intersectionPoints = trackLanesResult['intersection_points']
        print(startLine_intersectionPoints)
        temp = []
        for sl in startLine_intersectionPoints:
            intersect_x = int(sl[0])
            temp.append(intersect_x)
        intersectPointsSorted = sorted(temp)
        print(intersectPointsSorted)
        # get the startLine from the list and then remove
        startLine = trackLanes[0]
        del trackLanes[0]

    # write the final image
    # cv2.imwrite('images/merged_video.jpg', frame)
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
        if (y1 > 0.45 * height):
            # If we didn't get the full line, extend it out
            slope = (y1 - y2) / (x1 - x2)
            y1 = int(0.45 * height)
            x1 = int(((y1 - y2) / slope) + x2)
        cv2.line(frame, (x1, y1),
                 (x2, y2), (0, 0, 255), 6)

    # Draw the startLine
    cv2.line(frame, (startLine[0][0], startLine[0][1]),
             (startLine[1][0], startLine[1][1]), (0, 255, 255), 6)

    # Detect bounding box intersection with startLine
    for box in currentPredictedBoxes:
        if get_intersect.box_line(box, startLine) != False:
            p, side = get_intersect.box_line(box, startLine)
            cv2.circle(frame, (int(p[0]), int(p[1])), 5,
                       (0, 255, 0), thickness=5, lineType=8, shift=0)
            # Start is the last intersection on the bottom of the box at the beginning
            # if not started or count - startFrame < 300:
            if not started and side == 'right':
                started = True
                startFrame = count
                cv2.putText(frame, 'Start', (200, 800),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4, cv2.LINE_AA)
            elif started and not finished and count - startFrame > waitFrames:
                finishFrame = count
                totalFrames = finishFrame - startFrame
                timeStr = ""
                if args.mode == 'full':
                    time = totalFrames / cap.get(cv2.CAP_PROP_FPS)
                    print(time)
                    minutes = int(time / 60)
                    seconds = time - (minutes * 60)
                    #milliseconds = (time - (minutes * 60))
                    timeStr = str(minutes) + ":" + str(round(seconds, 2))
                    print("Total time is " + str(minutes) +
                          ":" + str(round(seconds, 2)))
                finished = True
                cv2.putText(frame, 'Finish: ' + timeStr, (200, 800),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4, cv2.LINE_AA)

    if started and count - startFrame < 90:
        cv2.putText(frame, 'Start', (200, 800),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4, cv2.LINE_AA)

    if finished and count - finishFrame < 90:
        cv2.putText(frame, 'Finish: ' + timeStr, (200, 800),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4, cv2.LINE_AA)

    # Find the intersection points
    for intersection_point in startLine_intersectionPoints:
        cv2.circle(frame, (int(intersection_point[0]), int(intersection_point[1])), 5,
                   (255, 255, 0), thickness=10, lineType=8, shift=0)

    # Display the resulting frame
    try:
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        count += 1
    except:
        break

    # if (count > 3):
    #    break

    # Write out the video frame here
    out.write(frame)

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
