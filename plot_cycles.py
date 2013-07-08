#!/usr/bin/env python2.7
# vim: set fileencoding=utf-8> :

# Note that ephem DOES NOT DO TIMEZONES!!!
# Nor does datetime.datetime.now include a timezone
# It is much safer to use utcnow and convert later

import datetime
import sys

import ephem
import matplotlib.pyplot as plt
import pylab
import matplotlib.dates
import matplotlib.ticker
import matplotlib.gridspec as gs

import config

parser = config.location_parser
parser.description = 'Plot the location of a heaveny body over several days.'
parser.add_argument('-b', '--body', nargs='+', default=['Moon'], help='Heavenly body/bodies to plot (default is Moon)')
parser.add_argument('-d', '--days', default=10, type=int, help='How many days to plot (default is 10)')
parser.add_argument('-f', '--file', help='Output file. Will not display to screen')
args = parser.parse_args()

bodies = []
for body in args.body:
    if body.title() in dir(ephem):
        bodies.append(getattr(ephem, body.title())())

location = config.get_location_from_namespace(args)

n_days = args.days
start_date = datetime.datetime.utcnow()
end_date = start_date + datetime.timedelta(days=n_days)

utc_timestamps = []
date = start_date
while date < end_date:
    utc_timestamps.append(date)
    date = date + datetime.timedelta(minutes = 15)

local_timestamps = []
body_alt = []
body_phase = []
for body in bodies:
    body_alt.append([])
    body_phase.append([])
for t in utc_timestamps:
    # Set location's time, compute body's altitude, convert to degrees
    location.date = t
    for i, body in enumerate(bodies):
        body.compute(location)
        body_alt[i].append(body.alt*180/ephem.pi)
        body_phase[i].append(body.phase)
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

fig = plt.figure(figsize=(12,3))

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

ax1 = fig.add_subplot(111) # rows, columns, n-plot
for i, alt in enumerate(body_alt):
    ax1.plot(local_timestamps, alt, c=alt_colors[i], label=bodies[i].name)
plt.ylim(0, 90)
ax1.set_title('%s Locations Over Next %i Days in %s' % (', '.join([body.name for body in bodies]), n_days, location.name))
ax1.set_ylabel('Altitude (Degrees Above Horizon)', color=alt_axis_color)
ax1.set_xlabel('Time (EDT)')
for tl in ax1.get_yticklabels():
    tl.set_color(alt_axis_color)
if len(bodies) > 1:
    ax1.legend()

ax2 = ax1.twinx()
for i, phase in enumerate(body_phase):
    ax2.plot(local_timestamps, phase, c=phase_colors[i])
plt.ylim(0, 100)
ax2.set_ylabel('Phase (% illuminated)', color=phase_axis_color)
for tl in ax2.get_yticklabels():
    tl.set_color(phase_axis_color)

if n_days < 20:
    ax1.set_xticks(local_sunrises)
    ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M\n%m/%d'))
if n_days <= 10:
    ax1.set_xticks(local_sunsets, minor=True)
    ax1.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%H:%M'))
#for label in ax1.xaxis.get_ticklabels():
#    label.set_rotation(30)

if local_sunsets[0] < local_sunrises[0]:
    # Starts with a sunset, so a partial day
    print "Adding initial sunrise"
    local_sunrises.insert(0, local_timestamps[0])
if local_sunrises[-1] > local_sunsets[-1]:
    # Ends with a sunrise, so a partial day
    print "Adding final sunset"
    local_sunsets.append(local_timestamps[-1])

for rise, set in zip(local_sunrises, local_sunsets):
    plt.axvspan(rise, set, facecolor='yellow', alpha=.2)

fig.subplots_adjust(left=.05, right=.95, bottom=.2)

#plt.tight_layout()

if args.file:
    pylab.savefig(args.file)
else:
    plt.show()
