#!/usr/bin/env python
# vim: set fileencoding=utf-8> :

import sys
from datetime import datetime
from collections import OrderedDict

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

# Set up variables
start_date = config.localtime_to_ephem(datetime(year=year, month=1, day=1, hour=0, minute=30)) # initialize at midnight:30 local time

# X-axis
days = []
# Y-axis
sun_events = OrderedDict()
sun_events['Morn Astr Twlt'] = {'data': [], 'color': 'blue', 'alpha': .7, 'horizon': '-18'   }
sun_events['Morn Naut Twlt'] = {'data': [], 'color': 'blue', 'alpha': .8, 'horizon': '-12'   }
sun_events['Morn Civl Twlt'] = {'data': [], 'color': 'blue', 'alpha': .9, 'horizon':  '-6'   }
sun_events['Rise'          ] = {'data': [], 'color': 'red' , 'alpha':1  , 'horizon':  '-0:34'}
sun_events['Morn Vit D'    ] = {'data': [], 'color': 'red' , 'alpha': .5, 'horizon': '50'    }
sun_events['Transit'       ] = {'data': [], 'color': 'red' , 'alpha':1  , 'horizon':  None   }
sun_events['Eve Vit D'     ] = {'data': [], 'color': 'red' , 'alpha': .5, 'horizon': '50'    }
sun_events['Set'           ] = {'data': [], 'color': 'red' , 'alpha':1  , 'horizon':  '-0:34'}
sun_events['Eve Civl Twlt' ] = {'data': [], 'color': 'blue', 'alpha': .9, 'horizon':  '-6'   }
sun_events['Eve Naut Twlt' ] = {'data': [], 'color': 'blue', 'alpha': .8, 'horizon': '-12'   }
sun_events['Eve Astr Twlt' ] = {'data': [], 'color': 'blue', 'alpha': .7, 'horizon': '-18'   }

altitude_at_transit = []
hours_of_daylight = []
negative_azimuth_at_sunrise = []

# pyephem variable initialization
starting_pressure = location.pressure
location.pressure = 0
sun = ephem.Sun()
horizon_offsets = ('-18', '-12', '-6', '-0:34', 50) # Astro, Nautical, Civil Twilights, set/rise, vitamin D

# Calculate data points
date = start_date
while config.time_conversion(date).year == year:
    location.date = date
    days.append(config.time_conversion(date).date())
    events = []

    # Twilights and sunrise
    for offset in horizon_offsets:
        location.horizon = offset
        try:
            sunrise = config.time_conversion(location.next_rising(sun))
            day_type = "normal"
        except ephem.AlwaysUpError:
            sunrise = None
            day_type = "sun"
        except ephem.NeverUpError:
            sunrise = None
            day_type = "dark"
        events.append(sunrise)

    # Reset
    location.horizon = 0
    location.pressure = starting_pressure

    # Azimuth at Sunrize
    try:
        sunrise = location.next_rising(sun)
        location.date = sunrise
        sun.compute(location)
        negative_azimuth_at_sunrise.append(-(sun.az*180./ephem.pi))
    except (ephem.AlwaysUpError, ephem.NeverUpError):
        negative_azimuth_at_sunrise.append(None)
    
    # High Noon
    transit = location.next_transit(sun)
    events.append(config.time_conversion(transit))

    location.date = transit # This might be redundant
    sun.compute(location)
    altitude_at_transit.append(sun.alt*180/ephem.pi)

    # Sunset and twilights
    location.pressure = 0
    for offset in horizon_offsets[::-1]:
        location.horizon = offset
        try:
            sunset = config.time_conversion(location.next_setting(sun))
        except (ephem.AlwaysUpError, ephem.NeverUpError):
            sunset = None
        events.append(sunset)

    for x in xrange(len(events)):
        if events[x]:
            hour = events[x].hour
            hour += events[x].minute/60.
            hour += events[x].second/3600.
        else:
            hour = None
        sun_events.items()[x][1]['data'].append(hour)
        events[x] = hour

    # 3 is sunrise, 5 is sunset
    sunrise, sunset = events[3], events[7]
    if sunset and sunrise:
        if sunrise < sunset:
            hours_of_daylight.append(sunset - sunrise) # sunset - sunrise
        else:
            hours_of_daylight.append(24 - (sunrise - sunset))
    elif sunset:
        hours_of_daylight.append(sunset)
    elif sunrise:
        hours_of_daylight.append(24 - sunrise)
    elif day_type == 'sun':
        hours_of_daylight.append(24)
    else:
        hours_of_daylight.append(0)
    date = ephem.Date(date+1)

if sleeptime:
    # Calculate bedtimes based on next day's sunrise
    bedtimes = []
    for sunrise in sun_events['Rise']['data'][1:]:
        bedtimes.append(24. + sunrise - sleeptime)
    bedtimes.append(None)

sol_eq = (config.time_conversion(ephem.next_vernal_equinox(start_date)),
          config.time_conversion(ephem.next_summer_solstice(start_date)),
          config.time_conversion(ephem.next_autumn_equinox(start_date)),
          config.time_conversion(ephem.next_winter_solstice(start_date))
         )

grid = gs.GridSpec(4, 1, height_ratios=[3, 1, 1, 1])

ax = plt.subplot(grid[0])
# Data
print 'Days: %i' % len(days)
for name, details in sun_events.iteritems():
    print name, len(details['data'])
for name, details in sun_events.iteritems():
    plt.plot(days, details['data'], label=name, c=details['color'], alpha=details['alpha'])
if sleeptime:
    plt.plot(days, bedtimes, label="bed", c='black', alpha=1)
try:
# Fill daylight hours with yellow
    plt.fill_between(days, sun_events['Rise']['data'], sun_events['Set']['data'], facecolor='yellow', alpha=.5) 
# Fill twilights with pale blue
    plt.fill_between(days, sun_events['Morn Astr Twlt']['data'], sun_events['Rise']['data'], facecolor='blue', alpha=.2) 
    plt.fill_between(days, sun_events['Set']['data'], sun_events['Eve Astr Twlt']['data'], facecolor='blue', alpha=.2) 
# Fill nights with darker blue
    plt.fill_between(days, sun_events['Morn Astr Twlt']['data'], facecolor='blue', alpha=.5) 
    plt.fill_between(days, sun_events['Eve Astr Twlt']['data'], [24.0 for x in xrange(len(days))], facecolor='blue', alpha=.5) 
except Exception as e:
    print "Oops, not doing fills: %s" % e
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
plt.ylabel('Hour of Day (%s)' % config.timezone.tzname(date.datetime()))
plt.title('The Sun in %i in %s' % (year, location.name))

#ax2 = plt.subplot(grid[1], sharex=ax)
ax2 = plt.subplot(grid[1])
plt.plot(days, altitude_at_transit)
plt.ylim((0, 90))
ax2.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(30))
ax2.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter(u'%i°'))
plt.xticks(sol_eq, [se.strftime('%B %d') for se in sol_eq])
ax2.xaxis.set_minor_locator(matplotlib.dates.MonthLocator())
plt.grid(True)
plt.ylabel('Elevation')
plt.title('Solar Elevation at Transit (Highest of the Day)')

#ax3 = plt.subplot(grid[2], sharex=ax)
print "%f hours of daylight in a year, avg of %f/day, min %s, max %s" %  (sum(hours_of_daylight), sum(hours_of_daylight)/float(len(hours_of_daylight)), min(hours_of_daylight), max(hours_of_daylight))
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

compass16 = ('N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW')
compass16_dict = dict([(-i*22.5, value) for i, value in enumerate(compass16)])
def deg2compass16(deg, pos):
    if deg in compass16_dict:
        return compass16_dict[deg]
    else:
        return u'%.1f°' % deg

ax4 = plt.subplot(grid[3])
plt.plot(days, negative_azimuth_at_sunrise)
ax4.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(22.5))
ax4.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(deg2compass16))
plt.xticks(sol_eq)
ax4.xaxis.set_minor_locator(matplotlib.dates.MonthLocator())
ax4.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%b'))
ax4.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
plt.grid(True)
plt.ylabel('Azimuth')
plt.title('Azimuth at Sunrise')

plt.tight_layout()
if file:
    pylab.savefig(file)
else:
    plt.show()
