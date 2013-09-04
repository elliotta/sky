#!/usr/bin/env python2.7
# vim: set fileencoding=utf-8> :
# See http://rhodesmill.org/pyephem/rise-set.html
import datetime
import collections

import ephem
from az2dir import az2compass16
from astro_unicode import to_unicode

import config
import poi

parser = config.location_parser
parser.description = 'List the times for solar, lunar, and planetary events today.'
parser.add_argument('-s', '--sleep', nargs='?', const=config.default_sleep_time, type=float, help='Hours of sleep desired each night (default is %.4g)' % config.default_sleep_time)
args = parser.parse_args()

location = config.get_location_from_namespace(args)
if args.sleep:
    sleep_time = datetime.timedelta(hours=args.sleep)
else:
    sleep_time = False

print 'It is %s in %s' % (config.time_conversion(location.date).strftime('%c'),
        location.name)
print

print "Up right now"
bodies = collections.OrderedDict() # want to be able to reference them by name
for body in  ('Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune'):
    bodies[body] = getattr(ephem, body)(location)
bodies['Galaxy'] = poi.galactic_center
bodies['Galaxy'].compute(location)
bodies['LMC'] = poi.large_magellanic_cloud
bodies['LMC'].compute(location)
bodies['SMC'] = poi.small_magellanic_cloud
bodies['SMC'].compute(location)
bodies['Crux'] = poi.crux
bodies['Crux'].compute(location)

for name, body in bodies.iteritems():
    if body.alt > 0:
        if hasattr(body, 'phase'):
            print u'%s %-7s: %11s, %3s in %6s phase %6.2f%%' % \
                    (to_unicode(name) or ' ',
                     name,
                     str(body.alt).replace(':', u'°', 1).replace(':', "'", 1).replace(':', '"', 1),
                     az2compass16(body.az),
                     ephem.constellation(body)[1],
                     body.phase)
        else:
            print u'%s %-7s: %11s, %3s in %6s' % \
                    (to_unicode(name) or ' ',
                     name,
                     str(body.alt).replace(':', u'°', 1).replace(':', "'", 1).replace(':', '"', 1),
                     az2compass16(body.az),
                     ephem.constellation(body)[1])

print

print "Happening Today"
start  = config.time_conversion(location.date)
events = {}
for name, body in bodies.iteritems():
    try:
        events[(name, 'rise')] = config.time_conversion(location.next_rising(body))
    except ephem.AlwaysUpError:
        pass
    try:
        events[(name, 'set')] = config.time_conversion(location.next_setting(body))
    except ephem.AlwaysUpError:
        pass
    try:
        events[(name, 'transit')] = config.time_conversion(body.transit_time)
    except ephem.AlwaysUpError:
        pass

# Twilights
location.pressure = 0
twilights = (("Astro", '-18'), ("Nautical", '-12'), ('Civil', '-6'))
for t in twilights:
    location.horizon = t[1]
    events[(t[0], 'dawn')] = config.time_conversion(location.next_rising(bodies['Sun'], use_center=True)) 
    events[(t[0], 'dusk')] = config.time_conversion(location.next_setting(bodies['Sun'], use_center=True)) 

if sleep_time:
    events[('Bedtime', '%s hr' % args.sleep)] = events[('Sun', 'rise')] - sleep_time

tomorrow = start + datetime.timedelta(days=1)
events[(start.strftime('%b %d'), '')] = datetime.datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day)

o_events = collections.OrderedDict(sorted(events.items(), key=lambda t: t[1]))
for what, when in o_events.iteritems():
    if when - start > datetime.timedelta(hours=24):
        break
    print '%-8s %-7s %s' % (what[0], what[1], when.strftime('%X'))


