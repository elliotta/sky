import ephem

import az2dir

def sun_sign(location):
    sun = ephem.Sun(location)
    return az2dir.zodiac_sign(sun)


def moon_sign(location):
    moon = ephem.Moon(location)
    return az2dir.zodiac_sign(moon)


def rising_sign(location):
    ra = location.radec_of('90:00:0.0', 0)[0]
    return az2dir.zodiac_sign(ra)
