#!/usr/bin/env python2.7
import collections

import ephem

import config

now = ephem.now()

sol_equ = {"Vernal (Spring) Equinox": config.time_conversion(ephem.next_vernal_equinox(now)),
        "Autumn Equinox": config.time_conversion(ephem.next_autumn_equinox(now)),
        "Summer Solstice": config.time_conversion(ephem.next_summer_solstice(now)),
        "Winter Solstice": config.time_conversion(ephem.next_winter_solstice(now))
        }

o_sol_equ = collections.OrderedDict(sorted(sol_equ.items(), key=lambda t: t[1]))

for what, when in o_sol_equ.iteritems():
    print what.ljust(27), when.strftime('%c')

