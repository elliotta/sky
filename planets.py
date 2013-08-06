#!/usr/bin/env python2.7
# vim: set fileencoding=utf-8> :

import ephem
from az2dir import az2compass16

import config
import astro_unicode

parser = config.location_parser
parser.description = 'List the current position of all the planets'
args = parser.parse_args()

location = config.get_location_from_namespace(args)

planets = (ephem.Mercury(location), ephem.Venus(location), ephem.Mars(location), ephem.Jupiter(location), ephem.Saturn(location), ephem.Uranus(location), ephem.Neptune(location))

print 'Planets from %s at %s' % (location.name, config.time_conversion(ephem.now()).strftime('%c'))

for planet in planets:
    symbol = astro_unicode.to_unicode(planet.name)
    print u'%s %-7s: %11s, %3s in %s; phase %6.2f%%, %5.2f ㍳ earth, %5.2f ㍳ sun' % \
            (symbol,
             planet.name,
             str(planet.alt).replace(':', u'°', 1).replace(':', "'", 1).replace(':', '"', 1),
             az2compass16(planet.az),
             ephem.constellation(planet)[0],
             planet.phase,
             planet.earth_distance,
             planet.sun_distance)

