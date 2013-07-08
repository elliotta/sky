# vim: set fileencoding=utf-8> :
# This is a set of configuration option used by the
#  other files in this directory.

import argparse
import os
import csv

import ephem

my_locations = {}

locations_files = ['./locations.csv', '~/locations.csv']
# Requires columns label, name, latitude, longitude, elevation
# Date column is optional, and uses whatever date formats ephem accepts
# latitude: positive is North
# longitude: positive is East
# lat and long: dd°mm'ss.ss" should be entered as dd:mm:ss.ss
# elevation is in meters
# pressure will be computed from elevation, will be in mBar
# Location file in this directory is on github. Home area contains
#  personal information, like my house's coordinates.

for f in locations_files:
    with open(os.path.expandvars(os.path.expanduser(f)), 'rb') as csvfile:
        # the skipinitialspace dialect means that ',' or ', ' are fine in between values
        # that way I don't have to run strip on every field
        location_reader = csv.DictReader(csvfile, skipinitialspace=True, delimiter=',')
        for row in location_reader:
            my_locations[row['label']] = ephem.Observer()
            my_locations[row['label']].name = row['name']
            my_locations[row['label']].lat = row['latitude']
            my_locations[row['label']].long = row['longitude']
            my_locations[row['label']].elevation = float(row['elevation'])
            my_locations[row['label']].compute_pressure()
            if 'date' in row and row['date']:
                my_locations[row['label']].date = ephem.Date(row['date'])


# List of cities available by:
# ephem.cities._city_data.keys()
default_location = ephem.city('Columbus')
#default_location = my_locations['ctio']


def _get_location(name):
    ephem_cities = ephem.cities._city_data.keys()
    if name in ephem_cities:
        return ephem.city(name)
    if name in my_locations:
        return my_locations[name]

def get_location(name=None, temp=None, pressure=None):
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
    return location


def get_location_from_namespace(namespace):
    return get_location(namespace.location, namespace.temp, namespace.pressure)


def time_conversion(ephem_time):
    # just return ephem_time for UTC
    # note that some times are None
    if ephem_time:
        return ephem.localtime(ephem_time)
    else:
        return ephem_time


class ConvertTempAction(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, 5./9.*(value-32))


location_parser = argparse.ArgumentParser()
location_parser.add_argument('-l', '--location', help='As seen from here (default from config file)')
location_parser.add_argument('-p', '--pressure', help='Pressure in mBar')
temp = location_parser.add_mutually_exclusive_group()
temp.add_argument('-C', '--celcius', type=float, dest='temp', help='Temperature in degrees Celcius')
temp.add_argument('-F', '--farenheit', type=float, action=ConvertTempAction, dest='temp', help='Temperature in degrees Farenheight')

default_sleep_time = 8 # hours
