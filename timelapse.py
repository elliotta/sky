#!/usr/bin/env python

import sys

input = raw_input('Interval in minutes:seconds? ')
try:
    min, sec = [int(x) for x in input.split(':')]
except:
    sys.exit('Invalid input')
interval = sec + min*60
total_seconds = 999*interval

output_hours = total_seconds / 3600
seconds_remaining = total_seconds - 3600 * output_hours
output_minutes = seconds_remaining / 60
seconds_remaining = seconds_remaining - 60 * output_minutes
print "%ih %im %is" % (output_hours, output_minutes, seconds_remaining)
