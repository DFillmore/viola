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

import os
import array
import zcode


data = None
originaldata = None
WORDSIZE = 2


def setup(gamedata):
    global data
    global originaldata
    global filelen
    global WORDSIZE
    data = gamedata[:]

    version = data[0]
    if version < 1 or version > 8:
        return False
    if version == 9:
        WORDSIZE = 4

    filelen = (data[0x1a] << 8) + data[0x1b]
    if filelen == 0:
        filelen = len(data)
    else:
        filelen = zcode.header.filelen()
    data = array.array('B', data)
    originaldata = data[:]
    return True
    
def verify():
    global originaldata
    checksum = 0
    for a in range(0x40, filelen):
        checksum += originaldata[a]
        checksum %= 0x10000
    if checksum == zcode.header.getchecksum():
        return True
    return False

def getbyte(offset):
    global data
    if offset >= len(data):
        zcode.error.fatal("Tried to read a byte beyond available memory at " + hex(offset) + ".")
    return data[offset]

def setbyte(offset, byte):
    global data
    if offset >= len(data):
        zcode.error.fatal("Tried to write a byte beyond available memory at " + hex(offset) + ".")
    byte = zcode.numbers.unneg(byte) & 0xFF 
    data[offset] = int(byte)

def getword(offset):
    global data
    if offset >= len(data):
        zcode.error.fatal("Tried to read a word beyond available memory at " + hex(offset) + ".")
    if WORDSIZE == 2:
        return (data[offset] << 8) + data[offset+1]
    else:
        return (data[offset] << 24) + (data[offset+1] << 16) + (data[offset+2] << 8) + data[offset+3]

def setword(offset, word):
    global data
    if offset >= len(data):
        zcode.error.fatal("Tried to write a word beyond available memory at " + hex(offset) + ".")
    word = zcode.numbers.unneg(word)
    for a in range(WORDSIZE):
        data[offset+a] = (int(word) >> ((WORDSIZE-(a+1))*8)) & 0xFF

def getarray(offset, length):
    return data[offset:offset+length]

def setarray(offset, newdata):
    global data
    for a in range(len(newdata)):
        data[offset+a] = newdata[a]


def wordaddress(address): # this is so simple, and so rare, it seems kinda pointless having it here.
    if address*WORDSIZE >= len(data):
        zcode.error.fatal("Tried to access data beyond available memory at " + hex(offset) + ".")
    return address * WORDSIZE

def unpackaddress(address, type=0):
    if zcode.header.zversion() < 4: # zversions 1, 2 and 3
        return address * 2
    elif zcode.header.zversion() < 6: # zversion 4 and 5
        return address * 4
    elif zcode.header.zversion() < 8: # zversions 6 and 7
        if type == 1: # routine calls
            return (address * 4) + zcode.header.routineoffset()
        elif type == 2: # print_paddr
            return (address * 4) + zcode.header.stringoffset()
    elif zcode.header.zversion() < 9: # zversion 8
        return address * 8
    else: #zversion 9 
        return address

    
