#!/usr/bin/env python2.7
# See http://rhodesmill.org/pyephem/rise-set.html
import datetime
import collections

import ephem
from az2dir import az2dir

import config

parser = config.location_parser
parser.description = 'List the times for solar events today.'
parser.add_argument('-s', '--sleep', nargs='?', const=config.default_sleep_time, type=float, help='Hours of sleep desired each night (default is %.4g)' % config.default_sleep_time)
args = parser.parse_args()

location = config.get_location_from_namespace(args)
if args.sleep:
    sleep_time = datetime.timedelta(hours=args.sleep)
else:
    sleep_time = False

sun = ephem.Sun(location)
print 'It is %s in %s' % (config.time_conversion(location.date).strftime('%c'),
        location.name)
print "The sun is at alt %s az %s (%s)" % (str(sun.alt), str(sun.az), az2dir(sun.az))
print

locations = {'Sunrise': config.time_conversion(location.next_rising(sun)),
             'Sunset': config.time_conversion(location.next_setting(sun)),
             'Transit': config.time_conversion(sun.transit_time)
            }
if sleep_time:
    locations['Bedtime'] = locations['Sunrise'] - sleep_time

o_loc = collections.OrderedDict(sorted(locations.items(), key=lambda t: t[1]))
for what, when in o_loc.iteritems():
    print '%-7s %s' % (what, when.strftime('%c'))

print
print "USNO version"
location.pressure = 0
twilights = (("Astronomical", '-18', True), ("Nautical", '-12', True), ('Civil', '-6', True))
set_rise = '-0:34' # USNO's correction for the atmosphere

for t in twilights + (("Rising", set_rise, False), ):
    location.horizon = t[1]
    #print t[0].ljust(25), location.next_rising(sun, use_center=True)
    print t[0].ljust(15), config.time_conversion(location.next_rising(sun, use_center=t[2])).strftime('%c')

print 

for t in (("Setting", set_rise, False), ) + twilights[::-1]:
    location.horizon = t[1]
    #print t[0].ljust(25), location.next_setting(sun, use_center=True)
    print t[0].ljust(15), config.time_conversion(location.next_setting(sun, use_center=t[2])).strftime('%c')
