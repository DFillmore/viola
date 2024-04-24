# Copyright (C) 2001 - 2024 David Fillmore
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

errors = []


def fatal(message):
    try:
       for a in range(1, 3):
           zcode.output.streams[a].write('Fatal Error: ' + str(message))
    except:
        pass 
    print('Fatal Error:', message, file=sys.stderr)
    sys.exit()


def strictz(message):
    global errors, strictzlevel
    if strictzlevel == 0:  # ignore all levels
        pass
    elif strictzlevel == 1:  # report first error
        if message not in errors:
            for a in range(1, 3):
                zcode.output.streams[a].write('Warning: ' + str(message) + ' (will ignore further occurences)\r')
            errors.append(message)
    elif strictzlevel == 2:  # report all errors
        for a in range(1, 3):
            zcode.output.streams[a].write('Warning: ' + str(message) + '\r')
    else:  # exit after any error
        for a in range(1, 3):
            zcode.output.streams[a].write('Fatal Error: ' + str(message) + '\r')
        zcode.routines.quit = 1


def warning(message):
    for a in range(1, 3):
        zcode.output.streams[a].write('Warning: ' + str(message) + '\r')
