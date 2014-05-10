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
import string
import zio as io
import settings
import zcode


def setup(b, width=800, height=600, foreground=2, background=9, title='', restarted=False):
    global zwindow
    global statusline
    global currentWindow
    global ioScreen
    global fonts
    global blorbs
    global pixelunits


    if zcode.header.zversion() == 6:
        pixelunits = True # in z6, units should be pixels, not characters
    if zcode.header.zversion() >= 5 and zcode.header.getflag(3, 1) == 1:
        pixelunits = True # if the game wishes to change font sizes, units should be pixels, not characters

    if not width:
        width = 800
    if not height:
        height = 600
    if restarted == False:
        ioScreen = io.pygame.screen(width, height, title)

    blorbs = b

    zwindow = []

    # create all the windows
    zwindow.append(window(ioScreen, fontlist[1])) # lower window (window 0)
    if zcode.header.zversion() < 4:
        statusline = window(ioScreen, fontlist[1]) # statusline
        statusline.window_id = "statusline"
    if zcode.header.zversion() > 2:
        zwindow.append(window(ioScreen, fontlist[1])) # upper window (window 1)
    if zcode.header.zversion() == 6:
        for a in range(6):
            zwindow.append(window(ioScreen, fontlist[1])) # windows 2 to 7
    for a in range(len(zwindow)):
        getWindow(a).window_id = str(a)
     

    # set the current window
        
    currentWindow = getWindow(0)

    # set up fonts

    if zcode.header.zversion() != 6 and zcode.header.zversion() >= 3:
        getWindow(1).fontlist[1] = font4
    if zcode.header.zversion() < 4:
        statusline.fontlist[1] = font4

    for a in zwindow:
        a.setFontByNumber(1)
    if zcode.header.zversion() < 4:
        statusline.setFontByNumber(1)



    # position and size the windows

    if zcode.header.zversion() == 6: # version 6
        for a in range(len(zwindow)):
            getWindow(a).setPosition(1, 1)
            getWindow(a).setSize(0,0)
        getWindow(0).setSize(ioScreen.getWidth(), ioScreen.getHeight())
        getWindow(1).setSize(ioScreen.getWidth(), 0)
    elif zcode.header.zversion() < 4: # version 1, 2 and 3
        getWindow(0).setSize(ioScreen.getWidth(), ioScreen.getHeight() - getWindow(0).getFont().getHeight())
        getWindow(0).setPosition(1, getWindow(0).getFont().getHeight() + 1)
        statusline.setSize(ioScreen.getWidth(), statusline.getFont().getHeight())
        statusline.setPosition(1, 1)
        if zcode.header.zversion() == 3: # version 3
            zwindow[1].setSize(ioScreen.getWidth(), 0)
            zwindow[1].setPosition(1, zwindow[1].getFont().getHeight() + 1)
    else: # version 4, 5, 7 and 8
        zwindow[0].setSize(ioScreen.getWidth(), ioScreen.getHeight())
        zwindow[0].setPosition(1, 1)
        zwindow[1].setSize(ioScreen.getWidth(), 0)
        zwindow[1].setPosition(1, 1)

    # set the cursor in the windows

    if zcode.header.zversion() == 6:
        for a in range(len(zwindow)):
            zwindow[a].setCursor(1,1)
    elif zcode.header.zversion() < 5:
        zwindow[0].setCursor(1, zwindow[0].y_size - zwindow[0].getFont().getHeight() + 1)
    else:
        zwindow[0].setCursor(1, 1)

    # set up window attributes

    if zcode.header.zversion() == 6:
        for a in range(len(zwindow)):
            zwindow[a].setattributes(8, 0)
        zwindow[0].setattributes(15, 0)
    elif zcode.header.zversion() < 4:
        zwindow[0].setattributes(15,0)
        statusline.setattributes(0,0)
        if zcode.header.zversion() == 3:
            zwindow[1].setattributes(4,0)
    else:
        zwindow[0].setattributes(15,0)
        zwindow[1].setattributes(4,0)

    # set other default window properties

    for a in range(len(zwindow)):
        zwindow[a].setBasicColours(foreground, background, flush=False)
        zwindow[a].font_size = (zwindow[a].getFont().getHeight() << 8) + zwindow[a].getFont().getWidth()
    if zcode.header.zversion() < 4:
        statusline.setBasicColours(background, foreground, flush=False)
        statusline.font_size = (statusline.getFont().getHeight() << 8) + statusline.getFont().getWidth()
    
    # give the lower window in versions other than 6 a margin
    if zcode.header.zversion() != 6:
        getWindow(0).left_margin = 5
        getWindow(0).right_margin = 5
   

pixelunits = False # should units be pixels? Generally only set True in z6 games, but also when z5 want to change font sizes


def supportedgraphics(arg): # should really tie this into the io module
    if arg == 0: # colour
        return 1
    if arg == 1: # true colour
        return 1
    if arg == 2: # transparent background colour
        if zcode.header.zversion() == 6:
            return 1
        return 0
    if arg == 3: # picture displaying 
        if zcode.header.zversion() == 6:
            return 1
        return 0
    return 0

def supportedstyles(arg):
    if arg >= 0x10: # we don't recognize any styles above 8
        return 0
    return 1 # all other styles and combinations are supported

# font 3 needs to be the same size as fixed width font

class font(io.pygame.font):
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

    def render(self, text, antialias, colour, background):

        f = self.fontData()
        if self.reversevideo:
            return f.render(text, antialias, background, colour)
        else:
            return f.render(text, antialias, colour, background)


class runicfont(io.pygame.font):
    def __init__(self, fontfile, size=14, boldfile=None, italicfile=None, bolditalicfile=None):
        self.default_size = size
        self.size = size
        self.font_data = io.pygame.image('images\\GfxFont.png', filename=True)
        self.width = font[4].getWidth()
        self.height = fonts[4].getHeight()
    
    bold = False
    italic = False
       
    def setBold(self, value):
        if value:
            self.bold = True
        else:
            self.bold = False

    def setItalic(self, value):
        if value:
            self.bold = False
        else:
            self.italic = False

    def getWidth(self):    
        return self.width
    
    def getHeight(self):
        return self.height

    def getStringLength(self, text):
        return self.width() * len(text)

    def getAscent(self):
        return self.getHeight()

    def getDescent(self):
        return 0

    def defaultSize(self):
        return 14

    def resize(self, dif):
        if dif == 0:
            self.size = self.defaultSize()
        else:
            self.size += dif

    def render(self, text, antialias, colour, background):
        
        return f.render(text, antialias, colour, background)

    def font(self):
        char = ord(char) - 32
        x = (char % 32) * fonts[4].getWidth()
        
        return None
        
    def drawchar(self, char):
        # once we have the right picture, we need to scale it to exactly the size of the fixed width font
        char = ord(char) - 32
        x = (char % 32) * fonts[4].getWidth()
        row = char // 32
        y = row * self.width()
        w = (self.font_data.getWidth() // 8) * self.width
        h = (self.font_data.getHeight() // 8) * self.height
        c = c.scale(w,h)
        return c


fixedpitchbit = False

def pix2units(pix, horizontal, coord=False): # converts a number of pixels into a number of units
    if pixelunits:
        value = pix
    elif not horizontal:
        value = ((pix - 1) // currentWindow.getFont().getHeight()) + 1
    else:
        value = ((pix - 1) // currentWindow.getFont().getWidth()) + 1
    return value

def units2pix(units, horizontal, coord=False): # converts a number of units into a number of pixels
    if pixelunits:
        value = units
    elif not horizontal:
        value = units * currentWindow.getFont().getHeight()
        if coord:
            value -= currentWindow.getFont().getHeight()
            value += 1
    else:
        value = units * currentWindow.getFont().getWidth()
        if coord:
            value -= currentWindow.getFont().getWidth()
            value += 1
    return value

font1 = font(io.pygame.getBaseDir() + "//fonts//FreeSerif.ttf",
             boldfile=io.pygame.getBaseDir() + "//fonts//FreeSerifBold.ttf",
             italicfile=io.pygame.getBaseDir() + "//fonts//FreeSerifItalic.ttf",
             bolditalicfile=io.pygame.getBaseDir() + "//fonts//FreeSerifBoldItalic.ttf",
             fixedfile=io.pygame.getBaseDir() + "//fonts//FreeMono.ttf", 
             boldfixedfile=io.pygame.getBaseDir() + "//fonts//FreeMonoBold.ttf", 
             italicfixedfile=io.pygame.getBaseDir() + "//fonts//FreeMonoOblique.ttf",
             bolditalicfixedfile=io.pygame.getBaseDir() + "//fonts//FreeMonoBoldOblique.ttf",
            )

font4 = font(io.pygame.getBaseDir() + "//fonts//FreeMono.ttf", 
             boldfile=io.pygame.getBaseDir() + "//fonts//FreeMonoBold.ttf", 
             italicfile=io.pygame.getBaseDir() + "//fonts//FreeMonoOblique.ttf",
             bolditalicfile=io.pygame.getBaseDir() + "//fonts//FreeMonoBoldOblique.ttf",
             fixedfile=io.pygame.getBaseDir() + "//fonts//FreeMono.ttf", 
             boldfixedfile=io.pygame.getBaseDir() + "//fonts//FreeMonoBold.ttf", 
             italicfixedfile=io.pygame.getBaseDir() + "//fonts//FreeMonoOblique.ttf",
             bolditalicfixedfile=io.pygame.getBaseDir() + "//fonts//FreeMonoBoldOblique.ttf",
            )

fontlist = [ None, 
             font1,
             None, # picture font. Unspecified, should always return 0
             None, # Beyond Zork font. Going to require some hacking.
             font4
        ]





    
        


def resize():
    if zcode.header.zversion != 6:
        zwindow[0].setSize(ioScreen.getWidth(), ioScreen.getHeight())
        zwindow[1].setSize(ioScreen.getWidth(), zwindow[1].getSize()[1])
    if zcode.header.zversion() < 4:
        statusline.setSize(ioScreen.getWidth(), statusline.getSize()[1])

    # Screen height (lines)
    zcode.header.setscreenheightlines(ioScreen.getHeight() // getWindow(1).getFont().getHeight())
    # Screen width (chars)
    zcode.header.setscreenwidthchars(ioScreen.getWidth() // getWindow(1).getFont().getWidth())
        
    if zcode.header.zversion() > 4:
        # Screen width (units)
        if zcode.header.zversion() == 6:
            zcode.header.setscreenwidth(ioScreen.getWidth())
        else:
            zcode.header.setscreenwidth(ioScreen.getWidth() // getWindow(1).getFont().getWidth())
        # Screen height (units)
        if zcode.header.zversion() == 6:
            zcode.header.setscreenheight(ioScreen.getHeight())
        else:
            zcode.header.setscreenheight(ioScreen.getHeight() // getWindow(1).getFont().getHeight())
    if zcode.header.zversion() == 6:
        zcode.header.setflag(2, 2, 1)


def getWindow(winnum):
    winnum = zcode.numbers.neg(winnum)
    if winnum == -3:
        return currentWindow
    return zwindow[winnum]

def updatestatusline(): # updates the status line for z-machine versions 1 to 3
    statusline.erase()
    if zcode.header.getflag(1,1) == 1 and zcode.header.zversion() == 3:
        type = 1
    else:
        type = 0
    statusline.setCursor(2 * statusline.getFont().getWidth() + 1, 1)
    location = zcode.objects.getshortname(zcode.game.getglobal(0))
    statusline.printText(location)    
    statusline.flushTextBuffer()
    if type == 0:
        statusline.setCursor(statusline.getSize()[0] - (23 * statusline.getFont().getWidth()) + 1, 1)
        score = str(zcode.game.getglobal(1))
        statusline.printText('Score: ' + score)
        statusline.flushTextBuffer()
        statusline.setCursor(statusline.getSize()[0] - (12 * statusline.getFont().getWidth()) + 1, 1)
        turns = str(zcode.game.getglobal(2))
        statusline.printText('Turns: ' + turns)
        statusline.flushTextBuffer()
    else:
        statusline.setCursor(statusline.getSize()[0] - (12 * statusline.getFont().getWidth()) + 1, 1)
        hours = str(zcode.game.getglobal(1))
        minutes = str(zcode.game.getglobal(2))
        if zcode.game.getglobal(2) < 10:
            minutes = '0' + minutes
        statusline.printText('Time: ' + hours + ':' + minutes)
        statusline.flushTextBuffer()
    statusline.flushTextBuffer()
    # Score: 999  Turns: 9999 #
    #             Time: 20:52 #
    currentWindow = zwindow[0]

def printtext(text):
    currentWindow.printText(text)

mouse_window = 1



# Colour definitions

colours = { 'under_cursor' : -1,
            'current' : 0,
            'default' : 1,
            'black' : 2,
            'red' : 3,
            'green' : 4,
            'yellow' : 5,
            'blue' : 6,
            'magenta' : 7,
            'cyan' : 8,
            'white' : 9,
            'light_grey' : 10,
            'medium_grey' : 11,
            'dark_grey' : 12
          }

def checkcolours():
    """Returns 1 if colours are available, 0 if unavailable."""
    return io.pygame.checkcolour()

# Styles definitions

styles = { 'roman'   : 0, # Selecting this style unselects all other styles.
           'bold'    : 1, # This style should make the text bold, or otherwise emphasized.
           'italic'  : 2, # This one should make it italic. Some interpreters make it underlined.
           'reverse' : 4, # Selecting this style reverses the text colours.
           'fixed'   : 8, # One of three ways to get fixed-pitch text. 
         }

spectrum = { 2 : 0x0000, # Black
             3 : 0x001D, # Red
             4 : 0x0340, # Green
             5 : 0x03BD, # Yellow
             6 : 0x59A0, # Blue
             7 : 0x7C1F, # Magenta
             8 : 0x77A0, # Cyan
             9 : 0x7FFF, # White
             10: 0x5AD6, # Light Grey
             11: 0x4631, # Medium Grey
             12: 0x2D6B, # Dark Grey
           }

def reverseSpectrumLookup(colour):
    for a in spectrum:
        if spectrum[a] == colour:
            return a
    return False
    



def fittext(text, width, wrapping=True, buffering=True):
    # if the text doesn't already fit, we make an educated guess at the right size
    # by dividing the width of the window in pixels by the width of the '0' character
    # in pixels. Then, if it is too small, we add characters until it fits, or if
    # it is too big, we remove characters until it fits.
    if width <= 0 or len(text) == 0:
        return 0
    elif currentWindow.getStringLength(text) <= width:
        x = len(text)
    else:
        charlen = currentWindow.getStringLength('0')
        x = width // charlen
        stringlen = currentWindow.getStringLength(text[:x])
            
        if stringlen < width:
            while stringlen < width:
                stringlen = currentWindow.getStringLength(text[:x])
                x += 1
            x -= 1
        if stringlen > width:
            while stringlen > width:
                stringlen = currentWindow.getStringLength(text[:x])
                x -= 1
        if x == -1:            
            x = 0
        if wrapping and buffering:
            x = text[:x].rfind(' ')         
    return x

# Windows. Yay!

def truetofull(incolour):
    b = incolour >> 10
    g = (incolour >> 5) & 31
    r = incolour & 31
    r = (r << 3) | (r >> 2)
    b = (b << 3) | (b >> 2)
    g = (g << 3) | (g >> 2)
    outcolour=(r,g,b)
    return outcolour



class window(io.pygame.window):
    def __str__(self):
        return 'window ' + str(self.window_id)
    # window properties (window coordinates are measured from 1,1, not 0,0, oh no. That would be sensible.)
    newline_routine = 0
    interrupt_countdown = 0
    basic_foreground_colour = 0
    basic_background_colour = 0
    font_number = 1
    font_size = 0
    attributes = 0
    true_foreground_colour = 0
    true_background_colour = 0

    relative_font_size = 0
    old_relative_font_size = 0
    window_id = None
    last_x_cursor = 1

    def __init__(self, screen, font):
        self.screen = screen
        self.fontlist = fontlist[:]
        self.setFont(font)
        self.setBasicColours(2, 9, flush=False)
        self.getFont().resetSize()

    def testfont(self, font):
        """Checks to see if the givenfont is available for use. Returns 1 if available, 0 if unavailable."""
        if font > len(self.fontlist):
            return False
        if self.fontlist[font] == None:
            return False
        else:
            return True


    def setFontSize(self, newsize):
        self.flushTextBuffer()
        if self.getFont().defaultSize() + newsize < 1:
            return False
        if newsize > 10:
            return False
        self.old_relative_font_size = self.relative_font_size
        self.relative_font_size += newsize
        self.getFont().resize(newsize)
        if self.getFont().getHeight() > self.maxfontheight:
            self.maxfontheight = self.getFont().getHeight()
        ascent = self.getFont().getAscent()
        descent = self.getFont().getDescent()
        self.font_metrics = ((ascent & 255) << 8) + (descent & 255)
        return True

    def getFont(self):
        if fixedpitchbit:
            return self.fontlist[4]
        return self.font


    def resetfontsize(self):
        s = self.old_relative_font_size - self.relative_font_size
        self.setfontsize(s)

    def atMargin(self): #
        """Checks to see if the cursor is at the left margin"""
        if self.getCursor()[0] == self.left_margin + 1:
            return True
        else:
            return False
   
    def setBasicColours(self, foreground, background, flush=True):
        self.basic_foreground_colour = foreground
        self.basic_background_colour = background
        if foreground == 16:
            foreground = -3
        else:
            foreground = spectrum[foreground]
        if background == 16:
            background = -3
        elif background == 15:
            background = -4
        else:
            background = spectrum[background]
        self.setTrueColours(foreground, background, True, flush=flush)

    def getBasicColours(self):
        return (self.basic_foreground_colour, self.basic_background_colour)



    def setTrueColours(self, foreground, background, fromspectrum=False, flush=True):
        if flush:
            self.flushTextBuffer()
        fo = 16
        bo = 16
        if foreground == -3:
            foreground = self.getPixelColour(self.getCursor()[0], self.getCursor()[1])
            fg = self.getTrueFromReal(foreground)
        else:
            fg = foreground
            foreground = truetofull(foreground)

        if background == -3:

            background = self.getPixelColour(self.getCursor()[0], self.getCursor()[1])
            bg = self.getTrueFromReal(background)
        elif background != -4:
            bg = background
            background = truetofull(background)

        if background == -4:
            bg = -4
            bo = 15           

        
        
           
        self.true_foreground_colour = fg
        self.true_background_colour = bg
        self.setColours(foreground, background)


    def getTrueColours(self):
        return (self.true_foreground_colour, self.true_background_colour)


    def getTrueFromReal(self, colour):
        r = colour[0] // 8
        g = colour[1] // 8
        b = colour[2] // 8
        c = (((b << 5) + g) << 5) + r
        return c

    
    def setMargins(self, left, right):
        self.left_margin = left
        self.right_margin = right
        self.setCursorToMargin()



    reversevideo = False
    fixedstyle = False

    def setStyle(self, style):
        self.flushTextBuffer()
        if style == 0:
            self.font.setReverse(False)
            self.font.setFixed(False)
            self.font.setBold(False)
            self.font.setItalic(False)
        else:
            if style & 1:
                self.font.setReverse(True)
            if style & 2:
                self.font.setBold(True)
            if style & 4:
                self.font.setItalic(True)
            if style & 8:
                self.font.setFixed(True)


    def getStyle(self):
        s = 0
        if self.font.reversevideo:
            s += 1
        if self.font.bold:
            s += 2
        if self.font.italic:
            s += 4
        if self.font.fixedstyle:
            s += 8
        return s

    def setPosition(self, x, y):
        self.x_coord = x - 1
        self.y_coord = y - 1

    def getPosition(self):
        return (self.x_coord + 1, self.y_coord + 1)

    def setCursor(self, x, y):
        self.x_cursor = x - 1
        self.y_cursor = y - 1

    def getCursor(self):
        return (self.x_cursor + 1, self.y_cursor + 1)

    def getPixelColour(self, x, y):
        x += self.getPosition()[0] - 1
        y += self.getPosition()[1] - 1
        return self.screen.getPixel(x - 1, y - 1)

    def setCursorToMargin(self): # makes sure the cursor is inside the margins
        if (self.getCursor()[0] <= self.left_margin) or (self.getCursor()[0] >= (self.getSize()[0] - self.right_margin)):
            self.setCursor(self.left_margin + 1, self.getCursor()[1])

    
    def setprops(self, property, value):
        """General purpose routine to set the value of a window property by property number. Generally not used."""
        if property == 0:
            self.setPosition(self.getPosition()[0], value)
        elif property == 1:
            self.setPosition(value, self.getPosition()[1])
        elif property == 2:
            self.setSize(self.getSize()[0], value)
        elif property == 3:
            self.setSize(value, self.getSize()[1])
        elif property == 4:
            self.setCursor(self.getCursor()[0], value)
        elif property == 5:
            self.setCursor(value, self.getCursor()[1])
        elif property == 6:
            self.left_margin = value
        elif property == 7:
            self.right_margin = value
        elif property == 8:
            self.newline_routine = value
        elif property == 9:
            self.interrupt_countdown = value
        elif property == 10:
            self.setStyle(value)
        elif property == 11:
            fg = value & 255
            bg = value >> 8
            self.setBasicColours(fg, bg)
        elif property == 12:
            self.setFontByNumber(value)
        elif property == 13:
            pass
        elif property == 14:
            self.attributes = value
        elif property == 15:
            self.line_count = value
        elif property == 16:
            pass
        elif property == 17:
            pass
        elif property == 18:
            pass
        else:
            return False

    def getprops(self, property):
        """General purpose routine to retrieve the value of a window property, by property number. Also generally not used."""
        if property == 0:
            return self.getPosition()[1]
        elif property == 1:
            return self.getPosition()[0]
        elif property == 2:
            return self.getSize()[1]
        elif property == 3:
            return self.getSize()[0]
        elif property == 4:
            return self.getCursor()[1]
        elif property == 5:
            return self.getCursor()[0]
        elif property == 6:
            return self.left_margin
        elif property == 7:
            return self.right_margin
        elif property == 8:
            return self.newline_routine
        elif property == 9:
            return self.interrupt_countdown
        elif property == 10:
            return self.getStyle()
        elif property == 11:
            fg, bg = self.getBasicColours()
            return (bg << 8) + fg
        elif property == 12:
            return self.font_number
        elif property == 13:
            return self.font_size
        elif property == 14:
            return self.attributes
        elif property == 15:
            return self.line_count
        elif property == 16:
            return self.true_foreground_colour
        elif property == 17:
            return self.true_background_colour
        elif property == 18:
            return self.font_metrics
        else:
            return False

    # functions to retrieve more meaningful info from properites

    
    def setattributes(self, flags, operation):
        if operation == 0:
            self.attributes = flags
        elif operation == 1:
            self.attributes = self.attributes | flags
        elif operation == 2:
            self.attributes = self.attributes & ~flags
        elif operation == 3:
            self.attributes - self.attributes & flags

    def testattributes(self, attribute):
        result = self.attributes & attribute
        if result == attribute:
            return True
        else:
            return False
   
    textbuffer = ''
    linetextbuffer = []
    stylebuffer = []
    linestylebuffer = []

    chars = 0 # the number of characters printed thus far without a font, colour or style change

    def updatestylebuffer():
        pass

    def buffertext(self, text):
        x = list(self.textbuffer)
        x.extend(text)
        self.textbuffer = ''.join(x)
        #self.chars += len(text)

    def alterTabs(self): # changes the tab character to various spaces
        x = list(self.textbuffer)
        if len(x) > 0 and x[0] == '\t' and self.atMargin():
            x[0] = '   '
        self.textbuffer = ''.join(x)
        self.textbuffer = self.textbuffer.replace('\t', ' ')


    def flushTextBuffer(self):
        #self.hideCursor()
        self.setCursorToMargin()

        self.alterTabs()
     

        if self.x_cursor > self.x_size - self.right_margin:
            self.x_cursor = self.left_margin + 1

        buffering = self.testattributes(8)

        if not self.testattributes(1): # if wrapping is off
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
                winwidth = (self.x_size - self.x_cursor - self.right_margin)
                x = fittext(linebuffers[a][:], winwidth, wrapping=False, buffering=buffering)
                linebuffer = linebuffers[a][0:x]
                

                self.drawText(linebuffer)
                if a < len(linebuffers) - 1:
                    self.newline()
                else:
                    self.x_cursor += self.getStringLength(linebuffer)
            self.textbuffer = ''
            
        else:
            while (len(self.textbuffer) > 0) and (zcode.routines.scrolling == 0):                
                winwidth = (self.x_size - self.x_cursor - self.right_margin)
                x = fittext(self.textbuffer[:], winwidth, buffering=buffering)
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
        
        if self.screen.resized:
            self.screen.resized = False
            resize()
        #self.showCursor()
        #self.screen.update() # if we uncomment this, screen updates are more immediate, but that means you see everything getting slowly drawn


    maxfontheight = 0

    def preNewline(self):
        story = settings.code
        # call the interrupt routine (if it's time to do so)
        if zcode.header.getterpnum() != 6 or story != '393.890714':
            self.cdown = self.countdown()

    def postNewline(self):
        story = settings.code
        if zcode.header.getterpnum() == 6 and story == '393.890714':
            self.cdown = self.countdown()

    def newline(self):
        self.preNewline()
        # move to the new line
        self.setCursor(self.getCursor()[0], self.getCursor()[1] + self.getFont().getHeight())
        if self.getCursor()[1] >= self.getSize()[1] - self.getFont().getHeight():
            if self.testattributes(2):
                self.scroll(self.getFont().getHeight()) # scroll the window region up
                self.setCursor(self.getCursor()[0], self.getCursor()[1] - self.getFont().getHeight())
        if self.line_count != -999:
            self.line_count+=1
        
        # put the cursor at the current left margin
        self.setCursor(self.left_margin + 1, self.getCursor()[1])
        if self.line_count >= (self.getSize()[1] // self.getFont().getHeight()) - 1 and self.testattributes(2):
            self.line_count = 0
            morestring = '[MORE]'
            self.drawText(morestring)
            while zcode.input.getinput(ignore=True) != 32:
                pass
            x = self.getCursor()[0] + self.getPosition()[0] - 1
            y = self.getCursor()[1] + self.getPosition()[1] - 1
            w = zcode.screen.currentWindow.getStringLength(morestring)
            h = zcode.screen.currentWindow.getStringHeight(morestring)
            zcode.screen.currentWindow.eraseArea(x-1,y-1,w,h)
            currentWindow.flushTextBuffer()

        self.postNewline()







    def countdown(self):
        if self.interrupt_countdown != 0:
            self.interrupt_countdown -= 1
            if self.interrupt_countdown == 0:
                i = zcode.game.interruptdata(zcode.game.INT_NEWLINE, self.newline_routine)
                zcode.game.interruptstack.append(i)
                zcode.game.interrupt_call()
                return 1

 
    def backspace(self, char):
        self.hideCursor()
        charwidth = self.getStringLength(char)
        charheight = self.getStringHeight(char)
        self.setCursor(self.getCursor()[0] - charwidth, self.getCursor()[1])
        area = ((self.getPosition()[0] + self.getCursor()[0]) - 1, (self.getPosition()[1] + self.getCursor()[1] - 1), charwidth, charheight)
        ioScreen.erase(self.getColours()[1], area)
        self.screen.update()
    
    
  

    def setFontByNumber(self, newfont):
        """Attempts to set the current font to newfont. Returns previous font number if successful, 0 if
           unsuccesful"""
        if self.testfont(newfont):
            self.flushTextBuffer()
            prevfont = self.getFontNumber()
            self.font_number = newfont
            self.setFont(self.fontlist[newfont])
            self.font_size = (self.getFont().getHeight() << 8) + self.getFont().getWidth()
            return prevfont
        else:
            return 0

    #current_font = 1

    def getFontNumber(self):
        """Returns the number of the current font."""
        return self.font_number
         
    def getpic(self, picture_number):
        picture_data = False
        scale = 1
        for a in blorbs:
            picture_data = a.getPict(picture_number)
            scale = a.getScale(picture_number, ioScreen.getWidth(), ioScreen.getHeight())
        if not picture_data:
            return None
        pic = io.pygame.image(picture_data)
        newwidth = pic.getWidth() * scale
        newheight = pic.getHeight() * scale
        pic = pic.scale(newwidth, newheight)
        palette = pic.getPalette()
        if palette:
            for a in blorbs:
                palette = a.getPalette(picture_number, palette)
            pic.setPalette(palette)
        return pic
            
        
    def drawpic(self, picture_number, x, y):
        pic = self.getpic(picture_number)
        if pic:
            pic.draw(self, (self.getPosition()[0] + x - 1 - 1), (self.getPosition()[1] + y - 1 - 1))

    def erasepic(self, picture_data, x, y, scale=1):
        pic = io.pygame.image(picture_data)
        newwidth = pic.getWidth() * scale
        newheight = pic.getHeight() * scale

        if self.getColours()[1] != -4:
            area = ((self.getPosition()[0] + x - 1 - 1), (self.getPosition()[1] + y - 1 - 1), newwidth, newheight)
            ioScreen.erase(self.getColours()[1], area)

    def eraseline(self, len):
        if self.getColours()[1] != -4:
            ioScreen.erase(self.getColours()[1], (self.getCursor()[0], self.getCursor()[1], len, self.getFont().getHeight()))
    fontlist = []


def eraseWindow(winnum):
    if zcode.numbers.neg(winnum) < 0 and currentWindow.getColours()[1] == -4:
        pass
    elif zcode.numbers.neg(winnum) == -1: # this should unsplit the screen, too. And move the cursor.
        ioScreen.erase(currentWindow.getColours()[1])
        split(0)
        for a in range(len(zwindow)):
            zwindow[a].setCursor(1, 1)
            zwindow[a].line_count = 0
    elif zcode.numbers.neg(winnum) == -2: # this doesn't unsplit the screen, but apparently may move the cursor. I don't get it. (actually, I think the spec's wrong)
        currentWindow.erase(currentWindow.getColours()[1])
    elif getWindow(winnum).getColours()[1] != -4:        
        getWindow(winnum).erase()
        if zcode.header.zversion() < 5 and winnum == 0:
            getWindow(0).setCursor(getWindow(0).getCursor()[0], getWindow(0).getSize()[1] - getWindow(0).getFont().getHeight())



def cursoron(): # makes the cursor visible
    global showcursor
    #showcursor = 1
    #io.pygame.showcursor()

def cursoroff(): # makes the cursor invisible
    global showcursor
    #showcursor = 0
    #io.pygame.hidecursor()

def split(size): # this is wrong. Infocom's terps and Frotz do not change the width of the windows
    oldycoord = zwindow[0].getPosition()[1]

    zwindow[0].setPosition(1, size + 1)
    zwindow[0].setSize(zwindow[0].getSize()[0], ioScreen.getHeight() - size)

    zwindow[1].setPosition(1, 1)
    zwindow[1].setSize(zwindow[1].getSize()[0], size)



    if zcode.header.zversion() == 3:
        eraseWindow(1)

    # move the window's cursor to the same absolute position in was in before the split

    difference = zwindow[0].getPosition()[1] - oldycoord
    zwindow[0].setCursor(zwindow[0].getCursor()[0], zwindow[0].getCursor()[1] - difference)

    # if the cursor now lies outside the window, move it to the window origin

    if (zwindow[0].getCursor()[1] > zwindow[0].getSize()[1]) or (zwindow[0].getCursor()[1] < 1):
        zwindow[0].setCursor(1,1)
    
    if (zwindow[1].getCursor()[1] > zwindow[0].getSize()[1]) or (zwindow[1].getCursor()[1] < 1):
        zwindow[1].setCursor(1,1)
