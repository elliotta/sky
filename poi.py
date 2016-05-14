'''Points of Interest

This is a collection of interesting (to me, at least) things in the sky,
some of which are not built-in to ephem. They are stored here for easy use
in other scripts, particularly in today.py.
'''

import ephem

# Celestial Poles
north_pole = ephem.FixedBody()
north_pole._ra = 0
north_pole._dec = '90.'

south_pole = ephem.FixedBody()
south_pole._ra = 0
south_pole._dec = '-90.'

# The center of the galaxy
galactic_center = ephem.FixedBody()
galactic_center._ra = '17:45:40.04'
galactic_center._dec = '-29:00:28.1'

# The magellanic clouds
large_magellanic_cloud = ephem.FixedBody()
large_magellanic_cloud._ra = '05:23:34.5'
large_magellanic_cloud._dec = '-69:45:22'

small_magellanic_cloud = ephem.FixedBody()
small_magellanic_cloud._ra = '00:52:44.8'
small_magellanic_cloud._dec = '-72:49:43'

# The center of the Southern Cross
# Constellation contains star Mimosa, which ephem knows about
crux = ephem.FixedBody()
crux._ra = '12:30:00.0'
crux._dec = '-60:00:00.0'

coalsack = ephem.FixedBody()
coalsack._ra = '12:50:00'
coalsack._dec = '-62:30:00'


class Asterism(dict):
    """An asterism is a group of stars (or other fixed bodies).

    This call will treat a collection of fixed bodies as a group
    so that compute calls need only happen once for the group, and 
    a check can be done to see if the entire asterism is above the
    horizon.
    """

    def compute(self, location):
        for body in self.itervalues():
            body.compute(location)

    def is_up(self):
        for body in self.itervalues():
            if body.alt < 0:
                return False
        return True

    def add_stars(self, *args):
        """From a list of strings, add the given stars to the asterism.

        These stars must be in epehem's database.
        """
        for s in args:
            self[s.lower()] = ephem.star(s)


summer_triangle = Asterism(deneb=ephem.star('Deneb'), altair=ephem.star('Altair'), vega=ephem.star('Vega'))

winter_hexagon = Asterism()
winter_hexagon.add_stars('Rigel', 'Aldebaran', 'Capella', 'Pollux', 'Procyon', 'Sirius')

def bodies(location, planets=True, poles=True, galaxy=True, winter_hexagon=True, summer_triangle=True):
    """Return a dictionary with pretty names and ephem bodies for the desired things.
    """
    #bodies = collections.OrderedDict() # want to be able to reference them by name
    bodies = {'Sun': ephem.Sun(location),
              'Moon': ephem.Moon(location)
             }
    if galaxy:
        bodies['Galaxy'] = galactic_center
        bodies['Galaxy'].compute(location)
        bodies['LMC'] = large_magellanic_cloud
        bodies['LMC'].compute(location)
        bodies['SMC'] = small_magellanic_cloud
        bodies['SMC'].compute(location)
        bodies['Crux'] = crux
        bodies['Crux'].compute(location)
        bodies['Coalsack'] = coalsack
        bodies['Coalsack'].compute(location)
    if planets:
        for body in  ('Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune'):
            bodies[body] = getattr(ephem, body)(location)
    if winter_hexagon:
        for star in ('Sirius', 'Rigel', 'Betelgeuse', 'Aldebaran', 'Capella', 'Pollux', 'Procyon'):
            bodies[star] = ephem.star(star, location)
    if summer_triangle:
        for star in ('Deneb', 'Altair', 'Vega'):
            bodies[star] = ephem.star(star, location)
    return bodies
