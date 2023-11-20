# Copyright (C) 2001 - 2019 David Fillmore
#
# This file is part of Viola.
#
# Viola is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Viola is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import sys
import zcode


strictzlevel = 1

errors = set()

def fatal(message, stream=1):
    zcode.output.printtext('Fatal Error: ' + str(message) + '\r', error=True)
    print('Fatal Error:', message, file=sys.stderr)
    zcode.routines.quit = 1

def strictz(message):
    global errors, strictzlevel
    if strictzlevel == 0: # ignore all levels
        return False

    ignore = False
    for stream in zcode.output.streams:
        if stream: # because stream 0 is None
            if strictzlevel == 3: # exit after any error
                fatal(message, stream)
            if strictzlevel == 1: # report first error only
                if message in errors: 
                    continue
                ignore = True
                errors.add(message)
            warning(message, stream, ignore)

def warning(message, stream=1, ignore=False):
    w =  'Warning: ' + str(message)
    if ignore:
        w += ' (will ignore further occurences)'
    w += '\r'
    zcode.output.printtext(w, error=True)
