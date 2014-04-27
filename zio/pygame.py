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
os.environ['PYGAME_FREETYPE'] = '1'


import pygame
import io
import sys
#import zcode

from pygame.locals import *
pygame.init()

tfont = None

TIMEREVENT = pygame.USEREVENT
SOUNDEVENT = pygame.USEREVENT + 1

mousebuttonmapping = {1:0,2:2,3:1}

class ZTimer:
    routine = 0

class image():
    data = None
    def __init__(self, data, filename=False):
        if type(data) == bytes:
            if filename:
                self.picture = pygame.image.load(data)
            else:
                self.picture = pygame.image.load(io.BytesIO(data))
            
        else: # assume pygame surface
            self.picture = data
        try:
            self.palette = self.picture.get_palette()
        except:
            self.palette = None

    def getPalette(self):
        return self.palette

    def setPalette(self, palette):
        self.palette = palette

    def draw(self, window, x, y, part=None): # part is tuple in form (left, top, width, height)
        picture = self.picture
        if self.palette:
            picture.set_palette(self.palette)
        picture = picture.convert_alpha(window.screen.screen)
        if part:
            r = pygame.Rect(part[0], part[1], part[2], part[3])
            window.screen.screen.blit(picture, (x,y), r)
        else:
            window.screen.screen.blit(picture, (x,y))
        area = pygame.Rect(window.getPosition(), window.getSize())
        window.screen.updates.append(area)

    def scale(self, width, height):
        newpic = pygame.transform.scale(self.picture, (int(width), int(height)))
        newImage = image(newpic)
        return newImage

    def getWidth(self):
        return self.picture.get_width()

    def getHeight(self):
        return self.picture.get_height()

class soundChannel:
    pass

class effectsChannel(soundChannel):
    pass

class musicChannel(soundChannel):
    pass


class font:
    #def __str__(self):
    #    return 'Font: ' + str(self.name)

    def __init__(self, fontfile, boldfile=None, italicfile=None, bolditalicfile=None):
        self.size = self.defaultSize()
        self.fontfile = fontfile
        self.boldfile = boldfile
        self.italicfile = italicfile
        self.bolditalicfile = bolditalicfile
        self.usefile = self.fontfile

    
    bold = False
    italic = False
    usefile = None


    def getUseFile(self):
        if self.italic and self.bold:
            return self.bolditalicfile
        elif self.italic:
            return self.italicfile
        elif self.bold:
            return self.boldfile
        else:
            return self.fontfile

       
    def setBold(self, value):
        if value:
            self.bold = True
        else:
            self.bold = False
        self.usefile = self.getUseFile()

    def setItalic(self, value):
        if value:
            self.italic = True
        else:
            self.italic = False
        self.usefile = self.getUseFile()

    def getWidth(self):
        self.width = self.fontData().size('0')[0]
        return self.width
    
    def getHeight(self):
        self.height = self.fontData().size('0')[1]
        return self.height

    def getStringLength(self, text):
        return self.fontData().size(text)[0]

    def getAscent(self):
        return self.fontData().get_ascent()

    def getDescent(self):
        return abs(self.fontData().get_descent())

    def defaultSize(self):
        return 14

    def increaseSize(self, amount=1):
        self.size += amount
        return 1

    def decreaseSize(self, amount=1):
        if self.size == 1:
            return 0
        self.size -= amount
        return 1

    def resetSize(self):
        self.size = self.defaultSize()

    def render(self, text, antialias, colour, background):
        f = self.fontData()
        return f.render(text, antialias, colour, background)

    def fontData(self):
        fon = pygame.font.Font(self.usefile, self.size)
        return fon

class window:
    y_coord = 0
    x_coord = 0
    y_size = 0
    x_size = 0
    y_cursor = 0
    x_cursor = 0
    left_margin = 0
    right_margin = 0
    text_style = 0
    foreground_colour = 0
    background_colour = 0
    font = None
    wrapping = 0
    scrolling = 0
    buffering = 0
    align_text = 0
    line_count = 0
    true_foreground_colour = 0
    true_background_colour = 0
    font_metrics = 0

    background = 0
    foreground = 0
    fontstyles = 0

    def __init__(self, screen, font):
        self.screen = screen
        self.setFont(font)

    def setFont(self, f):
        self.font = f

    def getFont(self):
        return self.font
    
    def setColours(self, foreground, background):
        self.foreground_colour = foreground
        self.background_colour = background

    def getColours(self):
        return (self.foreground_colour, self.background_colour)

    def setPosition(self, x, y):
        self.x_coord = x
        self.y_coord = y

    def getPosition(self):
        return (self.x_coord, self.y_coord)

    def setSize(self, width, height):
        self.x_size = width
        self.y_size = height

    def getSize(self):
        return (self.x_size, self.y_size)

    def setCursor(self, x, y):
        self.x_cursor = x
        self.y_cursor = y

    def getCursor(self):
        return (self.x_cursor, self.y_cursor)

    def getPixelColour(self, x, y):
        return self.screen.getpixel(x,y)

    def preErase(self):
        pass
    
    def postErase(self):
        pass

    def erase(self):
        area = pygame.Rect(self.getPosition(), self.getSize())
        self.screen.screen.fill(self.getColours()[1], area)
        self.line_count = 0
        self.x_cursor = 1
        self.y_cursor = 1


    def preNewline():
        pass

    def postNewline():
        pass

    def scroll(self, amount, dir=0):
        if dir == 0: # scroll area up
            xpos, ypos = self.getPosition()
            sourcex, sourcey = self.getPosition()
            sourcey += amount
            width, height = self.getSize()
            height -= amount
            sourcerect = pygame.Rect(sourcex, sourcey, width, height)
            destrect = pygame.Rect(xpos, ypos,width, height)
            self.screen.screen.set_clip(destrect)
            self.screen.screen.blit(self.screen.screen, self.getPosition(), sourcerect)
            self.screen.screen.set_clip()
            destrect = pygame.Rect(sourcex, ypos+height, width, amount)
            pygame.draw.rect(self.screen.screen, self.getColours()[1], destrect)
        else: # scroll area down
            xpos, ypos = self.getPosition()
            sourcex, sourcey = self.getPosition()
            width, height = self.getSize()
            sourcerect = pygame.Rect(sourcex, sourcey, width, height-amount)
            destrect = pygame.Rect(xpos, ypos+amount, width, height-amount)
            self.screen.screen.set_clip(destrect)
            self.screen.screen.blit(self.screen.screen, self.getPosition(), sourcerect)
            self.screen.screen.set_clip()
            destrect = pygame.Rect(xpos, ypos, width, amount)
            pygame.draw.rect(self.screen.screen, self.getColours()[1], destrect)
        area = pygame.Rect(xpos, ypos, width, height)
        self.screen.updates.append(area)

    def flushTextBuffer(self):
        pass


    def printText(self, text):
        print(text)
        self.buffertext(text) # assume that all text gets buffered for now
        if text.find('\r') != -1: # and io.pygame.timer.IsRunning() == 0:
            self.flushTextBuffer() # flush the text buffer if a new line has been printed
     

    def drawText(self, text):
        fg, bg = self.getColours()
        xpos, ypos = self.getPosition()
        xcursor, ycursor = self.getCursor()
        width, height = self.getSize()
        textsurface = self.font.render(text, 1, fg, bg)
        if text != '':
            self.screen.screen.blit(textsurface, (xpos + xcursor, ypos + ycursor))
        area = pygame.Rect(xpos, ypos, width, height)
        self.screen.updates.append(area)

    def getStringLength(self, text):
        return self.font.getStringLength(text)

    def getStringHeight(self, text):
        return self.font.getHeight()

class screen:
    updates = []
    def __init__(self, width, height):

        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self.screen.fill(0xFFFFFF)
        self.width = width
        self.height = height
        pygame.display.update()

    def getWidth(self):
        return self.width
    
    def getHeight(self):
        return self.height

    def getpixel(self, x,y):
        return self.screen.get_at((x, y))

    def erase(self, colour, area=None):
        if area:
            area = pygame.Rect((area))
        else:
            area = pygame.Rect((0, 0), (self.getWidth(), self.getHeight()))
        self.screen.fill(colour, area)
        self.updates.append(area)




class keypress:
    def __init__(self, value, character):
        self.value = value
        self.character = character

    character = None
    value = None

class mousemove:
    def __init__(self, event):
        self.xpos = event.pos[0]
        self.ypos = event.pos[1]
    xpos = 0
    ypos = 0


class mousedown:
    def __init__(self, event):
        self.button = mousebuttonmapping[event.button]
    button = None

class mouseup:
    def __init__(self, event):
        self.button = mousebuttonmapping[event.button]
    button = None

#class timerevent:
    

class input:
    def __init__(self, screen):
        self.screen = screen

    def getinput(self):
        pygame.display.update(self.screen.updates)
        self.screen.updates = []
        
        event = pygame.event.wait()
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYDOWN:
            return keypress(event.key, event.unicode)
#        if event.type == VIDEORESIZE:
#            resize()
        if event.type == MOUSEBUTTONDOWN:
            return mousedown(event)
        if event.type == MOUSEBUTTONUP:
            return mouseup(event)
        if event.type == MOUSEMOTION:
            return mousemove(event)
        if event.type == TIMEREVENT:
            try:
                timerroutine()
            except:
                pass
        if event.type == SOUNDEVENT:
            SOUNDEVENTHANDLER()


        
def setup():
    global zscreen
    global currentfont
    global inputtext
    global timerrunning
    timerrunning = False
    inputtext = []
    pygame.key.set_repeat(100, 100)

#def resize():
#    global screenwidth
#    global screenheight
#    global zscreen
#    size = zscreen.get_rect()
#    oldwidth = screenwidth
#    oldheight = screenheight
#    screenwidth = zscreen.get_width()
#    screenheight = zscreen.get_height()

#    backup = pygame.Surface((oldwidth, oldheight))

#    if header.zversion() == 6:
#        bg = screen.truetofull(screen.spectrum[defbgcolour()])
#    else:
#        bg = background
#        if bg == -4:
#            bg = screen.truetofull(screen.spectrum[defbgcolour()])
#    if screeenwidth < oldwidth:
#        oldwidth = screenwidth
#    if screenheight < oldheight:
#            oldheight = screenheight
#    screen.resize()

#    backup.blit(zscreen, (0,0))
#    zscreen.fill(bg)
#    zscreen.set_clip(pygame.Rect(0,0,oldwidth,oldheigh))
#    zscreen.blit(backup, (0,0))
#    zscreen.set_clip()
#    pygame.display.update()


def openfile(filename, prompt, mode):
    # if filename == None, prompt for a filename
    # returns a file object to be read/written
    mode = mode + 'b'
    if filename == None: # should prompt for filename
        return open("TESTFILE.AUX", mode)
    elif prompt: # prompt for filename, but supply suggestion
        return open("TESTFILE.AUX", mode)
    else: # just open the filename with no prompt
        return open(filename, mode) 






def opentranscript(filename=None):
    pass

        
def makemenu(self, title, items, number): # title is a string, items is a list of strings, number is the id number
    return 0
#    if number < 3 or number > 10:
#        return 0
#    if menus[number] != 0:
#        self.destroymenu(number)
#    menus[number] = wx.Menu()
#    for a in xrange(len(items)):
#        num = number * 100 + a
#        menus[number].Append(num, items[a])
#
#        menubar.Insert(number-2, menus[number], title)
#        return 1

def destroymenu(self, number):
    return 0
#    if number < 3 or number > 10:
#        return 0
#    else:
#        if menus[number] == 0:
#            return 0
#        menus[number] = 0
#        menubar.Remove(number - 2)
#        return 1


                


 
    
def nextinput():
    pass
   
def previnput():
    pass

def dobackspace():
    global xcursor, ycursor, termchar
    if routines.input == 2:
        termchar = 8
        routines.input = -2
        routines.execloop()
    elif len(inputtext) > 0:
        erasecursor()
        letter = inputtext.pop()
        width = getstringlength(letter)
        height = getstringheight(letter)
        movecursor(width * -1, 0) # move the cursor back one char
        area = pygame.Rect(io2z(xcursor), io2z(ycursor), width, height)
        erase(io2z(xcursor), io2z(ycursor), width, height)
        screen.currentwin.x_cursor -= width
        showcursor()
    try:
        pygame.display.update(area)
    except:
        pass


def doenter():
    global intext, inputtext, termchar
    if routines.input == 2:
        termchar = 13
        routines.input = -2
        routines.execloop()
    else:
        intext = string.join(inputtext, '')
        #self.inputlist.append(inputtext)
        inputtext = []
        pygame.display.update()
        if output.stream1 == 1:
            output.closestream(1)
            x = 1
        output.printtext(intext)
        if x == 1:
            output.openstream(1)
        erasecursor()
        #screen.currentwin.newline()
        showcursor()
        termchar = 13
        routines.input = -1
        routines.execloop()

  


        



timerroutine = None
        
def starttimer(time, r=None):
    global timerrunning 
    global timerroutine
    timerroutine = r
    timerrunning = True
    time *= 100
    pygame.time.set_timer(TIMEREVENT, time)
    
def stoptimer():
    global timerrunning
    timerrunning = False
    pygame.time.set_timer(TIMEREVENT, 0)







class musicobject():
    def __init__(self, data):
        self.data = data
    def play(self, loops=0):
        pygame.mixer.music.load(self.data)
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(loops=loops)
    def set_volume(self, volume):
        self.volume = volume


def sound(data, type):
    if type == 0:
        return pygame.mixer.Sound(io.BytesIO(data))
    else:
        return musicobject(io.BytesIO(data))
        
SOUNDEVENTHANDLER = None

def maxeffectschannels():
    return pygame.mixer.get_num_channels()

def maxmusicchannels():
    return 1

class soundChannel():
    sound = None
    routine = None
    type = None
    def __init__(self, id):
        self.id = id

    def setup(self, routine): # sets up to start timer events to check if the channel is playing
        global SOUNDEVENTHANDLER
        if self.type == 0:
            self.channelobj.set_endevent(SOUNDEVENT)
        elif self.type == 1:
            pygame.mixer.music.set_endevent(SOUNDEVENT)
        SOUNDEVENTHANDLER = routine
        if self.type == 0:
            self.clock = pygame.time.Clock()
            self.clock.tick()


    def cleanup(self):
        if self.type == 0:
            self.channelobj.set_endevent()
        elif self.type == 1:
            pygame.mixer.music.set_endevent()

    def getpos(self):
        if self.type == 1:
            return pygame.mixer.music.get_pos()
        elif self.type == 0:
            self.clock.tick()
            return self.clock.get_time()

    def Notify(self):
        pass
