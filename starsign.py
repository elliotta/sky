#!/usr/bin/env python

import sys

import ephem

import az2dir

date_string = raw_input('Date (YYYY/MM/DD): ')
try:
    date = ephem.Date(date_string)
except Exception, msg:
    sys.exit('Invalid date string')

sun = ephem.Sun()
sun.compute(date)
print 'Zodic Sign', az2dir.zodiac_sign(sun), az2dir.zodiac_sign(sun, unicode_symbol=True)
print 'Constellation', ephem.constellation(sun)[1]
