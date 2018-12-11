import cv2
import numpy as np
import math
import line_grouping
import copy


# takes in a openCV images and returns the lanes for the track as a
# list, with the first element of the list being the starting/finish line

def get_track_lanes(img):
    # The list we will be returning
    track_lines = []

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('images/gray_video.jpg', gray)

    high_thresh, thresh_im = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    lowThresh = 0.5 * high_thresh

    edges = cv2.Canny(gray, 125, 300)
    dilated = cv2.dilate(edges, np.ones((2, 2), dtype=np.uint8))
    cv2.imwrite('images/canny_video.jpg', dilated)

    # Mask
    mask = np.zeros(dilated.shape, dtype='uint8')
    # Draw white rectangle
    height, width = dilated.shape
    cv2.rectangle(mask, (0, int(height/2.42)),
                  (width-1, int(height-(height/5.5))), (255, 255, 255), -1)
    # Apply mask to the image
    dilated = cv2.bitwise_and(dilated, dilated, mask=mask)

    lines = cv2.HoughLinesP(
        dilated,
        rho=1,
        theta=np.pi / 180,
        threshold=200,
        minLineLength=275,
        maxLineGap=20)

    # If you need to view the houghlines uncomment the following lines:
    img2 = copy.deepcopy(img)
    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(img2, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.imwrite('images/hough_video.jpg', img2)

    linesFiltered = []
    for line in lines:
        for x1, y1, x2, y2 in line:
            if y1 != y2:
                if x2 > x1:
                    if y2 > height * .7 or x2 < width * .85:
                        linesFiltered.append(line)
                else:
                    if y1 > height * .7 or x1 < width * .85:
                        linesFiltered.append(line)

    img3 = copy.deepcopy(img)
    for line in linesFiltered:
        for x1, y1, x2, y2 in line:
            cv2.line(img3, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.imwrite('images/hough_video_lines_filtered.jpg', img3)

    # merge lines
    _lines = []
    for _line in line_grouping.get_lines(linesFiltered):
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
        print(line)
        if(line[1][0] < width * .8 or line[1][1] > height * .6):
            x1 = line[0][0]
            y1 = line[0][1]
            x2 = line[1][0]
            y2 = line[1][1]
            if y2 < y1:
                # The only line that moves up as it goes across the screen is the start/finish line,
                # so we have thar right here

                # We need to get the slope and y intercept, and then draw the line across the whole track
                slope = float(y2 - y1) / (x2 - x1)
                yIntercept = int(y1 - (slope * x1))

                # Find the edges of the track by getting the intersect of the starting
                # line with all the lines of the track, and then using the extreme
                # values to draw the start/finish line
                leftTrackEdge = width
                rightTrackEdge = 0
                for lineCheck in merged_lines_all:
                    if(line[1][0] < width * .8 or line[1][1] > height * .6):
                        if not lineCheck[1][1] < lineCheck[0][1]:
                            intersect = line_grouping.line_intersection(
                                line, lineCheck)
                            leftTrackEdge = min(intersect[0], leftTrackEdge)
                            rightTrackEdge = max(intersect[0], rightTrackEdge)

                # Get the y coordinates based on our intersect values and the previously
                # determined slope and yIntercept values
                yLeft = int(yIntercept + (slope * leftTrackEdge))
                yRight = int(yIntercept + (slope * rightTrackEdge))
                # cv2.line(img, (int(leftTrackEdge), yLeft),
                #         (int(rightTrackEdge), yRight), (0, 255, 255), 6)
                startLine = [(int(leftTrackEdge), yLeft),
                             (int(rightTrackEdge), yRight)]
                track_lines.insert(0, startLine)
            else:
                # cv2.line(img, (x1, y1),
                #         (x2, y2), (0, 0, 255), 6)
                track_lines.append(line)

    # cv2.imwrite('images/merged.jpg', img)
    return track_lines
