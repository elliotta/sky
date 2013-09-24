#!/usr/bin/env python

import time

import ephem

import config

parser = config.location_parser
parser.description = 'For given RA and Dec, print the current az and alt'
parser.add_argument('ra', type=str, help='Right Ascention')
parser.add_argument('dec', type=str, help='Declination')
parser.add_argument('-i', '--interval', type=float, default=5., help='Seconds between updates')
args = parser.parse_args()
location = config.get_location_from_namespace(args)

print args.ra, args.dec

shiny = ephem.FixedBody()
shiny._ra = args.ra
shiny._dec = args.dec

counter = 0
while True:
    try:
        location.date = ephem.now()
        shiny.compute(location)
        if not counter % 15:
            print 'ra,dec', shiny.ra, shiny.dec
        print shiny.az, shiny.alt
        counter = counter + 1
        time.sleep(args.interval)
    except KeyboardInterrupt:
        break

