#!/usr/bin/env python

import sys
import json

import config
import ephem

here = config.my_locations['ctio']

def main(start_time, alt_az_file, out_file):
    here.date = start_time
    f = open(alt_az_file)
    exposures = []
    for line in f:
        if not line.startswith('#'):
            az, alt = line.split()
            az.strip()
            alt.strip()
            ra, dec = here.radec_of(az,alt)
            print here.date, az, alt, '=', ra, dec
            exposures.append({'expType':'object',
                              'filter':'r',
                              'expTime':30,
                              'object':'Hexapod LUT',
                              'RA': str(ra),
                              'dec': str(dec),
                              'exclude': '[GUIDER, AOS]'
                             })
            here.date = here.date + ephem.minute*1.6
    f_out = open(out_file, 'w')
    f_out.write(json.dumps(exposures))


if __name__ == '__main__':
    now = ephem.now()
    print "Current time is %s" % now
    main(now + ephem.minute*float(sys.argv[1]), sys.argv[2], sys.argv[3])



