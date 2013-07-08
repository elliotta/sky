#!/usr/bin/env python2.7
import collections

import ephem
from az2dir import az2dir

import config

location = config.default_location
moon = ephem.Moon(location)
print "Current phase is %.2f%% illuminated" % (moon.phase)
print "Moon in %s is at alt %s in %s to the %s" % (location.name, moon.alt, ephem.constellation(moon)[1], az2dir(moon.az))
print


locations = {'rise': config.time_conversion(location.next_rising(moon)),
             'set': config.time_conversion(location.next_setting(moon)),
             'transit': config.time_conversion(moon.transit_time)
            }
    
if not locations['transit']:
    print 'No transit time'
    del locations['transit']

o_loc = collections.OrderedDict(sorted(locations.items(), key=lambda t: t[1]))

phases = {"Full Moon": ephem.next_full_moon(location.date),
        "New Moon": ephem.next_new_moon(location.date),
        "First Quarter": ephem.next_first_quarter_moon(location.date),
        "Last Quarter": ephem.next_last_quarter_moon(location.date)
        }

o_phases = collections.OrderedDict(sorted(phases.items(), key=lambda t: t[1]))

for what, when in o_loc.iteritems():
    location.date = when
    moon.compute(location)
    print "The moon will %7s on %s to the %s in %s" % \
            (what, when.strftime('%c'), az2dir(moon.az),
                    ephem.constellation(moon)[1])
print 

for what, when in o_phases.iteritems():
    location.date = when
    moon.compute(location)
    print what.ljust(15), config.time_conversion(when).strftime('%c'), '%11s to the %-2s in %s' % (str(moon.alt), az2dir(moon.az), ephem.constellation(moon)[1])

