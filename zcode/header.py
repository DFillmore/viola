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

import string

import zcode
from zcode.constants import *

standards = [(0,0), (0,2), (1,0), (1,1)]


def setup(): # set all the relevant bits and bytes and words in the header
    # Flags 1
    if zversion() == 3:
        setflag(1, 4, 0) # status line is available
        setflag(1, 5, 1) # screen splitting is available
        setflag(1, 6, 0) # The default font is not fixed-pitch
    elif zversion() < 9:
        setflag(1, 2, zcode.screen.supportedstyles(2)) # Boldface
        setflag(1, 3, zcode.screen.supportedstyles(4)) # Italic
        setflag(1, 4, zcode.screen.supportedstyles(8)) # Fixed-pitch style
        if zcode.use_standard >= STANDARD_02: # from 0.2 onward
            setflag(1, 7, 1) # Timed input
        if zversion() > 4:
            setflag(1, 0, zcode.screen.supportedgraphics(0)) # Colours
        if zversion() == 6:
            setflag(1, 1, zcode.screen.supportedgraphics(3)) # Picture displaying
        if zcode.sounds.availablechannels(0) + zcode.sounds.availablechannels(1) > 0: # if any effect or music channels are available, sound effects are available
            setflag(1, 5, 1) # sound effects
        else:
            setflag(1, 5, 0)


    # Flags 2 - If unset by the game, the terp should leave them like that.
    if zversion() > 4:
        if getflag(2, 3): # pictures
            setflag(2, 3, zcode.screen.supportedgraphics(3))
        if getflag(2, 4): # undo
            setflag(2, 4, 1)            
        if getflag(2, 5): # mouse
            setflag(2, 5, 1)
        if getflag(2, 6): # colours
            setflag(2, 6, zcode.screen.supportedgraphics(0))
        if getflag(2, 7): # sound effects
            if zcode.screen.supportedgraphics(0) + zcode.screen.supportedgraphics(1) > 0:
                setflag(2, 7, 1)
            else:
                setflag(2, 7, 0)
        if getflag(2, 8): # menus
            setflag(2, 8, 0)
    
    # Flags 3 - If unset by the game, the terp should leave them like that. All unknown bits should be set to 0.
    if zversion() > 4:
        if getflag(3, 0): # transparency
            setflag(3, 0, zcode.screen.supportedgraphics(2))
        for a in range(1, 16): # set all the other bits to 0, because we don't know what they do
            setflag(3, a, 0)

    if zversion() > 3:
        # Interpreter number
        setterpnum(6)
        # Interpreter version
        setterpversion(ord('V'))
    
    updateSizes()

    if zversion() > 4:
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
    if zversion() > 4:
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
    if zversion() > 3:
        columns = int(zcode.screen.ioScreen.getWidth() // zcode.screen.getWindow(1).getFont().getWidth())
        # Screen height (lines)
        setscreenheightlines(int(zcode.screen.ioScreen.getHeight() // zcode.screen.getWindow(1).getFont().getHeight()))
        # Screen width (chars)
        setscreenwidthchars(columns)
        
    if zversion() > 4:
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


def release():
    return zcode.memory.getword(0x2)

def serial():
    x = zcode.memory.getarray(0x12,6)
    return ''.join([chr(b) for b in x])

def identifier():
    return str(release()) + "." + serial()

zmachine_version = None    

def zversion():
    global zmachine_version
    if zmachine_version == None:
        zmachine_version = zcode.memory.getbyte(0)
    return zmachine_version


def getflag(bitmap, bit): # bitmap is the set of flags to look in, such as flags 1, bit is the bit number to check, such as bit 1 for z3 status line type checking
    if bitmap == 1:
        flag = 1
        for a in range(bit):
            flag = flag * 2

        if zcode.memory.getbyte(1) & flag == flag:
            return 1
        else:
            return 0
    elif bitmap == 2:
        flag = 1
        for a in range(bit):
            flag = flag * 2
        if zcode.memory.getword(0x10) & flag == flag:
            return 1
        else:
            return 0
    elif bitmap == 3:
        if headerextsize() < 4:
            return 0
        else:
            flag = 1
            for a in range(bit):
                flag = flag * 2
            if zcode.memory.getword(headerextloc() + 4) & flag == flag:
                return 1
            else:
                return 0
        

def setflag(bitmap, bit, value): 
    # bitmap is the set of flags to look in, bit is the bit number to change, value is either 1 for on or 0 for off
    global flags1, flags2
    if bitmap == 1: 
        flag = 1
        for a in range(bit):
            flag = flag * 2
        if value:
            zcode.memory.setbyte(1, zcode.memory.getbyte(1) | flag)
        else:
            zcode.memory.setbyte(1, zcode.memory.getbyte(1) & ~flag)
    elif bitmap == 2:
        flag = 1      
        for a in range(bit):
            flag = flag * 2
        if value:
            zcode.memory.setword(0x10, zcode.memory.getword(0x10) | flag)
        else:
            zcode.memory.setword(0x10, zcode.memory.getword(0x10) & ~flag)
    elif bitmap == 3:
        if headerextsize() >= 4:
            flag = 1
            for a in range(bit):
                flag = flag * 2
            if value:
                zcode.memory.setword(headerextloc() + 8, zcode.memory.getword(headerextloc() + 8) | flag)
            else:
                zcode.memory.setword(headerextloc() + 8, zcode.memory.getword(headerextloc() + 8) & ~flag)

high_memory = None

def highmembase():
    global high_memory
    if not high_memory:
        high_memory = zcode.memory.getword(0x4)
    return high_memory

initial_PC = None

def initialPC(): # for non z6
    global initial_PC
    if not initial_PC:
        initial_PC = zcode.memory.getword(0x6)
    return initial_PC

main_routine = None

def mainroutine(): # for z6
    global main_routine
    if not main_routine:
        main_routine = zcode.memory.getword(0x6)
    return main_routine

dictionary_location = None

def dictionaryloc():
    global dictionary_location
    if not dictionary_location:
        dictionary_location = zcode.memory.getword(0x8)
    return dictionary_location

object_table = None

def objtableloc():
    global object_table
    if not object_table:
        object_table = zcode.memory.getword(0xA)
    return object_table

globals_location = None

def globalsloc():
    global globals_location
    if not globals_location:
        globals_location = zcode.memory.getword(0xC)
    return globals_location

static_memory = None

def statmembase():
    global static_memory
    if not static_memory:
        static_memory = zcode.memory.getword(0xE)
    return static_memory

abbreviations_table = None

def abbrevtableloc():
    global abbreviations_table
    if not abbreviations_table:
        abbreviations_table = zcode.memory.getword(0x18)
    return abbreviations_table

file_length = None

def filelen(): # in the header, this may be 0, in which case this routine should figure it out manually. But it doesn't.
    global file_length
    if not file_length:
        l = (zcode.memory.getbyte(0x1a) << 8) + zcode.memory.getbyte(0x1b)
        if l == 0:
            file_length = len(memory.data)
        elif zversion() < 4: # versions 1 to 3
            file_length = l * 2
        elif zversion() < 6: # versions 4 and 5
            file_length = l * 4
        else: # versions 6, 7 and 8
            file_length = l * 8
    return file_length

checksum = None

def getchecksum():
    global checksum
    if not checksum:
        checksum = zcode.memory.getword(0x1C)
    return checksum

def setterpnum(number):
    zcode.memory.setbyte(0x1E, number)

def setterpversion(number):
    zcode.memory.setbyte(0x1F, number)

def getterpnum():
    return zcode.memory.getbyte(0x1E)

def getterpversion(): # I doubt this will be needed
    return zcode.memory.getbyte(0x1F)

def getscreenheightlines():
    return zcode.memory.getbyte(0x20)

def getscreenwidthchars():
    return zcode.memory.getbyte(0x21)

def getscreenwidth(): # screen width in units
    return zcode.memory.getword(0x22)

def getscreenheight(): # screen height in units
    return zcode.memory.getword(0x24)

def getfontwidth():
    if zversion() == 6:
        return zcode.memory.getbyte(0x27)
    else:
        return zcode.memory.getbyte(0x26)

def getfontheight():
    if zversion() == 6:
        return zcode.memory.getbyte(0x26)
    else:
        return zcode.memory.getbyte(0x27)



def setscreenheightlines(lines):
    zcode.memory.setbyte(0x20, lines)

def setscreenwidthchars(chars):
    zcode.memory.setbyte(0x21, chars)

def setscreenwidth(units): # screen width in units
    zcode.memory.setword(0x22, units)

def setscreenheight(units): # screen height in units
    zcode.memory.setword(0x24, units)

def setfontwidth(units):
    if zversion() == 6:
        zcode.memory.setbyte(0x27, units)
    else:
        zcode.memory.setbyte(0x26, units)

def setfontheight(units):
    if zversion() == 6:
        zcode.memory.setbyte(0x26, units)
    else:
        zcode.memory.setbyte(0x27, units)
    
routines_offset = None
def routineoffset(): # z6 only
    global routines_offset
    if not routines_offset:
        routines_offset = zcode.memory.getword(0x28) * 8
    return routines_offset

strings_offset = None

def stringoffset(): # z6 only
    global strings_offset
    if not strings_offset:
        strings_offset = zcode.memory.getword(0x2A) * 8
    return strings_offset

def setdefbgcolour(colour):
    zcode.memory.setbyte(0x2c, colour)

def setdeffgcolour(colour):
    zcode.memory.setbyte(0x2D, colour)

def getdefbgcolour():
    return zcode.memory.getbyte(0x2C)

def getdeffgcolour():
    return zcode.memory.getbyte(0x2D)

terminating_characters = None

def termcharloc():
    global terminating_characters
    if terminating_characters == None:
        terminating_characters = zcode.memory.getword(0x2E)
    return terminating_characters

def settextwidth(len): # total width in units of text sent to output stream 3
    zcode.memory.setword(0x30, len)

def setstandardnum(n, m): # for standard 1.0, setstandardnum(1, 0) would be sent.
    zcode.memory.setbyte(0x32, n)
    zcode.memory.setbyte(0x33, m)

def getstandardnum():
    n = zcode.memory.getbyte(0x32)
    m = zcode.memory.getbyte(0x33)
    return (n,m)

alphabet_table = None

def alphatableloc():
    global alphabet_table
    if alphabet_table == None:
        alphabet_table = zcode.memory.getword(0x34)
    return alphabet_table

header_extension = None

def headerextloc():
    global header_extension
    if header_extension == None:
        header_extension = zcode.memory.getword(0x36)
    return header_extension


    
# header extension stuff 

header_extension_size = None

def headerextsize():
    global header_extension_size
    if header_extension_size == None:
        if headerextloc() == 0:
            header_extension_size = 0
        else:
            header_extension_size = zcode.memory.getword(headerextloc())    
    return header_extension_size

def setHeaderExtWord(word, value):  
    if headerextsize() < word:
        return 0
    zcode.memory.setword(headerextloc() + (word*2), value)

def getHeaderExtWord(word):
    if headerextsize() < word:
        return 0
    else:
        return zcode.memory.getword(headerextloc() + (word*2))
    

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
