#!/usr/bin/env python2.7
# vim: set fileencoding=utf-8> :

import ephem
from az2dir import az2dir

import config
import astro_unicode

parser = config.location_parser
parser.description = 'List the current position of all the planets'
args = parser.parse_args()

location = config.get_location_from_namespace(args)

planets = (ephem.Mercury(location), ephem.Venus(location), ephem.Mars(location), ephem.Jupiter(location), ephem.Saturn(location), ephem.Uranus(location), ephem.Neptune(location))

print 'Planets from %s at %s' % (location.name, config.time_conversion(ephem.now()).strftime('%c'))
longest = len(ephem.constellation(planets[0])[1])
for planet in planets[1:]:
    n_char = len(ephem.constellation(planet)[1])
    if n_char > longest:
        longest = n_char
for planet in planets:
    symbol = astro_unicode.to_unicode(planet.name)
    print u'%s %-7s: %11s %2s in %s; phase %6.2f%% and %5.2f AU from Earth' % (symbol, planet.name, str(planet.alt).replace(':', u'°', 1).replace(':', "'", 1).replace(':', '"', 1), az2dir(planet.az), ephem.constellation(planet)[1].rjust(longest), planet.phase, planet.earth_distance)

