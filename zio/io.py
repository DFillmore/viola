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
os.environ['PYGAME_FREETYPE'] = '1'


import pygame
import pygame.ftfont
import io
import sys
import inspect
import types
import numpy
import fonts.font as fonts

from pygame.locals import *
pygame.init()


TIMEREVENT = pygame.USEREVENT
SOUNDEVENT = pygame.USEREVENT + 1

GAMEDIRECTORY = ''

mousebuttonmapping = {1:0,2:2,3:1}

def getBaseDir():
   if getattr(sys,"frozen",False):
       # If this is running in the context of a frozen (executable) file, 
       # we return the path of the main application executable
       return os.path.dirname(os.path.abspath(sys.executable))
   else:
       # If we are running in script or debug mode, we need 
       # to inspect the currently executing frame. This enable us to always
       # derive the directory of main.py no matter from where this function
       # is being called
       thisdir = os.path.dirname(inspect.getfile(inspect.currentframe()))
       return os.path.abspath(os.path.join(thisdir, os.pardir))

def findfile(filename, gamefile=False):
    global GAMEDIRECTORY
    paths = [os.curdir]
    paths.extend(os.path.expandvars("$INFOCOM_PATH").split(":"))
    for a in paths:
        x = os.path.isfile(os.path.join(a, filename))
        if x == 1:
            f = os.path.join(a, filename)
            if gamefile:
                GAMEDIRECTORY = os.path.dirname(f)
            return f
    return False

def setIcon(icon):
    pygame.display.set_icon(icon)

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
        # x and y are relative to the top left of the screen, not the window
        picture = self.picture
        if self.palette:
            picture.set_palette(self.palette)
        picture = picture.convert_alpha(window.screen.screen)
        if part:
            r = pygame.Rect(part[0], part[1], part[2], part[3])
            window.screen.screen.blit(picture, (x-1,y-1), r)
        else:
            window.screen.screen.blit(picture, (x-1,y-1))
        area = pygame.Rect((window.x_coord - 1, window.y_coord - 1), window.getSize())
        window.screen.updates.append(area)

    def scale(self, width, height):
        newpic = pygame.transform.scale(self.picture, (int(width), int(height)))
        newImage = image(newpic)
        return newImage

    def getWidth(self):
        return self.picture.get_width()

    def getHeight(self):
        return self.picture.get_height()


class font:
    #def __str__(self):
    #    return 'Font: ' + str(self.name)

    def __init__(self, fontfile, boldfile=None, italicfile=None, bolditalicfile=None, fixedfile=None, boldfixedfile=None, italicfixedfile=None, bolditalicfixedfile=None):
        self.size = self.defaultSize()
        self.fontfile = fontfile
        self.boldfile = boldfile
        self.italicfile = italicfile
        self.bolditalicfile = bolditalicfile
        self.fixedfile =fixedfile
        self.boldfixedfile = boldfixedfile
        self.italicfixedfile = italicfixedfile
        self.bolditalicfixedfile = bolditalicfixedfile
        self.usefile = self.fontfile
        codePointsRoman = fonts.getCodes(fontfile)
        codePointsBold = fonts.getCodes(boldfile)
        codePointsItalic = fonts.getCodes(italicfile)
        codePointsBoldItalic = fonts.getCodes(bolditalicfile)
        codePointsFixed = fonts.getCodes(fixedfile)
        codePointsBoldFixed = fonts.getCodes(boldfixedfile)
        codePointsItalicFixed = fonts.getCodes(italicfixedfile)
        codePointsBoldItalicFixed = fonts.getCodes(bolditalicfixedfile)
        self.codePoints = list(set(codePointsRoman).intersection(*[codePointsBold, codePointsItalic,codePointsBoldItalic,codePointsFixed,codePointsBoldFixed,codePointsItalicFixed,codePointsBoldItalicFixed]))


    
    bold = False
    italic = False
    usefile = None

    reversevideo = False
    fixedstyle = False

    def getUseFile(self):
        if self.italic and self.bold and self.fixedstyle:
            return self.bolditalicfixedfile
        elif self.italic and self.fixedstyle:
            return self.italicfixedfile
        elif self.bold and self.fixedstyle:
            return self.boldfixedfile
        elif self.fixedstyle:
            return self.fixedfile
        elif self.italic and self.bold:
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

    def setReverse(self, value):
        if value:
            self.reversevideo = True
        else:
            self.reversevideo = False

    def setFixed(self, value):
        if value:
            self.fixedstyle = True
        else:
            self.fixedstyle = False
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

    def checkChar(self, charnum):
        if charnum in self.codePoints:
            return True
        return False

    def defaultSize(self):
        return 16

    def render(self, text, antialias, colour, background):
        unavailable = list(numpy.setdiff1d(self.codePoints,list(map(ord, text))))
        for elem in unavailable:
            # Check if string is in the main string
            if chr(elem) in text:
                # Replace the string
                text = text.replace(elem, "?")


        f = self.fontData()
        if self.reversevideo:
            return f.render(text, antialias, background, colour)
        else:
            if background[3] == 0:
                return f.render(text, colour)
            return f.render(text, antialias, colour, background)

    def fontData(self):
        fon = pygame.ftfont.Font(self.usefile, self.size)
        return fon

font1 = font(getBaseDir() + "//fonts//FreeFont//FreeSerif.ttf",
             boldfile=getBaseDir() + "//fonts//FreeFont//FreeSerifBold.ttf",
             italicfile=getBaseDir() + "//fonts//FreeFont//FreeSerifItalic.ttf",
             bolditalicfile=getBaseDir() + "//fonts//FreeFont//FreeSerifBoldItalic.ttf",
             fixedfile=getBaseDir() + "//fonts//FreeFont//FreeMono.ttf", 
             boldfixedfile=getBaseDir() + "//fonts//FreeFont//FreeMonoBold.ttf", 
             italicfixedfile=getBaseDir() + "//fonts//FreeFont//FreeMonoOblique.ttf",
             bolditalicfixedfile=getBaseDir() + "//fonts//FreeFont//FreeMonoBoldOblique.ttf",
            )

#font1emoji = font(getBaseDir() + "//fonts//OpenSansEmoji//OpenSansEmoji.ttf",
#             boldfile=getBaseDir() + "//fonts//OpenSansEmoji//OpenSansEmoji.ttf",
#             italicfile=getBaseDir() + "//fonts//OpenSansEmoji//OpenSansEmoji.ttf",
#             bolditalicfile=getBaseDir() + "//fonts//OpenSansEmoji//OpenSansEmoji.ttf",
#             fixedfile=getBaseDir() + "//fonts//OpenSansEmoji//OpenSansEmoji.ttf", 
#             boldfixedfile=getBaseDir() + "//fonts//OpenSansEmoji//OpenSansEmoji.ttf", 
#             italicfixedfile=getBaseDir() + "//fonts//OpenSansEmoji//OpenSansEmoji.ttf",
#             bolditalicfixedfile=getBaseDir() + "//fonts//OpenSansEmoji//OpenSansEmoji.ttf",
#            )

font2 = None

#font3 = font(getBaseDir() + "//fonts//bzork.ttf", 
#             boldfile=getBaseDir() + "//fonts//bzork.ttf", 
#             italicfile=getBaseDir() + "//fonts//bzork.ttf", 
#             bolditalicfile=getBaseDir() + "//fonts//bzork.ttf", 
#             fixedfile=getBaseDir() + "//fonts//bzork.ttf", 
#             boldfixedfile=getBaseDir() + "//fonts//bzork.ttf", 
#             italicfixedfile=getBaseDir() + "//fonts//bzork.ttf", 
#             bolditalicfixedfile=getBaseDir() + "//fonts//bzork.ttf", 
#            )
font3 = None

font4 = font(getBaseDir() + "//fonts//FreeFont//FreeMono.ttf", 
             boldfile=getBaseDir() + "//fonts//FreeFont//FreeMonoBold.ttf", 
             italicfile=getBaseDir() + "//fonts//FreeFont//FreeMonoOblique.ttf",
             bolditalicfile=getBaseDir() + "//fonts//FreeFont//FreeMonoBoldOblique.ttf",
             fixedfile=getBaseDir() + "//fonts//FreeFont//FreeMono.ttf", 
             boldfixedfile=getBaseDir() + "//fonts//FreeFont//FreeMonoBold.ttf", 
             italicfixedfile=getBaseDir() + "//fonts//FreeFont//FreeMonoOblique.ttf",
             bolditalicfixedfile=getBaseDir() + "//fonts//FreeFont//FreeMonoBoldOblique.ttf",
            )

class window:
    y_coord = 1
    x_coord = 1
    y_size = 0
    x_size = 0
    y_cursor = 1
    x_cursor = 1
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

    def showCursor(self):
        area = pygame.Rect(self.x_coord+self.x_cursor, self.y_coord+self.y_cursor, 1, self.getFont().getHeight())
        pygame.draw.rect(self.screen.screen, self.foreground_colour, area)

    def hideCursor(self):
        area = pygame.Rect(self.x_coord+self.x_cursor, self.y_coord+self.y_cursor, 1, self.getFont().getHeight())
        pygame.draw.rect(self.screen.screen, self.background_colour, area)

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
        x = x - 1 + self.getPosition()[0] - 1
        y = y - 1 + self.getPosition()[1] - 1
        try:
            return self.screen.getPixel(x, y)
        except:
            return -1

    def erase(self):
        area = pygame.Rect((self.x_coord-1, self.y_coord-1), (self.x_size, self.y_size))
        self.screen.screen.fill(self.getColours()[1], area)
        self.screen.updates.append(area)
        self.line_count = 0
        self.x_cursor = 1
        self.y_cursor = 1


    def eraseArea(self, x, y, w, h):
        x = self.x_coord - 1 + x - 1
        y = self.y_coord - 1 + y - 1
        area = pygame.Rect(x, y, w, h)
        self.screen.screen.fill(self.getColours()[1], area)
        self.screen.updates.append(area)
        self.screen.update()


    def getFont(self):
        return font


    def preNewline():
        pass

    def postNewline():
        pass

    def scroll(self, amount, dir=0):
        if dir == 0: # scroll area up
            # copy an image of the window - *amount* pixels from the top to
            # the origin point of the window
            sourcex, sourcey = self.x_coord, self.y_coord + amount
            destx, desty = self.x_coord, self.y_coord
            width, height = self.getSize()
            height -= amount
            sourceRect = pygame.Rect(sourcex-1, sourcey-1, width, height)
            destRect = pygame.Rect(destx-1, desty-1, width, height)
            self.screen.screen.blit(self.screen.screen, destRect, sourceRect)
            # draw a rectangle of the background colour with height of *amount* at the bottom of
            # the window, to cover the text left behind
            destRect = pygame.Rect(destx - 1, sourcey - 1 + height - amount, width, amount)
            pygame.draw.rect(self.screen.screen, self.getColours()[1], destRect)
        else: # scroll area down
            # copy an image of the window - *amount* pixels from the bottom to
            # the origin point of the window + *amount* pixels down 
            sourcex, sourcey = self.x_coord, self.y_coord
            destx, desty = self.x_coord, self.y_coord + amount
            width, height = self.getSize()
            height -= amount
            sourceRect = pygame.Rect(sourcex-1, sourcey-1, width, height)
            destRect = pygame.Rect(destx-1, desty-1, width, height)
            self.screen.screen.blit(self.screen.screen, destRect, sourceRect)
            #self.screen.screen.set_clip()
            # draw a rectangle of the background colour with height of *amount* at the top of
            # the window, to cover the text left behind
            destRect = pygame.Rect(destx - 1, sourcey - 1, width, amount)
            pygame.draw.rect(self.screen.screen, self.getColours()[1], destRect)
        area = pygame.Rect(sourcex - 1, sourcey - 1, width, height)
        self.screen.updates.append(area)

    def printText(self, text):
        self.buffertext(text)
        buffering = self.testattribute(8)
        if text.find('\r') != -1 or buffering == False:
            self.flushTextBuffer() # flush the text buffer if a new line has been printed (or buffering is off)

    def fitText(self, text, width, wrapping=True, buffering=True):
        # if the text doesn't already fit, we make an educated guess at the right size
        # by dividing the width of the window in pixels by the width of the '0' character
        # in pixels. Then, if it is too small, we add characters until it fits, or if
        # it is too big, we remove characters until it fits.
        if width <= 0 or len(text) == 0:
            return 0
        elif self.getStringLength(text) <= width:
            x = len(text)
        else:
            charlen = self.getStringLength('0')
            x = width // charlen
            stringlen = self.getStringLength(text[:x])
                
            if stringlen < width:
                while stringlen < width:
                    stringlen = self.getStringLength(text[:x])
                    x += 1
                x -= 1
            if stringlen > width:
                while stringlen > width:
                    stringlen = self.getStringLength(text[:x])
                    x -= 1
            if x == -1:            
                x = 0
            if wrapping and buffering:
                x = text[:x].rfind(' ')         
        return x     

    def drawText(self, text):
        fg, bg = self.getColours()
        xpos, ypos = self.x_coord-1, self.y_coord-1
        xcursor, ycursor = self.x_cursor-1, self.y_cursor-1
        width, height = self.getSize()
        textsurface = self.getFont().render(text, 1, fg, bg)
        x = xpos + xcursor
        y = ypos + ycursor
        if text != '':
            self.screen.screen.blit(textsurface, (x,y))
        area = pygame.Rect(xpos, ypos, width, height)
        self.screen.updates.append(area)

    def flushTextBuffer(self):
        #self.hideCursor()
        self.setCursorToMargin()

        self.alterTabs()
     

        if self.x_cursor > self.x_size - self.right_margin:
            self.x_cursor = self.left_margin + 1

        buffering = self.testattribute(8)

        if not self.testattribute(1): # if wrapping is off
            linebuffers = []
            x = 0
            while x != -1:
                x = self.textbuffer.find('\r')
                if x != -1:
                    linebuffers.append(self.textbuffer[:x])
                    self.textbuffer = self.textbuffer[x+1:]
                else:
                    linebuffers.append(self.textbuffer[:])
            for a in range(len(linebuffers)):
                winwidth = (self.x_size - (self.x_cursor - 1) - self.right_margin)
                x = self.fitText(linebuffers[a][:], winwidth, wrapping=False, buffering=buffering)
                linebuffer = linebuffers[a][0:x]
                

                self.drawText(linebuffer)
                if a < len(linebuffers) - 1:
                    self.newline()
                else:
                    self.x_cursor += self.getStringLength(linebuffer)
            self.textbuffer = ''
            
        else:
            while (len(self.textbuffer) > 0):                
                winwidth = (self.x_size - (self.x_cursor - 1) - self.right_margin)
                x = self.fitText(self.textbuffer[:], winwidth, buffering=buffering)
                definitescroll = 0
                linebuffer = self.textbuffer[:]
                if linebuffer[:x].find('\r') != -1:
                    x = linebuffer[:x].find('\r')
                    definitescroll = 1
                linebuffer = self.textbuffer[:x]
                self.textbuffer = self.textbuffer[len(linebuffer):]
                
                
                

                if len(self.textbuffer) > 0 and ((self.textbuffer[0] == ' ') or (self.textbuffer[0] == '\r')):
                    self.textbuffer = self.textbuffer[1:len(self.textbuffer)]
                
                self.drawText(linebuffer)
                self.cdown = False
                if definitescroll == 1 or len(self.textbuffer) > 0:
                    self.newline()
                else:
                    self.x_cursor += self.getStringLength(linebuffer)
                if self.cdown:
                    return 1
        

        #self.showCursor()
        #self.screen.update() # if we uncomment this, screen updates are more immediate, but that means you see everything getting slowly drawn


    def getStringLength(self, text):
        return self.getFont().getStringLength(text)

    def getStringHeight(self, text):
        return self.getFont().getHeight()

class screen:
    updates = []
    def __init__(self, width, height, title='', background=0xFFFFFF):
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption(title)
        self.screen.fill(background)
        self.width = width
        self.height = height
        self.update()

    def update(self):
        pygame.display.update()

    def getWidth(self):
        return self.width
    
    def getHeight(self):
        return self.height

    def getPixel(self, x,y):
        return self.screen.get_at((x-1, y-1))

    def erase(self, colour, area=None):
        if area:
            area = list(area)
            area[0] -= 1
            area[1] -= 1
            area = pygame.Rect((area))
        else:
            area = pygame.Rect((0, 0), (self.getWidth(), self.getHeight()))
        self.screen.fill(colour, area)
        self.updates.append(area)


    background = 0xFFFFFF
    resized = False
    justloaded = True

    def resize(self, newsize):
        if self.justloaded:
            self.justloaded = False
            return False
        x = pygame.display.Info()
        size = self.screen.get_rect()
        oldwidth = self.getWidth()
        oldheight = self.getHeight()
        screenwidth = newsize[0]
        screenheight = newsize[1]        
        self.width = screenwidth
        self.height = screenheight
        backup = pygame.Surface((oldwidth, oldheight))
        if screenwidth < oldwidth:
            oldwidth = screenwidth
        if screenheight < oldheight:
            oldheight = screenheight

        backup.blit(self.screen, (0,0))
        self.screen = pygame.display.set_mode((screenwidth, screenheight), pygame.RESIZABLE)
        self.screen.set_clip(None)

        self.erase(self.background)
        self.screen.set_clip(pygame.Rect(0,0,oldwidth,oldheight))
        self.screen.blit(backup, (0,0))
        self.screen.set_clip(None)
        self.resized = True
        self.update()




class keypress:
    def __init__(self, value, character, modifier):
        self.value = value
        self.character = character
        self.modifer = modifier

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
        try:
            self.button = mousebuttonmapping[event.button]
        except:
            self.button = None
    button = None

class mouseup:
    def __init__(self, event):
        try:
            self.button = mousebuttonmapping[event.button]
        except:
            self.button = None
    button = None


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
            return keypress(event.key, event.unicode, event.mod)
        if event.type == VIDEORESIZE:
            self.screen.resize(event.dict['size'])
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
    global currentfont
    global inputtext
    global timerrunning
    timerrunning = False
    inputtext = []
    pygame.key.set_repeat(100, 100)

def getinput(screen):
    i = input(screen).getinput()
  
    if isinstance(i, keypress):
        return i
    else:
        return None

def openfile(window, mode, filename=None, prompt=None):
    global GAMEDIRECTORY
    # if filename == None, prompt for a filename
    # returns a file object to be read/written



    if filename == None: # should prompt for filename
        prompt = True

    if prompt: # prompt for filename, but supply suggestion
        
        window.printText('Filename: ')
        window.flushTextBuffer()
        i = None
        c = None
        if filename:
            t = list(filename)
            window.printText(filename)
            window.flushTextBuffer()
        else:
            t = []
        while c != '\r':
            i = getinput(window.screen) 
            if i:
                c = i.character
                if ord(c) == 8 and len(t) > 0:
                    window.backspace(t.pop())
                else:
                    t.append(c)
                    window.printText(c)
                    window.flushTextBuffer()
        t.pop()
        filename = ''.join(t)

    filename = os.path.basename(filename) # strip the directory information from the filename (maybe should allow it if it's a subfolder of the game directory?)
    filename = os.path.join(GAMEDIRECTORY, filename) # use the game directory as the location for file

    if mode == 'a':
        if findfile(filename) == False:
            mode = 'w'
    mode = mode + 'b'
 
    try:
        f = open(filename, mode)
    except:
        f = None

    return f

    

        
def makemenu(title, items, number): # title is a string, items is a list of strings, number is the id number
    return 0
#    if number < 3 or number > 10:
#        return 0
#    if menus[number] != 0:
#        destroymenu(number)
#    menus[number] = wx.Menu()
#    for a in xrange(len(items)):
#        num = number * 100 + a
#        menus[number].Append(num, items[a])
#
#        menubar.Insert(number-2, menus[number], title)
#        return 1

def destroymenu(number):
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





def beep():
    try:
        f = getBaseDir() + "//sounds//beep.aiff"
        b = pygame.mixer.Sound(f)
        b.play()
    except:
        pass


def boop():
    try:
        f = getBaseDir() + "//sounds//boop.aiff"
        b = pygame.mixer.Sound(f)
        b.play()
    except:
        pass

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

soundchannels = [[],[]]

def soundhandler():
    for a in soundchannels:
        for b in a:
            b.Notify()

     
class musicChannel(soundChannel):
    type = 1

    def getbusy(self):
        return pygame.mixer.music.get_busy()

    def play(self, sound, volume, repeats, routine):
        self.sound = sound
        if self.sound.type != 1:
            self.sound = None
            return False
        self.routine = routine
        self.sound.play(volume, repeats)
        self.setup(soundhandler)
    
    def setvolume(self, volume):
        pygame.mixer.music.set_volume(volume)

    def stop(self, sound):
        if self.sound == None:
            return False
        if self.sound.number == sound.number:
            self.routine = None
            self.sound.stop()
            self.sound = None
            self.cleanup()



class effectsChannel(soundChannel):
    type = 0

    def __init__(self, id):
        self.id = id
        self.channelobj = pygame.mixer.Channel(id)

    channelobj = None

    def getbusy(self):
        try:
            busy = self.channelobj.get_busy()
        except:
            busy = False
        return busy

    def play(self, sound, volume, repeats, routine):
        self.sound = sound
        if self.sound.type != 0:
            self.sound = None
            return False      
        self.routine = routine
        self.setvolume(volume)
        self.channelobj.play(self.sound.sound, repeats)
        self.setup(soundhandler)

    def setvolume(self, volume):
        self.channelobj.set_volume(volume)

    def stop(self, sound):
        if self.sound == None:
            return False
        if self.sound.number == sound.number:
            self.routine = None
            self.channelobj.stop()
            self.sound = None

            self.cleanup()

def stopallsounds():
    pygame.mixer.stop()

def initsound():
    pygame.mixer.init()
