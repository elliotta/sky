#!/usr/bin/env python

import time

import ephem

import config

parser = config.location_parser
parser.description = 'For given RA and Dec, print the current az and alt'
parser.add_argument('ra', help='Right Ascention')
parser.add_argument('dec', help='Declination')
parser.add_argument('-i', '--interval', type=float, default=5., help='Seconds between updates')
args = parser.parse_args()
location = config.get_location_from_namespace(args)

shiny = ephem.FixedBody()
shiny._ra = args.ra
shiny._dec = args.dec

while True:
    try:
        location.date = ephem.now()
        shiny.compute(location)
        print shiny.az, shiny.alt
        time.sleep(args.interval)
    except KeyboardInterrupt:
        break

