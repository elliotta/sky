#!/usr/bin/env python2.7
# vim: set fileencoding=utf-8> :

import sys

import ephem
import matplotlib.pyplot as plt
import pylab
import matplotlib.dates
import matplotlib.ticker
import matplotlib.gridspec as gs

import config 

# Configuration
parser = config.location_parser
parser.description = 'Plot the sun\'s rising and setting, hours of daylight, and maximum elevation over a year.'
parser.add_argument('-y', '--year', default=ephem.now().datetime().year, type=int, help='Which year to plot (default is this year)')
parser.add_argument('-f', '--file', help='Output file. Will not display to screen')
parser.add_argument('-s', '--sleep', nargs='?', const=config.default_sleep_time, type=float, help='Hours of sleep desired each night (default is %.4g)' % config.default_sleep_time)
args = parser.parse_args()
location = config.get_location_from_namespace(args)
year = args.year
file = args.file
sleeptime = args.sleep

tz = -5 # Time zone offset for starting time

# Set up variables
start_date = ephem.Date('%i/1/1 %i:30:0' % (year, 0 - tz)) # initialize at midnight:30 local time

# X-axis
days = []
# Y-axis
sun_events = [[], [], [], # astro, nautical civil
              [], [], [], # rise, transit, set
              [], [], []] # civil, nautical, astro
sun_event_labels = ('Astro Twlt', 'Naut Twlt', 'Civil Twlt',
                    'Rise', 'Transit', 'Set',
                    'Civil Twlt', 'Naut Twlt', 'Astr Twlt')
azimuth_at_transit = []
hours_of_daylight = []

# Plot properties
colors = ('blue', 'blue', 'blue',
          'red', 'red', 'red',
          'blue', 'blue', 'blue')
alphas = (.7, .8, .9,
          1, 1, 1,
          .9, .8, .7)

# pyephem variable initialization
location.pressure = 0
sun = ephem.Sun()
horizon_offsets = ('-18', '-12', '-6', '-0:34') # Astro, Nautical, Civil Twilights and set/rise

# Calculate data points
date = start_date
while config.time_conversion(date).year == year:
    location.date = date
    days.append(config.time_conversion(date).date())
    events = []

    # Twilights and sunrise
    for offset in horizon_offsets:
        location.horizon = offset
        events.append(config.time_conversion(location.next_rising(sun)))

    # High Noon
    location.horizon = 0
    transit = location.next_transit(sun)
    events.append(config.time_conversion(transit))

    location.date = transit # This might be redundant
    sun.compute(location)
    azimuth_at_transit.append(sun.alt*180/ephem.pi)

    # Sunset and twilights
    for offset in horizon_offsets[::-1]:
        location.horizon = offset
        events.append(config.time_conversion(location.next_setting(sun)))

    for x in xrange(len(events)):
        hour = events[x].hour
        hour += events[x].minute/60.
        hour += events[x].second/3600.
        sun_events[x].append(hour)
        events[x] = hour

    hours_of_daylight.append(events[5] - events[3]) # sunset - sunrise
    date = ephem.Date(date+1)

if sleeptime:
    # Calculate bedtimes based on next day's sunrise
    bedtimes = []
    for sunrise in sun_events[3][1:]:
        bedtimes.append(24. + sunrise - sleeptime)
    bedtimes.append(None)

sol_eq = (config.time_conversion(ephem.next_vernal_equinox(start_date)),
          config.time_conversion(ephem.next_summer_solstice(start_date)),
          config.time_conversion(ephem.next_autumn_equinox(start_date)),
          config.time_conversion(ephem.next_winter_solstice(start_date))
         )

grid = gs.GridSpec(3, 1, height_ratios=[3, 1, 1])

ax = plt.subplot(grid[0])
# Data
for event, label, color, alpha in zip(sun_events, sun_event_labels, colors, alphas):
    plt.plot(days, event, label=label, c=color, alpha=alpha)
if sleeptime:
    plt.plot(days, bedtimes, label="bed", c='black', alpha=1)
# Fill daylight hours with yellow
plt.fill_between(days, sun_events[5], sun_events[3], facecolor='yellow', alpha=.5) 
# Fill twilights with pale blue
plt.fill_between(days, sun_events[0], sun_events[3], facecolor='blue', alpha=.2) 
plt.fill_between(days, sun_events[5], sun_events[8], facecolor='blue', alpha=.2) 
# Fill nights with darker blue
plt.fill_between(days, sun_events[0], facecolor='blue', alpha=.5) 
plt.fill_between(days, sun_events[8], [24.0 for x in xrange(len(days))], facecolor='blue', alpha=.5) 
# X Axis
plt.xticks(sol_eq, ('Vernal Eq.', 'Summer Sol.', 'Autumn Eq.', 'Winter Sol.'))
ax.xaxis.set_minor_locator(matplotlib.dates.MonthLocator())
# Y Axis
plt.ylim((24, 0))
ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(3))
ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator())
ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%i:00'))
#plt.legend(loc='upper left')
plt.grid(True)
plt.ylabel('Hour of Day (EDT)')
plt.title('The Sun in %i in %s' % (year, location.name))

#ax2 = plt.subplot(grid[1], sharex=ax)
ax2 = plt.subplot(grid[1])
plt.plot(days, azimuth_at_transit)
plt.ylim((0, 90))
ax2.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(30))
ax2.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter(u'%i°'))
plt.xticks(sol_eq, [se.strftime('%B %d') for se in sol_eq])
ax2.xaxis.set_minor_locator(matplotlib.dates.MonthLocator())
plt.grid(True)
plt.ylabel('Elevation')
plt.title('Solar Elevation at Transit (Highest of the Day)')

#ax3 = plt.subplot(grid[2], sharex=ax)
ax3 = plt.subplot(grid[2])
plt.plot(days, hours_of_daylight)
plt.fill_between(days, hours_of_daylight, facecolor='yellow', alpha=.5) 
plt.fill_between(days, hours_of_daylight, [24. for x in xrange(len(days))], facecolor='blue', alpha=.5) 
plt.ylim((0, 24))
ax3.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(6))
#plt.setp(ax3.get_xticklabels(), visible=False)
plt.xticks(sol_eq)
ax3.xaxis.set_minor_locator(matplotlib.dates.MonthLocator())
ax3.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%b'))
ax3.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
plt.grid(True)
plt.ylabel('N Hours')
plt.title('Hours of Daylight')


plt.tight_layout()
if file:
    pylab.savefig(file)
else:
    plt.show()
