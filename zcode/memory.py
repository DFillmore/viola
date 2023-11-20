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

import os
import sys
import array
import zcode
from zcode.constants import *


data = None
originaldata = None
WORDSIZE = 2
memory_size = 0


def setup(gamedata):
    global data
    global originaldata
    global filelen
    global WORDSIZE
    global memory_size
    data = gamedata[:]
    memory_size = len(data)

    version = data[0]
    if version > 6 and zcode.use_standard == STANDARD_00:
        print('Versions 7 and 8 of the Z-Machine are not available before Standard 0.2')
        sys.exit()
    if version < 1 or version > 8:
        return False

    filelen = int.from_bytes(data[0x1a:0x1c], byteorder='big')
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

    offset = zcode.numbers.unsigned(offset)

    if offset == 0x26 or offset == 0x27:
        zcode.header.updateFontSize() 

    if offset >= memory_size:
        zcode.error.fatal("Tried to read a byte beyond available memory at " + hex(offset) + ".")

    return data[offset]

def setbyte(offset, byte):
    global data
    offset = zcode.numbers.unsigned(offset)

    if offset == 0x11:
        # if the transcription bit is being set, start transcription
        if byte & 1 and (zcode.output.streams[2].active == False):
            zcode.output.openstream(2)
        elif byte & 1 == 0 and (zcode.output.streams[2].active): # if however it has just been unset, stop transcription
            zcode.output.closestream(2)

        if byte & 2 and zcode.screen.fixedpitchbit == False:
            zcode.screen.currentWindow.flushTextBuffer()
            zcode.screen.fixedpitchbit = True
        elif byte & 2 == 0 and zcode.screen.fixedpitchbit:
            zcode.screen.currentWindow.flushTextBuffer()
            zcode.screen.fixedpitchbit = False

    if offset >= zcode.header.statmembase():
        zcode.error.fatal("Tried to write a byte beyond dynamic memory at " + hex(offset) + ".")

    byte = zcode.numbers.unsigned(byte) & 0xFF 
    data[offset] = int(byte)

def getword(offset):
    global data

    offset = zcode.numbers.unsigned(offset)

    if offset == 0x26:
        zcode.header.updateFontSize() 

    if offset >= memory_size:
        zcode.error.fatal("Tried to read a word beyond available memory at " + hex(offset) + ".")
    
    return int.from_bytes(data[offset:offset+2], byteorder='big')
    
def setword(offset, word):
    global data
    
    offset = zcode.numbers.unsigned(offset)

    if offset == 0x10:
        # if the transcription bit is being set, start transcription
        if word & 1 and (zcode.output.streams[2].active == False):
            zcode.output.openstream(2)
        elif word & 1 == 0 and (zcode.output.streams[2].active): # if however it being unset, stop transcription
            zcode.output.closestream(2)
        if word & 2 and zcode.screen.fixedpitchbit == False:
            zcode.screen.currentWindow.flushTextBuffer()
            zcode.screen.fixedpitchbit = True
        elif word & 2 == 0 and zcode.screen.fixedpitchbit:
            zcode.screen.currentWindow.flushTextBuffer()
            zcode.screen.fixedpitchbit = False

    if offset >= zcode.header.statmembase():
        zcode.error.fatal("Tried to write a word beyond dynamic memory at " + hex(offset) + ".")

    word = zcode.numbers.unsigned(word)
    data[offset:offset+WORDSIZE] = array.array(data.typecode, int.to_bytes(word, WORDSIZE, byteorder='big'))


def getarray(offset, length):
    offset = zcode.numbers.unsigned(offset)
    return data[offset:offset+length]

def setarray(offset, newdata):
    global data
    offset = zcode.numbers.unsigned(offset)
    if len(newdata) + offset > zcode.header.statmembase():
        zcode.error.fatal("Tried to write a word beyond dynamic memory at " + hex(offset+len(newdata)) + ".")
    data[offset:offset+len(newdata)] = array.array(data.typecode, newdata)


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
    elif zcode.header.zversion() == 8: # zversion 8
        return address * 8

    
