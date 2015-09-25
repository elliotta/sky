#!/usr/bin/env python2.7
# vim: set fileencoding=utf-8> :

# Note that ephem DOES NOT DO TIMEZONES!!!
# Nor does datetime.datetime.now include a timezone
# It is much safer to use utcnow and convert later

import datetime
import sys
import errno

import ephem
import ephem.stars # auto-import by ephem.star, but not before
import matplotlib.pyplot as plt
import pylab
import matplotlib.dates
import matplotlib.ticker
import matplotlib.gridspec as gs

import config

parser = config.location_parser
parser.description = 'Plot the location of a heaveny body over a particular time period.'
parser.add_argument('-b', '--body', nargs='+', default=['Moon'], help='Heavenly body/bodies to plot (default is Moon)')
parser.add_argument('-d', '--duration', default=120, type=int, help='How many minutes to plot (default is 120)')
parser.add_argument('-f', '--file', help='Output file. Will not display to screen')
args = parser.parse_args()

bodies = []
for body in args.body:
    if body.title() in dir(ephem):
        bodies.append(getattr(ephem, body.title())())
    elif body.title() in ephem.stars.stars.keys():
        bodies.append(ephem.star(body.title()))
    else:
        print 'Body %s unknown' % body
        sys.exit(errno.EINVAL)

location = config.get_location_from_namespace(args)

n_minutes = args.duration
start_date = config.time_conversion(location.date)
end_date = start_date + datetime.timedelta(minutes=n_minutes)

utc_timestamps = []
date = start_date
while date < end_date:
    utc_timestamps.append(date)
    date = date + datetime.timedelta(minutes=1)

local_timestamps = []
body_alt = []
body_az = [] 
for i, body in enumerate(bodies):
    body_alt.append([])
    body_az.append([])
for t in utc_timestamps:
    # Set location's time, compute body's altitude, convert to degrees
    location.date = t
    for i, body in enumerate(bodies):
        body.compute(location)
        body_alt[i].append(body.alt*180/ephem.pi)
        body_az[i].append(body.az*180/ephem.pi)
    local_timestamps.append(config.time_conversion(location.date))

sun = ephem.Sun()

local_sunrises = []
next_sunrise = location.next_rising(sun, start=start_date)
ephem_end_date = ephem.Date(end_date)
while next_sunrise < ephem_end_date:
    local_sunrises.append(config.time_conversion(next_sunrise))
    next_sunrise = location.next_rising(sun, start=next_sunrise)

local_sunsets = []
next_sunset = location.next_setting(sun, start=start_date)
while next_sunset < ephem_end_date:
    local_sunsets.append(config.time_conversion(next_sunset))
    next_sunset = location.next_setting(sun, start=next_sunset)

fig = plt.figure()

alt_colors = []
phase_colors = []
if len(bodies) == 1:
    alt_colors.append('green')
    phase_colors.append('blue')
    alt_axis_color = 'green'
    phase_axis_color = 'blue'
else:
    colors = ('blue', 'red', 'green', 'orange', 'purple', 'yellow')
    alt_axis_color = 'black'
    phase_axis_color = 'black'
    for i, body in enumerate(bodies):
        alt_colors.append(colors[i])
        phase_colors.append(colors[i])

compass16 = ('N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW')
compass16_dict = dict([(-i*22.5, value) for i, value in enumerate(compass16)])
def deg2compass16(deg, pos):
    if deg in compass16_dict:
        return compass16_dict[deg]
    else:
        return u'%.1f°' % deg

ax1 = fig.add_subplot(111) # rows, columns, n-plot
for i, (az, alt) in enumerate(zip(body_az, body_alt)):
    ax1.plot(az, alt, c=alt_colors[i], label=bodies[i].name)
ax1.set_title('%s Locations Over %i Minutes in %s Starting On %s' % (', '.join([body.name for body in bodies]), n_minutes, location.name, config.time_conversion(location.date).strftime('%b %d, %Y')))
ax1.set_ylabel('Altitude (Degrees Above Horizon)', color=alt_axis_color)
ax1.set_xlabel('Azimuth (East of North)')
ax1.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(deg2compass16))
ax1.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter(u'%d°'))
for tl in ax1.get_yticklabels():
    tl.set_color(alt_axis_color)
if len(bodies) > 1:
    ax1.legend()

plt.tight_layout()

if args.file:
    pylab.savefig(args.file)
else:
    plt.show()
