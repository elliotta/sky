#!/usr/bin/env python2.7
import collections
import operator
import argparse

import ephem

import config

parser = argparse.ArgumentParser(description='Displays seasons and apsis for one year')
parser.add_argument('-y', '--year', type=int, help='Seasons for a particular year. Default is today.')
parser.add_argument('-v', '--verbose', action='store_true', help='Print extra information about apsis precision')

args = parser.parse_args()

if args.year:
    now = ephem.date('%i-01-01' % args.year)
else:
    now = ephem.now()
sun = ephem.Sun()


def au(date):
    sun.compute(date)
    return sun.earth_distance


def apsis(starting_date, op):
    interval = 30. # About one month
    precision = ephem.minute
    d = starting_date
    while interval >= precision:
        if op(au(d+interval), au(d)):
            d = ephem.date(d + interval)
        elif op(au(d-interval), au(d)):
            d = ephem.date(d - interval)
        else:
            if au(d) == au(d+interval) == au(d-interval):
                if interval > precision:
                    if args.verbose:
                        print 'Hit limit of precision between %s and %s' % (ephem.date(d-interval), ephem.date(d+interval))
                    current_au = au(d)
                    min_d = ephem.date(d - interval)
                    max_d = ephem.date(d + interval)
                    while au(min_d) == current_au:
                        min_d = ephem.date(min_d - precision)
                    while au(max_d) == current_au:
                        max_d = ephem.date(max_d + precision)
                    d = ephem.date((min_d + max_d) / 2.)
                    if args.verbose:
                        print 'Same distance from %s to %s, averaged to %s' % (ephem.date(min_d), ephem.date(max_d), d)
                break
            interval = interval/2.
    return d


def aphelion(starting_date):
    '''Furthest from sun'''
    return apsis(starting_date, operator.gt)


def perihelion(starting_date):
    '''Closest to sun'''
    return apsis(starting_date, operator.lt)


sol_equ = []

for evt, date in (('Vernal (Spring) Equinox', ephem.next_vernal_equinox(now)),
                  ('Autumn Equinox', ephem.next_autumn_equinox(now)),
                  ('Summer Solstice', ephem.next_summer_solstice(now)),
                  ('Aphelion', aphelion(ephem.next_summer_solstice(now))),
                  ('Winter Solstice', ephem.next_winter_solstice(now)),
                  ('Perihelion', perihelion(ephem.next_winter_solstice(now)))
                  ):
    sol_equ.append((evt, (config.time_conversion(date), au(date))))


o_sol_equ = collections.OrderedDict(sorted(sol_equ, key=lambda t: t[1]))

for what, details in o_sol_equ.iteritems():
    print what.ljust(27), details[0].strftime('%c'), '  %.4f AU' % details[1]

