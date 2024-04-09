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

import functools
import sys

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

    originaldata = gamedata[:]
    data = bytearray(gamedata)

    memory_size = len(data)

    version = data[0]
    if version > 6 and zcode.use_standard == STANDARD_00:
        print('Versions 7 and 8 of the Z-Machine are not available before Standard 0.2')
        sys.exit()
    if version < 1 or version > 8:
        return False

    filelen = int.from_bytes(data[0x1a:0x1c], byteorder='big')
    # in the header, the file lenth may be 0, in which case it is figured it out manually.
    if filelen == 0:
        filelen = len(data)
    elif version < 4:  # versions 1 to 3
        filelen *= 2
    elif version < 6:  # versions 4 and 5
        filelen *= 4
    elif version < 9:  # versions 6, 7 and 8
        filelen *= 8

    return True


def verify():
    global originaldata
    checksum = sum(originaldata[0x40:zcode.header.filelen]) % 0x10000
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
        if byte & 1 and not zcode.output.streams[2].active:
            zcode.output.openstream(2)
        elif byte & 1 == 0 and zcode.output.streams[2].active:  # if however it has just been unset, stop transcription
            zcode.output.closestream(2)

        if not (byte & 2 and zcode.screen.fixedpitchbit):
            zcode.screen.currentWindow.flushTextBuffer()
            zcode.screen.fixedpitchbit = True
        elif byte & 2 == 0 and zcode.screen.fixedpitchbit:
            zcode.screen.currentWindow.flushTextBuffer()
            zcode.screen.fixedpitchbit = False

    if offset >= zcode.header.statmembase:
        zcode.error.fatal("Tried to write a byte beyond dynamic memory at " + hex(offset) + ".")

    byte = zcode.numbers.unsigned(byte) & 0xFF
    data[offset] = int(byte)


static_words = {}


def getword(offset):
    global data
    global static_words
    if offset in static_words:
        return static_words[offset]

    offset = zcode.numbers.unsigned(offset)

    if offset == 0x26:
        zcode.header.updateFontSize()

    if offset >= memory_size:
        zcode.error.fatal("Tried to read a word beyond available memory at " + hex(offset) + ".")

    value = int.from_bytes(data[offset:offset + WORDSIZE], byteorder='big')

    if offset > zcode.header.statmembase:
        static_words[offset] = value

    return value


def setword(offset, word):
    global data

    offset = zcode.numbers.unsigned(offset)

    if offset == 0x10:
        # if the transcription bit is being set, start transcription
        if word & 1 and (zcode.output.streams[2].active == False):
            zcode.output.openstream(2)
        elif word & 1 == 0 and zcode.output.streams[2].active:  # if however it is being unset, stop transcription
            zcode.output.closestream(2)
        if word & 2 and zcode.screen.fixedpitchbit == False:
            zcode.screen.currentWindow.flushTextBuffer()
            zcode.screen.fixedpitchbit = True
        elif word & 2 == 0 and zcode.screen.fixedpitchbit:
            zcode.screen.currentWindow.flushTextBuffer()
            zcode.screen.fixedpitchbit = False

    if offset >= zcode.header.statmembase:
        zcode.error.fatal("Tried to write a word beyond dynamic memory at " + hex(offset) + ".")

    word = zcode.numbers.unsigned(word)
    data[offset:offset + WORDSIZE] = int.to_bytes(word, WORDSIZE, byteorder='big')


def getarray(offset, length):
    offset = zcode.numbers.unsigned(offset)
    return data[offset:offset + length]


def getwordarray(offset, length):
    offset = zcode.numbers.unsigned(offset)
    return [int.from_bytes(a, byteorder='big') for a in zip(*(iter(getarray(offset, length * WORDSIZE)),) * WORDSIZE)]


def setarray(offset, newdata):
    global data
    offset = zcode.numbers.unsigned(offset)
    if len(newdata) + offset > zcode.header.statmembase:
        zcode.error.fatal("Tried to write a word beyond dynamic memory at " + hex(offset + len(newdata)) + ".")
    data[offset:offset + len(newdata)] = newdata[:]


@functools.lru_cache(maxsize=128)
def wordaddress(address):  # this is so simple, and so rare, it seems kinda pointless having it here.
    if address * WORDSIZE >= len(data):
        zcode.error.fatal("Tried to access data beyond available memory at " + hex(address) + ".")
    return address * WORDSIZE


@functools.lru_cache(maxsize=128)
def unpackaddress(address, type=0):
    if zcode.header.zversion < 4:  # zversions 1, 2 and 3
        return address * 2
    elif zcode.header.zversion < 6:  # zversion 4 and 5
        return address * 4
    elif zcode.header.zversion < 8:  # zversions 6 and 7
        if type == 1:  # routine calls
            return (address * 4) + zcode.header.roffset
        elif type == 2:  # print_paddr
            return (address * 4) + zcode.header.soffset
    elif zcode.header.zversion == 8:  # zversion 8
        return address * 8
