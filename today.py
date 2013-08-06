#!/usr/bin/env python2.7
# vim: set fileencoding=utf-8> :
# See http://rhodesmill.org/pyephem/rise-set.html
import datetime
import collections

import ephem
from az2dir import az2dir
from astro_unicode import to_unicode

import config

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
    if bodies[body].alt > 0:
        print u'%s %-7s: %11s %2s in %6s phase %6.2f%%' % \
                (to_unicode(body),
                 body,
                 str(bodies[body].alt).replace(':', u'°', 1).replace(':', "'", 1).replace(':', '"', 1),
                 az2dir(bodies[body].az),
                 ephem.constellation(bodies[body])[1],
                 bodies[body].phase)
print

print "Happening Today"
events = {}
for name, body in bodies.iteritems():
    events[(name, 'rise')] = config.time_conversion(location.next_rising(body))
    events[(name, 'set')] = config.time_conversion(location.next_setting(body))
    events[(name, 'transit')] = config.time_conversion(body.transit_time)

# Twilights
location.pressure = 0
twilights = (("Astro", '-18'), ("Nautical", '-12'), ('Civil', '-6'))
for t in twilights:
    location.horizon = t[1]
    events[(t[0], 'dawn')] = config.time_conversion(location.next_rising(bodies['Sun'], use_center=True)) 
    events[(t[0], 'dusk')] = config.time_conversion(location.next_setting(bodies['Sun'], use_center=True)) 

if sleep_time:
    events[('Bedtime', '%s hr' % args.sleep)] = events[('Sun', 'rise')] - sleep_time

o_events = collections.OrderedDict(sorted(events.items(), key=lambda t: t[1]))
today = config.time_conversion(location.date).date()
for what, when in o_events.iteritems():
    if when.date()  == today:
        print '%-8s %-7s %s' % (what[0], what[1], when.strftime('%X'))
    else:
        break


