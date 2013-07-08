#!/usr/bin/env python

import ephem
import matplotlib.pyplot as plt

import config

parser = config.location_parser
parser.add_argument('body1')
parser.add_argument('body2')
args = parser.parse_args()

location = config.get_location_from_namespace(args)

def get_body(name):
    if name.title() in dir(ephem):
        return getattr(ephem, name)()
    else:
        return ephem.star(name)


body1 = get_body(args.body1)
body2 = get_body(args.body2)
moon_radius = ephem.Moon(location).size/60/60/2

hours = 6
interval = 5 # minutes

time_list = []
separation = []
sep_in_moon_r = []
b1_alt = []

for x in xrange(hours*60/interval):
    time_list.append(ephem.localtime(location.date))
    body1.compute(location)
    body2.compute(location)
    b1_alt.append(body1.alt*180/ephem.pi)
    sep = ephem.separation(body1, body2)
    separation.append(sep)
    sep_in_moon_r.append(sep/moon_radius)
    location.date = location.date + ephem.minute*interval

for date, sep, rad, alt in zip(time_list, separation, sep_in_moon_r, b1_alt):
    print date, sep, rad, alt

sep_color = 'red'
alt_color = 'blue'

fig = plt.figure(figsize=(12,3))
ax1 = fig.add_subplot(111) # rows, columns, n-plot
ax1.plot(time_list, sep_in_moon_r, c=sep_color)
ax1.set_title('Positions of %s and %s for the next %i hours' % (body1.name, body2.name, hours))
ax1.set_ylabel('Separation in Moon Radius', color=sep_color)
ax2 = ax1.twinx()
ax2.plot(time_list, b1_alt, c=alt_color, label='%s Altitude' % body1.name)
plt.ylim(0,90)
ax2.set_ylabel('Altitude of %s' % body1.name, color=alt_color)
plt.show()
