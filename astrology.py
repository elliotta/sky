import ephem

import az2dir

def sun_sign(location):
    sun = ephem.Sun(location)
    return az2dir.ra2zodiac(sun)


def moon_sign(location):
    moon = ephem.Moon(location)
    return az2dir.ra2zodiac(moon)


def rising_sign(location):
    ra = location.radec_of('90:00:0.0', 0)[0]
    return az2dir.ra2zodiac(ra)
