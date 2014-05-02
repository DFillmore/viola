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

import string

import zcode

def setup(): # set all the relevant bits and bytes and words in the header
    # Flags 1
    if zversion() == 3:
        setflag(1, 4, 0) # status line is available
        setflag(1, 5, 1) # screen splitting is available
        setflag(1, 6, 0) # The default font is not fixed-pitch
    elif zversion() < 9:
        setflag(1, 2, gestalt(4, 2)) # Boldface
        setflag(1, 3, gestalt(4, 4)) # Italic
        setflag(1, 4, gestalt(4, 8)) # Fixed-pitch style
        setflag(1, 7, gestalt(5)) # Timed input
        if zversion() > 4:
            setflag(1, 0, gestalt(2, 0)) # Colours
        if zversion() == 6:
            setflag(1, 1, gestalt(2, 3)) # Picture displaying
        if gestalt(3, 0) + gestalt(3, 1) > 0: # if any effect or music channels are available, sound effects are available
            setflag(1, 5, 1) # sound effects
        else:
            setflag(1, 5, 0)


    # Flags 2 - If unset by the game, the terp should leave them like that.
    if zversion() > 4:
        if getflag(2, 3): # pictures
            setflag(2, 3, gestalt(2, 3)) 
        if getflag(2, 4): # undo
            if gestalt(7):
                setflag(2, 4, 1)
            else:
                setflag(2, 4, 0)
        if getflag(2, 5): # mouse
            setflag(2, 5, gestalt(6, 2))
        if getflag(2, 6): # colours
            setflag(2, 6, gestalt(2, 0))
        if getflag(2, 7): # sound effects
            if gestalt(3, 0) + gestalt(3, 1) > 0:
                setflag(2, 7, 1)
            else:
                setflag(2, 7, 0)
        if getflag(2, 8): # menus
            setflag(2, 8, gestalt(8))
    
    # Flags 3 - If unset by the game, the terp should leave them like that. All unknown bits should be set to 0.
    if zversion() > 4:
        if getflag(3, 0): # transparency
            setflag(3, 0, gestalt(2, 2))
        if getflag(3, 1): # font resizing
            setflag(3, 1, gestalt(11))
        for a in range(2, 16): # set all the other bits to 0, because we don't know what they do
            setflag(3, a, 0)


    

    if zversion() > 3:
        columns = int(zcode.screen.ioScreen.getWidth() // zcode.screen.getWindow(1).font.getWidth())
        # Interpreter number
        setterpnum(6)
        # Interpreter version
        setterpversion(ord('V'))
        #io.frame.screen.setstyle(8)
        # Screen height (lines)
        setscreenheightlines(int(zcode.screen.ioScreen.getHeight() // zcode.screen.getWindow(1).font.getHeight()))
        # Screen width (chars)

        setscreenwidthchars(columns)
        
    if zversion() > 4:
        # Screen width (units)
        if zversion() == 6:
            setscreenwidth(zcode.screen.ioScreen.getWidth())
        else:
            setscreenwidth(columns)
        # Screen height (units)
        if zversion() == 6:
            setscreenheight(zcode.screen.ioScreen.getHeight())
        else:
            setscreenheight(int(zcode.screen.ioScreen.getHeight() // zcode.screen.getWindow(1).font.getHeight()))
        # Font width (units, obviously)
        if zversion() == 6:
            setfontwidth(zcode.screen.currentWindow.font.getWidth())
        else:
            setfontwidth(1)
        # Font height
        if zversion() == 6:
            setfontheight(zcode.screen.currentWindow.font.getHeight())
        else:
            setfontheight(1)
        # Default foreground colour
        setdeffgcolour(2)
        # Default background colour
        setdefbgcolour(9)
        settruedefaultforeground(zcode.screen.spectrum[2])
        settruedefaultbackground(zcode.screen.spectrum[9])
    # Z-machine Standard number
    # not bug free enough to fully support even 1.0
    # although even 1.2 is partially implemented
    setstandardnum(0, 0) 


def release():
    return zcode.memory.getword(0x2)

def serial():
    x = zcode.memory.getarray(0x12,6)
    return ''.join([chr(b) for b in x])

def identifier():
    return str(release()) + "." + serial()

    

def zversion():
    return zcode.memory.getbyte(0)


def getflag(bitmap, bit): # bitmap is the set of flags to look in, such as flags 1, bit is the bit number to check, such as bit 1 for z3 status line type checking
    if bitmap == 1:
        if zversion() > 8:
            return 0 # z9 has no flags 1

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
        if zversion() > 8: # z9 has no flags 1
            return False
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
                zcode.memory.setword(headerextloc() + 8, zcode.memory.getword(headerextloc() + 8 | flag))
            else:
                zcode.memory.setword(headerextloc() + 8, zcode.memory.getword(headerextloc() + 8 & ~flag))

def highmembase():
    return zcode.memory.getword(0x4)

def initialPC(): # for non z6
    return zcode.memory.getword(0x6)

def mainroutine(): # for z6
    return zcode.memory.getword(0x6)

def dictionaryloc():
    return zcode.memory.getword(0x8)

def objtableloc():
    return zcode.memory.getword(0xA)

def globalsloc():
    return zcode.memory.getword(0xC)

def statmembase():
    return zcode.memory.getword(0xE)

def abbrevtableloc():
    return zcode.memory.getword(0x18)

def filelen(): # in the header, this may be 0, in which case this routine should figure it out manually. But it doesn't.
    l = (zcode.memory.getbyte(0x1a) << 8) + zcode.memory.getbyte(0x1b)

    if zversion() < 4: # versions 1 to 3
        return l * 2
    elif zversion() < 6: # versions 4 and 5
        return l * 4
    else: # versions 6, 7 and 8
        return l * 8

def getchecksum():
    return zcode.memory.getword(0x1C)

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
    
def routineoffset(): # z6 only
    return zcode.memory.getword(0x28) * 8

def stringoffset(): # z6 only
    return zcode.memory.getword(0x2A) * 8

def setdefbgcolour(colour):
    zcode.memory.setbyte(0x2c, colour)

def setdeffgcolour(colour):
    zcode.memory.setbyte(0x2D, colour)

def getdefbgcolour():
    return zcode.memory.getbyte(0x2C)

def getdeffgcolour():
    return zcode.memory.getbyte(0x2D)

def termcharloc():
    return zcode.memory.getword(0x2E)

def settextwidth(len): # total width in units of text sent to output stream 3
    zcode.memory.setword(0x30, len)

def setstandardnum(n, m): # for standard 1.0, setstandardnum(1, 0) would be sent.
    zcode.memory.setbyte(0x32, n)
    zcode.memory.setbyte(0x33, m)

def getstandardnum():
    n = zcode.memory.getbyte(0x32)
    m = zcode.memory.getbyte(0x33)
    return (n,m)

def alphatableloc():
    return zcode.memory.getword(0x34)

def headerextloc():
    return zcode.memory.getword(0x36)


    
# header extension stuff 

def headerextsize():
    if headerextloc() == 0:
        return 0
    words = zcode.memory.getword(headerextloc())
    return words

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


def unicodetableloc():
    return getHeaderExtWord(3)


    

# Standard 1.1 stuff below

def settruedefaultforeground(colour):
    setHeaderExtWord(5, colour)

def settruedefaultbackground(colour):
    setHeaderExtWord(6, colour)

def gettruedefaultforeground():
    return getHeaderExtWord(5)

def gettruedefaultbackground():
    return getHeaderExtWord(6)

# Standard 1.2 stuff

viola_version = 8 # version 0.8

def gestalt(id, arg1=0, arg2=0, arg3=0):
    if id == 0: # interpreter version
        return viola_version
    if id == 2: # graphics capablities 
        return zcode.screen.supportedgraphics(arg1)
    if id == 3: # sound capablities
        return zcode.sounds.availablechannels(arg1)
    if id == 4: # text styles
        return zcode.screen.supportedstyles(arg1)
    if id == 5: # timed input
        return 1 # should really query the io code to see if we support this
    if id == 6: # supported input devices
        if arg1 == 1: # keyboard support
            return 1
        if arg2 == 2: # mouse support
            return 1
        return 0 # no other supported devices
    if id == 7: # undo support
        return -1 # supports multiple undo, but we have no way to tell how many more undo slots are available
    if id == 8: # menu support (as in the interpreter application's menu bar)
        return 0
    if id == 9: # output streams
        if arg2 == 0: # is the stream supported?
            try:
                if zcode.output.streams[arg1]:
                    return 1
                return 0
            except:
                return 0
        if arg2 == 1: # number of streams of the type given that are currently open
            return zcode.output.numopenstreams(arg1)
        if arg1 == 5 and arg2 == 2: # special case for output stream 5. should look at an area in memory, read an identifier, and return 1 if supported
            return zcode.output.checkident(arg3) # currently claiming not to support any identifiers
    if id == 10: # input streams
        if arg1 < 2: 
            return 1
        return 0
    if id == 11: # font size
        return 0 # we don't yet support the font size opcode
    if id == 12: # unicode strings (using the unicode escape character)
        return 1 # we support unicode string. In theory. In practice, it's kinda broken.

     
#def setFontMetric(value):
    