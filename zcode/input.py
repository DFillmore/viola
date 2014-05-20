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
import zio.pygame as io
import zcode

stream = 0
file_commands = []
instring = []

command_history = []
chplace = -1


def setup():
    global ioInput
    global mouse
    mouse = mouseTracker()
    ioInput = io.input(zcode.screen.ioScreen)

def setStream(number, filename=0):
    global stream
    global filecommands
    stream = number
    if number == 0 and streamfile != 0:
        streamfile = 0
    elif number == 1:
        streamfile = readFile(-1, filename="COMMANDS.REC", prompt=True).decode('utf-8')
        if streamfile:
            filecommands = streamfile.split('\n')
            while filecommands[-1].strip() == '':
                filecommands.pop()
            filecommands.reverse()
            stream = 1

def getTerminatingCharacters():
    if zcode.header.zversion() < 5:
        return []
    location = zcode.header.termcharloc()
    chars = []
    x = 1
    while x != 0:
        x = zcode.memory.getbyte(location)
        location += 1
        chars.append(x)
    chars.pop()
    if chars.count(255) != 0: # if 255 is one of the terminating characters, make every 'function character' terminating
        chars = []
        for a in range(129,155):
            chars.append(a)
        for a in range(252,255):
            chars.append(a)
    return chars
    
class mouseTracker:
    xpos = 1
    ypos = 1
    buttons = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]


def convertInputToZSCII(char):
    if char == 273:
        return 129
    if char == 274:
        return 130
    if char == 275:
        return 132
    if char == 276:
        return 131
    if char >= 282 and char <= 293:
        char -= 149
        return char
    if char >= 256 and char <= 265:
        char -= 111
        return char
    if char in zcode.text.unitable:
        char = zcode.text.reverseunitable[char]
        return char
    return None


def getInput(display=True, ignore=False, chistory=True):
    global mouse
    global stream
    global instring
    global chplace
    termchar = False
    zcode.game.interrupt_call()
    if stream == 0:
        input = ioInput.getinput()
        if ignore:
            if isinstance(input, io.keypress):
                return input.value
            return None
        zsciivalue = None

        if isinstance(input, io.keypress):
            if chistory and input.value == 273: # pressed up key
                if chplace < len(command_history) -1:
                    chplace += 1

                    inp = [chr(a) for a in zcode.input.instring]
                    inp = ''.join(inp)
                    w = zcode.screen.currentWindow.getStringLength(inp)
                    h = zcode.screen.currentWindow.getStringHeight(inp)
                    x = zcode.screen.currentWindow.getCursor()[0] - w
                    y = zcode.screen.currentWindow.getCursor()[1]
                    zcode.screen.currentWindow.eraseArea(x-1,y-1,w,h)
                    zcode.screen.currentWindow.setCursor(x,y)

                    instring = command_history[chplace]
                    for c in instring:
                        zcode.output.streams[1].write(chr(c))
                    zcode.screen.currentWindow.flushTextBuffer()
                return None
            if chistory and input.value == 274: # pressed down key
                if chplace >= 0:
                    if chplace >= 0:
                        chplace -= 1
                        newstring = command_history[chplace]
                    if chplace == -1:
                        newstring = []

                    inp = [chr(a) for a in zcode.input.instring]
                    inp = ''.join(inp)
                    w = zcode.screen.currentWindow.getStringLength(inp)
                    h = zcode.screen.currentWindow.getStringHeight(inp)
                    x = zcode.screen.currentWindow.getCursor()[0] - w
                    y = zcode.screen.currentWindow.getCursor()[1]
                    zcode.screen.currentWindow.eraseArea(x-1,y-1,w,h)
                    zcode.screen.currentWindow.setCursor(x,y)

                    instring = newstring
                    for c in instring:
                        zcode.output.streams[1].write(chr(c))
                    zcode.screen.currentWindow.flushTextBuffer()

                return None
                    
            if len(input.character) == 1:
                zsciivalue = ord(input.character)
            else:
                zsciivalue = input.value
            if zsciivalue > 126:
                zsciivalue = convertInputToZSCII(zsciivalue)

        if isinstance(input, io.mousedown):
            if input.button != None:
                mouse.buttons[input.button] = 1
                zsciivalue = 254 # mouse down == single click
                zcode.header.setmousex(mouse.xpos)
                zcode.header.setmousey(mouse.ypos)

        if isinstance(input, io.mouseup):
            if input.button != None:
                mouse.buttons[input.button] = 0


        if isinstance(input, io.mousemove):
            mouse.xpos = zcode.screen.pix2units(input.xpos + 1, horizontal=True, coord=True)
            mouse.ypos = zcode.screen.pix2units(input.ypos + 1, horizontal=False, coord=True)

        if isinstance(input, io.keypress):
            if zsciivalue in zcode.text.inputvalues:
                if zsciivalue not in getTerminatingCharacters() and display and zsciivalue in zcode.text.outputvalues:
                    if zsciivalue == 13:
                        zcode.screen.currentWindow.hideCursor()

                    zcode.output.streams[1].write(chr(zsciivalue))
    
                    zcode.screen.currentWindow.flushTextBuffer()
                    if zcode.header.zversion != 6:
                        zcode.output.streams[2].write(chr(zsciivalue))

            else:
                return None
        return zsciivalue
    else:
        currentcommand = filecommands.pop()
        if len(currentcommand) > 0:
            c = currentcommand[0]
            if len(c) == 1:
                zsciivalue = ord(c)
            else:
                zsciivalue = convertInputToZSCII(c) 
            currentcommand = currentcommand[1:]
            filecommands.append(currentcommand)
            
            if zsciivalue not in getTerminatingCharacters() and display:
                 zcode.output.streams[1].write(chr(zsciivalue))
            return zsciivalue
        else:
            if len(filecommands) == 0:
                stream = 0
            zcode.output.streams[1].write('\r')
            return 13

def readFile(length, filename=None, prompt=False, seek=0): 
    f = io.openfile(zcode.screen.currentWindow, 'r', filename, prompt)
    if f == None:
        return False
    f.seek(seek)
    if length == -1:
        data = f.read()
    else:
        data = f.read(length)
    f.close()
    return data

