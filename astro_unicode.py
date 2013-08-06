#!/usr/bin/env python
# vim: set fileencoding=utf-8> :

import unicodedata


def to_unicode(ascii):
    name = ascii.strip().upper()
    if name == 'MARS':
        return unicodedata.lookup('MALE SIGN')
    elif name == 'VENUS':
        return unicodedata.lookup('FEMALE SIGN')
    elif name == 'MOON':
        # There are two moons: first and last quarter
        # First quarter matches the alchemical moon symbol
        return unicodedata.lookup('FIRST QUARTER MOON')
    try:
        return unicodedata.lookup(name)
    except KeyError:
        return None


if __name__ == '__main__':
    import sys
    symbols = [to_unicode(w) for w in sys.argv[1:]]
    print u' '.join(symbols)

