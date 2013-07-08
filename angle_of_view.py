#!/usr/bin/env python
# vim: set fileencoding=utf-8> :

import math
import argparse


def aov(image_length, focal_length):
    return math.degrees(2.*math.atan(image_length/(2.*focal_length)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate angle of view based on image size and focal length')
    parser.add_argument('image_length', type=float, help='Length of image in mm (DX is 24x16)')
    parser.add_argument('focal_length', type=float, help='Focal length of lens in mm')
    args = parser.parse_args()
    angle = aov(args.image_length, args.focal_length)
    print '%.2f° (%.1f\')' % (angle, angle*60.)

