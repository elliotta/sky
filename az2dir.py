# vim: set fileencoding=utf-8> :
# Convert numers to symbols from a list of evenly spaced, cyclic symbols.
# First symbol starts with its center at zero.

from math import pi

import ephem

cardinals = ('N', 'E', 'S', 'W')
principal_winds = ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')
compass16 = ('N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW')
compass32 = ('N', 'NbE', 'NNE', 'NEbN', 'NE', 'NEbE', 'ENE', 'EbN', 'E', 'EbS', 'ESE', 'SEbE', 'SE', 'SEbS', 'SSE', 'SbE',  'S', 'SbW', 'SSW', 'SWbS', 'SW', 'SWbW', 'WSW', 'WbS', 'W', 'WbN', 'WNW', 'NWbW', 'NW', 'NWbN', 'NNW', 'NbW')
zodiac = ('Aries', 'Taurus', 'Gemini',
          'Cancer', 'Leo', 'Virgo',
          'Libra', 'Scorpius', 'Sagittarius',
          'Capricorn', 'Aquarius', 'Pisces')
zodiac_abbr = ('Ari', 'Tau', 'Gem',
               'Cnc', 'Leo', 'Vir',
               'Lib', 'Sco', 'Sgr',
               'Cap', 'Aqr', 'Psc')
zodiac_unicode = (u'♈', u'♉', u'♊',
                  u'♋', u'♌', u'♍',
                  u'♎', u'♏', u'♐',
                  u'♑', u'♒', u'♓')


def number2symbol(number, cycle_size, symbol_list):
    n_symbols = len(symbol_list)
    number_per_symbol = cycle_size/n_symbols
    return symbol_list[int((number + number_per_symbol/2.)/number_per_symbol)%n_symbols]

def degrees2symbol(degrees, symbol_list):
    return number2symbol(degrees, 360, symbol_list)


def radians2symbol(radians, symbol_list):
    return number2symbol(radians, 2*pi, symbol_list)
    

def az2cardinal(azimuth):
    # Convert aziumth in radians to the nearest cardianl direction
    return radians2symbol(azimuth, cardinals)


def az2dir(azimuth):
    # Convert aziumth in radians to the nearest principal wind
    return radians2symbol(azimuth, principal_winds)


# Note that the zodiac as evenly spaced units do not necessary correlate with the associated asterism
# The zodiac is traditionally measured by the longitude along the ecliptic, with Ares at zero.
# Substituding ra for longitude might give close enough results
def ra2zodiac(longitude, unicode_symbol=False):
    global zodiac
    global zodiac_unicode
    if unicode_symbol:
        z = zodiac_unicode
    else:
        z = zodiac
    if isinstance(longitude, ephem.Body):
        return radians2symbol(ephem.Ecliptic(longitude).lon, z)
    return radians2symbol(longitude, z)


