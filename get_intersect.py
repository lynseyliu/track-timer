import numpy as np
import cv2
from line_grouping import line_intersection
import math

def p_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def point_line(p, line):
    a = line[0]
    b = line[1]
    return p_distance(a, p) + p_distance(p, b) == p_distance(a, b)

def line_line(line1, line2):
    try:
        x, y = line_intersection(line1, line2)
        if point_line((x, y), line1):
            return x, y
        else:
            return False
    except:
        return False

def box_line(box, line):
    top = [ (box['x'], box['y']), (box['x'] + box['w'], box['y']) ]
    left = [ (box['x'], box['y']), (box['x'], box['y'] + box['h']) ]
    right = [ (box['x'] + box['w'], box['y'] + box['h']), (box['x'] + box['w'], box['y']) ]
    bottom = [ ( int(box['x'] + box['w']), int(box['y'] + box['h']) ), ( int(box['x']), int(box['y'] + box['h']) ) ]
    return line_line(bottom, line)
