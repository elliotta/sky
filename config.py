# vim: set fileencoding=utf-8> :
# This is a set of configuration option used by the
#  other files in this directory.

import argparse
import os
import csv

import ephem
import ephem.cities
import pytz

my_locations = {}
timezone = pytz.timezone('UTC')

locations_files = ['./locations.csv', '~/locations.csv']
# Requires columns label, name, latitude, longitude, elevation
# Timezone column is optional, and uses timezones understood by tz
# Date column is optional, and uses whatever date formats ephem accepts
# latitude: positive is North
# longitude: positive is East
# lat and long: dd°mm'ss.ss" should be entered as dd:mm:ss.ss
# elevation is in meters
# pressure will be computed from elevation, will be in mBar
# Location file in this directory is on github. Home area contains
#  personal information, like my house's coordinates.

for f in locations_files:
    if os.path.isfile(f):
        with open(os.path.expandvars(os.path.expanduser(f)), 'r') as csvfile:
            # the skipinitialspace dialect means that ',' or ', ' are fine in between values
            # that way I don't have to run strip on every field
            location_reader = csv.DictReader(csvfile, skipinitialspace=True, delimiter=',')
            for row in location_reader:
                my_locations[row['label']] = {}
                my_locations[row['label']]['observer'] = ephem.Observer()
                my_locations[row['label']]['observer'].name = row['name']
                my_locations[row['label']]['observer'].lat = row['latitude']
                my_locations[row['label']]['observer'].long = row['longitude']
                my_locations[row['label']]['observer'].elevation = float(row['elevation'])
                my_locations[row['label']]['observer'].compute_pressure()
                if 'timezone' in row and row['timezone']:
                    my_locations[row['label']]['timezone'] = pytz.timezone(row['timezone'].strip())
                if 'date' in row and row['date']:
                    my_locations[row['label']]['observer'].date = ephem.Date(row['date'])


def _get_location(name):
    """Return the user-defined location if exists, else return the ephem location.
    """
    if name in my_locations:
        if 'timezone' in my_locations[name]:
            global timezone
            timezone = my_locations[name]['timezone']
        return my_locations[name]['observer']
    ephem_cities = ephem.cities._city_data.keys()
    if name in ephem_cities:
        return ephem.city(name)

def get_location(name=None, temp=None, pressure=None, time=None):
    '''temp must be in deg C, and pressure in mBar'''
    if not name:
        location = default_location
    else:
        location = _get_location(name)
        if not location:
            name = name.title()
            location = _get_location(name)
        if not location:
            name = name.lower()
            location = _get_location(name)
        if not location:
            name = name.upper()
            location = _get_location(name)
    if location and (temp or pressure):
        if temp:
            location.temp = temp
        if pressure:
            location.pressure = pressure
        else:
            location.compute_pressure() # with the new temp
    if location and time:
        location.date = ephem.Date(time)
    return location


# List of cities available by:
# ephem.cities._city_data.keys()
default_location = ephem.city('Columbus')
timezone = pytz.timezone('America/New_York')
#default_location = my_locations['ctio']


def get_location_from_namespace(namespace):
    return get_location(namespace.location, namespace.temp, namespace.pressure, namespace.time)


def time_conversion(ephem_time):
    """Convert from UTC to configured local time.
    """
    if ephem_time:
        global timezone
        return timezone.fromutc(ephem_time.datetime())

def localtime_to_ephem(localtime):
    """Convert a local datetime object to ephem utc date
    """
    global timezone
    return ephem.Date(timezone.localize(localtime).astimezone(pytz.UTC))


class ConvertTempAction(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, 5./9.*(value-32))


location_parser = argparse.ArgumentParser()
location_parser.add_argument('-l', '--location', help='As seen from here (default from config file)')
location_parser.add_argument('-t', '--time', help='year/month/day [hours:minutes:seconds]')
location_parser.add_argument('-p', '--pressure', help='Pressure in mBar')
temp = location_parser.add_mutually_exclusive_group()
temp.add_argument('-C', '--celcius', type=float, dest='temp', help='Temperature in degrees Celcius')
temp.add_argument('-F', '--farenheit', type=float, action=ConvertTempAction, dest='temp', help='Temperature in degrees Farenheight')

default_sleep_time = 8 # hours
