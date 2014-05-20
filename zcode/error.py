# Copyright (C) 2001 - 2014 David Fillmore
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
#
# You should have received a copy of the GNU General Public License
# along with Viola; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import sys
import zcode


strictzlevel = 1

errors = []

def fatal(message):
    for a in range(1,3):
        zcode.output.streams[a].write('Fatal Error: ' + str(message))
    print('Fatal Error:', message, file=sys.stderr)
    sys.exit()

def strictz(message):
    global errors, strictzlevel
    if strictzlevel == 0: # ignore all levels
        pass
    elif strictzlevel == 1: # report first error 
        if message not in errors:
            for a in range(1,3):
                zcode.output.streams[a].write('Warning: ' + str(message) + ' (will ignore further occurences)\r')
            errors.append(message)
    elif strictzlevel == 2: # report all errors
        for a in range(1,3):
            zcode.output.streams[a].write('Warning: ' + str(message) + '\r')
    else: # exit after any error
        for a in range(1,3):
            zcode.output.streams[a].write('Fatal Error: ' + str(message) + '\r')
        routines.quit = 1

def warning(message):
    for a in range(1,3):
        zcode.output.streams[a].write('Warning: ' + str(message) + '\r')
