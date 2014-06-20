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
parser.description = 'Plot the moon and sun\'s rising and setting, hours of daylight, and maximum elevations over a year.'
parser.add_argument('-y', '--year', default=ephem.now().datetime().year, type=int, help='Which year to plot (default is this year)')
parser.add_argument('-f', '--file', help='Output file. Will not display to screen')
parser.add_argument('-s', '--sleep', nargs='?', const=config.default_sleep_time, type=float, help='Hours of sleep desired each night (default is %.4g)' % config.default_sleep_time)
args = parser.parse_args()
location = config.get_location_from_namespace(args)
lunar_transit_location = config.get_location_from_namespace(args)
year = args.year
file = args.file
sleeptime = args.sleep

tz = -5 # Time zone offset for starting time

# Set up variables
start_date = ephem.Date('%i/1/1 %i:30:0' % (year, 0 - tz)) # initialize at midnight:30 local time

# X-axis 
days = []
# Y-axis for daily things
sun_events = [[], [], [], # astro, nautical civil
              [], [], [], # rise, transit, set
              [], [], []] # civil, nautical, astro
sun_event_labels = ('Astro Twlt', 'Naut Twlt', 'Civil Twlt',
                    'Rise', 'Transit', 'Set',
                    'Civil Twlt', 'Naut Twlt', 'Astr Twlt')
solar_azimuth_at_transit = []
hours_of_daylight = []
daily_moon_phase = []
daily_lunar_azimuth_at_transit = []
full_moon_dates = []

# Plot properties
sun_color = 'red'
moon_color = 'green'
night_color = 'blue'
daylight_color = 'yellow'
# Colors and alphas are for morning twilights, sun rise/transit/set, and evening twilights
colors = (night_color,)*3 + (sun_color,)*3 + (night_color,)*3
alphas = (.7, .8, .9,
          1, 1, 1,
          .9, .8, .7)

# pyephem variable initialization
location.pressure = 0
sun = ephem.Sun()
moon = ephem.Moon()
horizon_offsets = ('-18', '-12', '-6', '-0:34') # Astro, Nautical, Civil Twilights and set/rise

# Calculate full moons
next_full = ephem.next_full_moon(start_date)
while config.time_conversion(next_full).year == year:
    full_moon_dates.append(config.time_conversion(next_full))
    next_full = ephem.next_full_moon(next_full+1.)

# Calculate daily data points
date = start_date
while config.time_conversion(date).year == year:
    location.date = date
    days.append(config.time_conversion(date).date())
    day_solar_events = []
    day_lunar_events = []

    # Twilights and sunrise
    for offset in horizon_offsets:
        location.horizon = offset
        day_solar_events.append(config.time_conversion(location.next_rising(sun)))

    # Reset horizon for next set of points
    location.horizon = 0

    # Moon data, while location's date is still midnight
    moon.compute(location)
    daily_moon_phase.append(moon.phase)

    lunar_transit_time = location.next_transit(moon)
    lunar_transit_location.date = lunar_transit_time
    moon.compute(lunar_transit_location)
    daily_lunar_azimuth_at_transit.append(moon.alt*180/ephem.pi)

    # High Noon
    solar_transit = location.next_transit(sun)
    day_solar_events.append(config.time_conversion(solar_transit))

    location.date = solar_transit # This might be redundant
    sun.compute(location)
    solar_azimuth_at_transit.append(sun.alt*180/ephem.pi)

    # Sunset and twilights
    for offset in horizon_offsets[::-1]:
        location.horizon = offset
        day_solar_events.append(config.time_conversion(location.next_setting(sun)))

    for x in xrange(len(day_solar_events)):
        hour = day_solar_events[x].hour
        hour += day_solar_events[x].minute/60.
        hour += day_solar_events[x].second/3600.
        sun_events[x].append(hour)
        day_solar_events[x] = hour

    hours_of_daylight.append(day_solar_events[5] - day_solar_events[3]) # sunset - sunrise
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

fig = plt.figure(figsize=(10.5,8))
grid = gs.GridSpec(4, 1, height_ratios=[2, 1, .5, 1])

ax = plt.subplot(grid[0])
# Data
for event, label, color, alpha in zip(sun_events, sun_event_labels, colors, alphas):
    plt.plot(days, event, label=label, c=color, alpha=alpha)
if sleeptime:
    plt.plot(days, bedtimes, label="bed", c='black', alpha=1)
# Fill daylight hours with yellow
plt.fill_between(days, sun_events[5], sun_events[3], facecolor=daylight_color, alpha=.5) 
# Fill twilights with pale blue
plt.fill_between(days, sun_events[0], sun_events[3], facecolor=night_color, alpha=.2) 
plt.fill_between(days, sun_events[5], sun_events[8], facecolor=night_color, alpha=.2) 
# Fill nights with darker blue
plt.fill_between(days, sun_events[0], facecolor=night_color, alpha=.5) 
plt.fill_between(days, sun_events[8], [24.0 for x in xrange(len(days))], facecolor=night_color, alpha=.5) 
# X Axis
plt.xticks(sol_eq, ('Vernal Eq.', 'Summer Sol.', 'Autumn Eq.', 'Winter Sol.'))
ax.xaxis.grid(color=sun_color)
ax.xaxis.set_minor_locator(matplotlib.dates.MonthLocator())
# Y Axis
plt.ylim((24, 0))
ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(3))
ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator())
ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%i:00'))
#plt.legend(loc='upper left')
ax.yaxis.grid(color='black')
plt.ylabel('Hour of Day (EDT)')
plt.title('The Sun and Moon in %i in %s' % (year, location.name))

#ax2 = plt.subplot(grid[1], sharex=ax)
ax2 = plt.subplot(grid[1])
plt.plot(days, solar_azimuth_at_transit, color=sun_color)
plt.plot(days, daily_lunar_azimuth_at_transit, color=moon_color)
plt.ylim((0, 90))
ax2.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(30))
ax2.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter(u'%i°'))
plt.xticks(sol_eq, [se.strftime('%B %d') for se in sol_eq])
ax2.xaxis.grid(color=sun_color)
#ax2.xaxis.set_minor_locator(matplotlib.dates.MonthLocator())
ax2.xaxis.set_ticks(full_moon_dates, minor=True)
ax2.yaxis.grid(color='black')
ax2.xaxis.grid(which='minor', color=moon_color)
plt.ylabel('Elevation')
plt.title('Solar (Red) and Lunar (Blue) Elevation at Transit')

#ax3 = plt.subplot(grid[3], sharex=ax)
ax3 = plt.subplot(grid[2])
plt.plot(days, daily_moon_phase, color=moon_color)
#plt.fill_between(days, daily_moon_phase, [100. for x in xrange(len(days))], facecolor='black', alpha=.4) 
plt.ylim((0, 100))
ax3.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(50))
ax3.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(25))
ax3.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter(u'%i%%'))
ax3.yaxis.grid(color='black')
ax3.yaxis.grid(color='black', which='minor')
#plt.setp(ax3.get_xticklabels(), visible=False)
plt.xticks(sol_eq)
ax3.xaxis.grid(which='major', color=sun_color)
ax3.xaxis.set_ticks(full_moon_dates, minor=True)
ax3.xaxis.grid(which='minor', color=moon_color)
ax3.xaxis.set_ticklabels(['%s%i\n%s' % (d.strftime('%b')[:-1], d.day, d.strftime('%H:%M')) for d in full_moon_dates], minor=True)
#ax3.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%b\n%d'))
ax3.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
plt.ylabel('Fullness')
plt.title('Lunar Phase')

ax4 = plt.subplot(grid[3])
plt.plot(days, hours_of_daylight, color=sun_color)
plt.fill_between(days, hours_of_daylight, facecolor=daylight_color, alpha=.5) 
plt.fill_between(days, hours_of_daylight, [24. for x in xrange(len(days))], facecolor=night_color, alpha=.5) 
plt.ylim((0, 24))
ax4.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(6))
plt.xticks(sol_eq)
ax4.xaxis.grid(color=sun_color)
ax4.xaxis.set_minor_locator(matplotlib.dates.MonthLocator())
ax4.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%b'))
ax4.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
ax4.yaxis.grid(color='black')
plt.ylabel('N Hours')
plt.title('Hours of Daylight')


plt.tight_layout()
if file:
    pylab.savefig(file)
else:
    plt.show()
