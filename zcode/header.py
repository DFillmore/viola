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

import zcode
from zcode.constants import *

standards = [(0,0), (0,2), (1,0), (1,1)]

ZVERSION_ADDRESS = 0x0
FLAGS1_ADDRESS = 0x1
RELEASE_ADDRESS = 0x2
HIGHMEM_ADDRESS = 0x4
INITIALPC_ADDRESS = 0x6
DICTIONARY_ADDRESS = 0x8
OBJECTS_ADDRESS = 0xA
GLOBALS_ADDRESS = 0xC
STATICMEM_ADDRESS = 0xE
FLAGS2_ADDRESS = 0x10
SERIAL_ADDRESS = 0x12
ABBREVS_ADDRESS = 0x18
FILELEN_ADDRESS = 0x1A
CHECKSUM_ADDRESS = 0x1C
TERPNUM_ADDRESS = 0x1E
TERPVER_ADDRESS = 0x1F
SLINES_ADDRESS = 0x20
SCHARS_ADDRESS = 0x21
SWIDTH_ADDRESS = 0x22
SHEIGHT_ADDRESS = 0x24
FWIDTH_ADDRESS = 0x26
FHEIGHT_ADDRESS = 0x27
ROFFSET_ADDRESS = 0x28
SOFFSET_ADDRESS = 0x2A
BG_ADDRESS = 0x2C
FG_ADDRESS = 0x2D
TERMCHARS_ADDRESS = 0x2E
TEXTWIDTH_ADDRESS = 0x30
STANDARD_ADDRESS = 0x32
ALPHATABLE_ADDRESS = 0x34
HEADEREXT_ADDRESS = 0x36

TERP_DEC      = 1  # DECSystem-20
TERP_APPLEE   = 2  # Apple IIe
TERP_MAC      = 3  # Macintosh
TERP_AMIGA    = 4  # Amiga
TERP_ATARI    = 5  # Atari ST
TERP_IBM      = 6  # IBM PC
TERP_C128     = 7  # Commodore 128
TERP_C64      = 8  # Commodore 64
TERP_APPLEC   = 9  # Apple IIc
TERP_APPLEGS = 10  # Apple IIgs
TERP_TANDY   = 11  # Tandy Color

TERP_NUMBER = TERP_IBM


def setup():  # set all the relevant bits and bytes and words in the header
    global zversion, release, highmembase, startat, dictionaryloc, objtableloc, globalsloc, statmembase, serial, abbrevtableloc
    global checksum, roffset, soffset, termcharloc, alphatableloc, headerextloc
    global FWIDTH_ADDRESS, FHEIGHT_ADDRESS

    statmembase = int.from_bytes(zcode.memory.data[STATICMEM_ADDRESS:STATICMEM_ADDRESS+zcode.memory.WORDSIZE], byteorder='big')
    

    zversion = zcode.memory.getbyte(0)
    release = zcode.memory.getword(RELEASE_ADDRESS)
    highmembase = zcode.memory.getword(HIGHMEM_ADDRESS)
    startat = zcode.memory.getword(INITIALPC_ADDRESS)
    dictionaryloc = zcode.memory.getword(DICTIONARY_ADDRESS)
    objtableloc = zcode.memory.getword(OBJECTS_ADDRESS)
    globalsloc = zcode.memory.getword(GLOBALS_ADDRESS)

    serial = ''.join([chr(c) for c in zcode.memory.getarray(SERIAL_ADDRESS, 6)])
    abbrevtableloc = zcode.memory.getword(ABBREVS_ADDRESS)

    # filelen is set and used in the memory module

    checksum = zcode.memory.getword(CHECKSUM_ADDRESS)

    if zversion == 6:
        roffset = zcode.memory.getword(ROFFSET_ADDRESS) * 8
        soffset = zcode.memory.getword(SOFFSET_ADDRESS) * 8

    termcharloc = zcode.memory.getword(TERMCHARS_ADDRESS)
    alphatableloc = zcode.memory.getword(ALPHATABLE_ADDRESS)
    headerextloc = zcode.memory.getword(HEADEREXT_ADDRESS)

    if zversion == 6:
        FWIDTH_ADDRESS = 0x27
        FHEIGHT_ADDRESS = 0x26

    # Flags 1
    if zversion == 3:
        setflag(1, 4, 0)  # status line is available
        setflag(1, 5, 1)  # screen splitting is available
        setflag(1, 6, 0)  # The default font is not fixed-pitch
    elif zversion < 9:
        setflag(1, 2, zcode.screen.supportedstyles(2))  # Boldface
        setflag(1, 3, zcode.screen.supportedstyles(4))  # Italic
        setflag(1, 4, zcode.screen.supportedstyles(8))  # Fixed-pitch style
        if zcode.use_standard >= STANDARD_02:  # from 0.2 onward
            setflag(1, 7, 1)  # Timed input
        if zversion > 4:
            setflag(1, 0, zcode.screen.supportedgraphics(0))  # Colours
        if zversion == 6:
            setflag(1, 1, zcode.screen.supportedgraphics(3))  # Picture displaying
        if zcode.sounds.availablechannels(0) + zcode.sounds.availablechannels(1) > 0:  # if any effect or music channels are available, sound effects are available
            setflag(1, 5, 1)  # sound effects
        else:
            setflag(1, 5, 0)

    # Flags 2 - If unset by the game, the terp should leave them like that.
    if zversion > 4:
        if getflag(2, 3):  # pictures
            setflag(2, 3, zcode.screen.supportedgraphics(3))
        if getflag(2, 4):  # undo
            setflag(2, 4, 1)
        if getflag(2, 5):  # mouse
            setflag(2, 5, 1)
        if getflag(2, 6):  # colours
            setflag(2, 6, zcode.screen.supportedgraphics(0))
        if getflag(2, 7):  # sound effects
            if zcode.screen.supportedgraphics(0) + zcode.screen.supportedgraphics(1) > 0:
                setflag(2, 7, 1)
            else:
                setflag(2, 7, 0)
        if getflag(2, 8):  # menus
            setflag(2, 8, 0)

    # Flags 3 - If unset by the game, the terp should leave them like that. All unknown bits should be set to 0.
    if zversion > 4:
        if getflag(3, 0):  # transparency
            setflag(3, 0, zcode.screen.supportedgraphics(2))
        for a in range(1, 16):  # set all the other bits to 0, because we don't know what they do
            setflag(3, a, 0)

    if zversion > 3:
        # Interpreter number
        setterpnum(TERP_NUMBER)
        # Interpreter version
        setterpversion(ord('V'))

    updateSizes()

    if zversion > 4:
        # Default foreground colour
        setdeffgcolour(zcode.screen.DEFFOREGROUND)
        # Default background colour
        setdefbgcolour(zcode.screen.DEFBACKGROUND)
        settruedefaultforeground(zcode.screen.spectrum[2])
        settruedefaultbackground(zcode.screen.spectrum[9])
    # Z-machine Standard number
    m = standards[zcode.use_standard][0]
    n = standards[zcode.use_standard][1]
    setstandardnum(m, n)


def updateFontSize():
    if zversion > 4:
        # Font width 
        if zcode.screen.graphics_mode == 1:
            setfontwidth(zcode.screen.currentWindow.getFont().getWidth())
        else:
            setfontwidth(1)
        # Font height
        if zcode.screen.graphics_mode == 1:
            setfontheight(zcode.screen.currentWindow.getFont().getHeight())
        else:
            setfontheight(1)


def updateSizes():
    if zversion > 3:
        columns = int(zcode.screen.ioScreen.getWidth() // zcode.screen.getWindow(1).getFont().getWidth())
        # Screen height (lines)
        setscreenheightlines(int(zcode.screen.ioScreen.getHeight() // zcode.screen.getWindow(1).getFont().getHeight()))
        # Screen width (chars)
        setscreenwidthchars(columns)

    if zversion > 4:
        # Screen width (units)
        if zcode.screen.graphics_mode == 1:
            setscreenwidth(zcode.screen.ioScreen.getWidth())
        else:
            setscreenwidth(columns)
        # Screen height (units)
        if zcode.screen.graphics_mode == 1:
            setscreenheight(zcode.screen.ioScreen.getHeight())
        else:
            setscreenheight(int(zcode.screen.ioScreen.getHeight() // zcode.screen.getWindow(1).getFont().getHeight()))
        updateFontSize()


def identifier():
    return str(release) + "." + serial


def getflag(bitmap,
            bit):  # bitmap is the set of flags to look in, such as flags 1, bit is the bit number to check, such as bit 1 for z3 status line type checking
    if bitmap == 1:
        flag = pow(2, bit)
        if zcode.memory.getbyte(FLAGS1_ADDRESS) & flag == flag:
            return 1
        else:
            return 0
    elif bitmap == 2:
        flag = pow(2, bit)
        if zcode.memory.getword(FLAGS2_ADDRESS) & flag == flag:
            return 1
        else:
            return 0
    elif bitmap == 3:
        if headerextsize() < 4:
            return 0
        else:
            flag = pow(2, bit)
            if zcode.memory.getword(headerextloc() + 4) & flag == flag:
                return 1
            else:
                return 0


def setflag(bitmap, bit, value):
    # bitmap is the set of flags to look in, bit is the bit number to change, value is either 1 for on or 0 for off
    global flags1, flags2
    if bitmap == 1:
        flag = pow(2, bit)
        if value:
            zcode.memory.setbyte(FLAGS1_ADDRESS, zcode.memory.getbyte(FLAGS1_ADDRESS) | flag)
        else:
            zcode.memory.setbyte(FLAGS1_ADDRESS, zcode.memory.getbyte(FLAGS1_ADDRESS) & ~flag)
    elif bitmap == 2:
        flag = pow(2, bit)
        if value:
            zcode.memory.setword(FLAGS2_ADDRESS, zcode.memory.getword(FLAGS2_ADDRESS) | flag)
        else:
            zcode.memory.setword(FLAGS2_ADDRESS, zcode.memory.getword(FLAGS2_ADDRESS) & ~flag)
    elif bitmap == 3:
        if headerextsize() >= 4:
            flag = pow(2, bit)
            if value:
                zcode.memory.setword(headerextloc() + 8, zcode.memory.getword(headerextloc() + 8) | flag)
            else:
                zcode.memory.setword(headerextloc() + 8, zcode.memory.getword(headerextloc() + 8) & ~flag)


def setterpnum(number):
    zcode.memory.setbyte(TERPNUM_ADDRESS, number)


def setterpversion(number):
    zcode.memory.setbyte(TERPVER_ADDRESS, number)


def getterpnum():
    return zcode.memory.getbyte(TERPNUM_ADDRESS)


def getterpversion():  # I doubt this will be needed
    return zcode.memory.getbyte(TERPVER_ADDRESS)


def getscreenheightlines():
    return zcode.memory.getbyte(SLINES_ADDRESS)


def getscreenwidthchars():
    return zcode.memory.getbyte(SCHARS_ADDRESS)


def getscreenwidth():  # screen width in units
    return zcode.memory.getword(SWIDTH_ADDRESS)


def getscreenheight():  # screen height in units
    return zcode.memory.getword(SHEIGHT_ADDRESS)


def getfontwidth():
    return zcode.memory.getbyte(FWIDTH_ADDRESS)


def getfontheight():
    return zcode.memory.getbyte(FHEIGHT_ADDRESS)


def setscreenheightlines(lines):
    zcode.memory.setbyte(SLINES_ADDRESS, lines)


def setscreenwidthchars(chars):
    zcode.memory.setbyte(SCHARS_ADDRESS, chars)


def setscreenwidth(units):  # screen width in units
    zcode.memory.setword(SWIDTH_ADDRESS, units)


def setscreenheight(units):  # screen height in units
    zcode.memory.setword(SHEIGHT_ADDRESS, units)


def setfontwidth(units):
    zcode.memory.setbyte(FWIDTH_ADDRESS, units)


def setfontheight(units):
    zcode.memory.setbyte(FHEIGHT_ADDRESS, units)


def setdefbgcolour(colour):
    zcode.memory.setbyte(BG_ADDRESS, colour)


def setdeffgcolour(colour):
    zcode.memory.setbyte(FG_ADDRESS, colour)


def getdefbgcolour():
    return zcode.memory.getbyte(BG_ADDRESS)


def getdeffgcolour():
    return zcode.memory.getbyte(FG_ADDRESS)


def settextwidth(len):  # total width in units of text sent to output stream 3
    zcode.memory.setword(TEXTWIDTH_ADDRESS, len)


def setstandardnum(n, m):  # for standard 1.0, setstandardnum(1, 0) would be sent.
    zcode.memory.setbyte(STANDARD_ADDRESS, n)
    zcode.memory.setbyte(STANDARD_ADDRESS + 1, m)


def getstandardnum():
    n = zcode.memory.getbyte(STANDARD_ADDRESS)
    m = zcode.memory.getbyte(STANDARD_ADDRESS + 1)
    return (n, m)


# header extension stuff

header_extension_size = None


def headerextsize():
    global header_extension_size
    if header_extension_size == None:
        if headerextloc == 0:
            header_extension_size = 0
        else:
            header_extension_size = zcode.memory.getword(headerextloc)
    return header_extension_size


def setHeaderExtWord(word, value):
    if headerextsize() < word:
        return 0
    zcode.memory.setword(headerextloc() + (word * 2), value)


def getHeaderExtWord(word):
    if headerextsize() < word:
        return 0
    else:
        return zcode.memory.getword(headerextloc + (word * 2))


def setmousex(xpos):
    setHeaderExtWord(1, xpos)


def setmousey(ypos):
    setHeaderExtWord(2, ypos)


unicode_table = None


def unicodetableloc():
    global unicode_table
    if unicode_table == None:
        unicode_table = getHeaderExtWord(3)
    return unicode_table


# Standard 1.1 stuff below

def settruedefaultforeground(colour):
    setHeaderExtWord(5, colour)


def settruedefaultbackground(colour):
    setHeaderExtWord(6, colour)


def gettruedefaultforeground():
    return getHeaderExtWord(5)


def gettruedefaultbackground():
    return getHeaderExtWord(6)

