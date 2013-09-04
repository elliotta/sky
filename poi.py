'''Points of Interest'''

import ephem

north_pole = ephem.FixedBody()
north_pole._ra = 0
north_pole._dec = '90.'


south_pole = ephem.FixedBody()
south_pole._ra = 0
south_pole._dec = '-90.'

galactic_center = ephem.FixedBody()
galactic_center._ra = '17:45:40.04'
galactic_center._dec = '-29:00:28.1'

large_magellanic_cloud = ephem.FixedBody()
large_magellanic_cloud._ra = '05:23:34.5'
large_magellanic_cloud._dec = '-69:45:22'

small_magellanic_cloud = ephem.FixedBody()
small_magellanic_cloud._ra = '00:52;44.8'
small_magellanic_cloud._dec = '-72:49:43'
