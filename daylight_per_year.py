#!/usr/bin/env python2.7
# vim: set fileencoding=utf-8> :
# This code was written to help calculate the Return on Investment for a
#   friend considering purchasing an automated home outdoor lighting system.

import sys

import numpy
import ephem

import config 

# Configuration
parser = config.location_parser
parser.description = 'Return the sum total of the number of hours of daylight for a particular year.'
parser.add_argument('-y', '--year', default=ephem.now().datetime().year, type=int, help='Which year (default is this year)')
args = parser.parse_args()

location = config.get_location_from_namespace(args)
year = args.year
tz = -5 # Time zone offset for starting time
# Set up variables
start_date = ephem.Date('%i/1/1 %i:30:0' % (year, 0 - tz)) # initialize at midnight:30 local time

# Calculate data points
date = start_date
sun = ephem.Sun()
daylight_hours = []
while config.time_conversion(date).year == year:
    location.date = date
    sun.compute(location)
    rise = location.next_rising(sun)
    setting = location.next_setting(sun)
    daylight_hours.append((setting - rise)/ephem.hour)
    date = ephem.Date(date+1)

dh_array = numpy.array(daylight_hours)
print "Over %i days in %i in %s, there are %f hours of daylight, with an average of %f per day" % (len(daylight_hours), year, location.name, dh_array.sum(), dh_array.mean())
print "The longest day is %f hours, and the shortest is %f" % (dh_array.max(), dh_array.min())
