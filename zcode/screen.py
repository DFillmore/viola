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


import settings
import data
import vio.zcode as io
import zcode
from zcode.constants import *

screen_buffer_mode = 0

graphics_mode = 0

cursor = True

DEFFOREGROUND = 2
DEFBACKGROUND = 9


def setup(restarted=False):
    global zwindow
    global statusline
    global currentWindow
    global ioScreen
    global fonts
    global unitHeight
    global unitWidth
    global spectrum
    global DEFFOREGROUND
    global DEFBACKGROUND
    global graphics_mode

    colours.update(special_colours)

    if zcode.memory.data[0] == 6:  # if we're running a Version 6 game
        graphics_mode = 1  # set to graphics mode (units == pixels, not units == characters)
        colours.update(v6_colours)

    if zcode.use_standard < STANDARD_11:
        spectrum.pop(15)

    if restarted == False:
        ioScreen = io.zApp.screen

    foreground, background = ioScreen.defaultForeground, ioScreen.defaultBackground
    DEFFOREGROUND, DEFBACKGROUND = convertRealToBasicColour(foreground), convertRealToBasicColour(background)

    width = ioScreen.width
    height = ioScreen.height

    zwindow = []

    # create all the windows
    zwindow.append(window(ioScreen, fontlist[1]))  # lower window (window 0)
    if zcode.memory.data[0] < 4:
        statusline = window(ioScreen, fontlist[1])  # statusline
        statusline.window_id = "statusline"
    if zcode.memory.data[0] > 2:
        zwindow.append(window(ioScreen, fontlist[1]))  # upper window (window 1)
    if zcode.memory.data[0] == 6:
        for a in range(6):
            zwindow.append(window(ioScreen, fontlist[1]))  # windows 2 to 7
    for count, value in enumerate(zwindow):
        getWindow(count).window_id = str(count)

    if graphics_mode == 1:  # units are pixels
        unitHeight = 1
        unitWidth = 1
    else:  # units are characters
        unitHeight = getWindow(0).getFont().getHeight()
        unitWidth = getWindow(0).getFont().getWidth()

        # set the current window

    currentWindow = getWindow(0)

    # set up fonts

    if zcode.memory.data[0] != 6 and zcode.memory.data[0] >= 3:
        getWindow(1).fontlist[1] = fontlist[4]
    if zcode.memory.data[0] < 4:
        statusline.fontlist[1] = fontlist[4]

    for a in zwindow:
        a.setFontByNumber(1)
    if zcode.memory.data[0] < 4:
        statusline.setFontByNumber(1)

    # position and size the windows

    if zcode.memory.data[0] == 6:  # version 6
        for count, value in enumerate(zwindow):
            getWindow(count).setPosition(1, 1)
            getWindow(count).setSize(0,0)
        getWindow(0).setSize(ioScreen.getWidth(), ioScreen.getHeight())
        getWindow(1).setSize(ioScreen.getWidth(), 0)
    elif zcode.memory.data[0] < 4:  # version 1, 2 and 3
        getWindow(0).setSize(ioScreen.getWidth(), ioScreen.getHeight() - getWindow(0).getFont().getHeight())
        getWindow(0).setPosition(1, getWindow(0).getFont().getHeight() + 1)
        statusline.setSize(ioScreen.getWidth(), statusline.getFont().getHeight())
        statusline.setPosition(1, 1)
        if zcode.memory.data[0] == 3:  # version 3
            getWindow(1).setSize(ioScreen.getWidth(), 0)
            getWindow(1).setPosition(1, getWindow(1).getFont().getHeight() + 1)
    else:  # version 4, 5, 7 and 8
        getWindow(0).setSize(ioScreen.getWidth(), ioScreen.getHeight())
        getWindow(0).setPosition(1, 1)
        getWindow(1).setSize(ioScreen.getWidth(), 0)
        getWindow(1).setPosition(1, 1)

    # set the cursor in the windows

    if zcode.memory.data[0] == 6:
        for count, value in enumerate(zwindow):
            getWindow(count).setCursor(1, 1)
    elif zcode.memory.data[0] < 5:
        getWindow(0).setCursor(1, getWindow(0).y_size - getWindow(0).getFont().getHeight() + 1)
    else:
        getWindow(0).setCursor(1, 1)

    # set up window attributes

    if zcode.memory.data[0] == 6:
        for count, value in enumerate(zwindow):
            getWindow(count).setattributes(8, 0)
        getWindow(0).setattributes(15, 0)
    elif zcode.memory.data[0] < 4:
        getWindow(0).setattributes(15, 0)
        statusline.setattributes(0, 0)
        if zcode.memory.data[0] == 3:
            getWindow(1).setattributes(0, 0)
    else:
        getWindow(0).setattributes(15, 0)
        getWindow(1).setattributes(0, 0)

    # set other default window properties

    for count, value in enumerate(zwindow):
        getWindow(count).setRealColours(foreground, background)
        getWindow(count).font_size = (getWindow(count).getFont().getHeight() << 8) + getWindow(count).getFont().getWidth()
    if zcode.memory.data[0] < 4:
        statusline.setRealColours(background, foreground)
        statusline.font_size = (statusline.getFont().getHeight() << 8) + statusline.getFont().getWidth()

    # give the lower window in versions other than 6 a margin
    if zcode.memory.data[0] != 6:
        getWindow(0).left_margin = 5
        getWindow(0).right_margin = 5


def supportedgraphics(arg):  # should really tie this into the io module
    if arg == 0:  # colour
        return 1
    if arg == 1:  # true colour
        return 1
    if arg == 2:  # transparent background colour
        if zcode.memory.data[0] == 6:
            return 1
        return 0
    if arg == 3:  # picture displaying
        if zcode.memory.data[0] == 6:
            return 1
        return 0
    return 0


def supportedstyles(arg):
    # probably we should change this depending on the current font chosen? Font 3 has no bold or italic variations.
    if arg >= 0x10:  # we don't recognize any styles above 8
        return 0
    return 1  # all other styles and combinations are supported


# font 3 needs to be the same size as fixed width font

fixedpitchbit = False


def pix2units(pix, horizontal, coord=False):
    """converts a number of pixels into a number of z-machine units"""
    if graphics_mode == 1:
        return pix
    if not horizontal:
        value = ((pix - 1) // currentWindow.getFont().getHeight()) + 1
    else:
        value = ((pix - 1) // currentWindow.getFont().getWidth()) + 1
    return value


def units2pix(units, horizontal, coord=False):
    """converts a number of z-machine units into a number of pixels"""
    if graphics_mode == 1:
        return units
    if coord:
        units -= 1
    if not horizontal:
        value = units * currentWindow.getFont().getHeight()
    else:
        value = units * currentWindow.getFont().getWidth()
    if coord:
        value += 1
    return value


def chars2units(chars, horizontal, coord=False):
    """converts a height/width size in number of characters into a number of z-machine units"""

    if graphics_mode == 1:
        return chars
    if not horizontal:
        value = ((chars - 1) // currentWindow.getFont().getHeight()) + 1
    else:
        value = ((chars - 1) // currentWindow.getFont().getWidth()) + 1
    return value


def units2chars(units, horizontal, coord=False):
    """converts a number of z-machine units into a height/width size in number of characters"""
    if graphics_mode == 1:
        return units
    if coord:
        units -= 1
    if not horizontal:
        value = units * currentWindow.getFont().getHeight()
    else:
        value = units * currentWindow.getFont().getWidth()
    if coord:
        value += 1
    return value


class runeFont(io.font):
    def prerender(self, text):
        self.antialiase = 0
        # The version of font 3 used on the Mac has 6 characters for the 'bar filling up'
        # Other versions have 8 characters. This hack fixes the visual by changing
        # characters to the correct ones.
        if (zcode.header.TERP_NUMBER == zcode.header.TERP_MAC) and (settings.code in zcode.constants.beyond_zork_codes):
            text = text.replace('U', 'W')
            text = text.replace('T', 'V')
            text = text.replace('S', 'T')
            text = text.replace('R', 'S')
            text = text.replace('Q', 'R')
        return text


font3 = runeFont(io.getBaseDir() + "//fonts//bzork.ttf", name="Runic Font")

fontlist = [None,
            io.defaultFont,
            None,  # picture font. Unspecified, should always return 0
            font3,  # Beyond Zork font. Going to require some hacking.
            io.fixedFont
            ]


def specialfont3():
    for w in zwindow:
        w.fontlist[3] = io.fixedFont


def resize():
    if zcode.header.zversion != 6:
        getWindow(0).setSize(ioScreen.getWidth(), ioScreen.getHeight())
        getWindow(1).setSize(ioScreen.getWidth(), getWindow(1).getSize()[1])
    if zcode.memory.data[0] < 4:
        statusline.setSize(ioScreen.getWidth(), statusline.getSize()[1])

    # Screen height (lines)
    zcode.header.setscreenheightlines(ioScreen.getHeight() // getWindow(1).getFont().getHeight())
    # Screen width (chars)
    zcode.header.setscreenwidthchars(ioScreen.getWidth() // getWindow(1).getFont().getWidth())

    if zcode.memory.data[0] > 4:
        # Screen width (units)
        if zcode.memory.data[0] == 6:
            zcode.header.setscreenwidth(ioScreen.getWidth())
        else:
            zcode.header.setscreenwidth(ioScreen.getWidth() // getWindow(1).getFont().getWidth())
        # Screen height (units)
        if zcode.memory.data[0] == 6:
            zcode.header.setscreenheight(ioScreen.getHeight())
        else:
            zcode.header.setscreenheight(ioScreen.getHeight() // getWindow(1).getFont().getHeight())

    if zcode.memory.data[0] < 4:  # version 1, 2 and 3
        statusline.setSize(ioScreen.getWidth(), statusline.getFont().getHeight())

        if zcode.memory.data[0] == 3:  # version 3
            getWindow(1).setSize(ioScreen.getWidth(), getWindow(1).getSize()[1])
            getWindow(0).setSize(ioScreen.getWidth(), ioScreen.getHeight() - (statusline.getSize()[1] + getWindow(1).getSize()[1]))
        else:  # versions 1 and 2
            getWindow(0).setSize(ioScreen.getWidth(), ioScreen.getHeight() - statusline.getSize()[1])
    else:  # version 4, 5, 7 and 8
        getWindow(1).setSize(ioScreen.getWidth(), getWindow(1).getSize()[1])
        getWindow(0).setSize(ioScreen.getWidth(), ioScreen.getHeight() - getWindow(1).getSize()[1])

    if zcode.memory.data[0] == 6:
        zcode.header.setflag(2, 2, 1)


def getWindow(winnum):
    winnum = zcode.numbers.signed(winnum)
    if winnum == -3:
        return currentWindow
    return zwindow[winnum]


def updatestatusline():  # updates the status line for z-machine versions 1 to 3
    global currentWindow
    prevWindow = currentWindow
    currentWindow = statusline
    statusline.erase()
    if zcode.header.getflag(1, 1) == 1 and zcode.memory.data[0] == 3:
        type = 1
    else:
        type = 0
    statusline.setCursor(2 * statusline.getFont().getWidth() + 1, 1)
    location = zcode.objects.getShortName(zcode.game.getglobal(0))
    if location == 0:
        zcode.error.strictz('Tried to print short name of object 0')
    else:
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
    currentWindow = prevWindow


def printtext(text):
    currentWindow.printText(text)


mouse_window = 1

# Styles definitions

styles = { 'roman':   0,  # Selecting this style unselects all other styles.
           'bold':    1,  # This style should make the text bold, or otherwise emphasized.
           'italic':  2,  # This one should make it italic. Some interpreters make it underlined.
           'reverse': 4,  # Selecting this style reverses the text colours.
           'fixed':   8,  # One of three ways to get fixed-pitch text.
         }

# Colour definitions

colours = { 'black':   2,
            'red':     3,
            'green':   4,
            'yellow':  5,
            'blue':    6,
            'magenta': 7,
            'cyan':    8,
            'white':   9
          }

special_colours = { 'current': 0,
                    'default': 1
                  }
v6_colours = { 'under_cursor': -1,
               'light_grey':   10,
               'medium_grey':  11,
               'dark_grey':    12,
               'transparent':  15
             }


def checkcolours():
    """Returns 1 if colours are available, 0 if unavailable."""
    return io.checkcolour()


# colours

spectrum = {  2: 0x0000,  # Black
              3: 0x001D,  # Red
              4: 0x0340,  # Green
              5: 0x03BD,  # Yellow
              6: 0x59A0,  # Blue
              7: 0x7C1F,  # Magenta
              8: 0x77A0,  # Cyan
              9: 0x7FFF,  # White
             10: 0x5AD6,  # Light Grey
             11: 0x4631,  # Medium Grey
             12: 0x2D6B,  # Dark Grey
             15: -4       # Transparent
           }

last_spectrum_colour = 0


def convertBasicToRealColour(basic_colour):
    true_colour = convertBasicToTrueColour(basic_colour)
    if true_colour != None:
        return convertTrueToRealColour(true_colour)
    return None


def convertRealToBasicColour(real_colour):
    true_colour = convertRealToTrueColour(real_colour)
    basic_colour = convertTrueToBasicColour(true_colour)
    return basic_colour


def convertBasicToTrueColour(basic_colour):
    if basic_colour in spectrum:
        return spectrum[basic_colour]
    else:
        return None


def convertTrueToBasicColour(true_colour):
    global last_spectrum_colour
    global spectrum
    highest_spectrum = 0
    for a in spectrum:
        if spectrum[a] == true_colour:
            return a

    if last_spectrum_colour == 0 or last_spectrum_colour == 255:
        last_spectrum_colour = 16
    else:
        last_spectrum_colour += 1
    spectrum[last_spectrum_colour] = true_colour
    return last_spectrum_colour


def convertTrueToRealColour(true_colour):
    if true_colour == -4:
        return (0, 0, 0, 0)  # transparent
    b = true_colour >> 10
    g = (true_colour >> 5) & 31
    r = true_colour & 31
    r = (r << 3) | (r >> 2)
    b = (b << 3) | (b >> 2)
    g = (g << 3) | (g >> 2)
    a = 0xff  # alpha = fully opaque
    real_colour = (r, g, b, a)
    return real_colour


def convertRealToTrueColour(colour):
    if colour[3] == 0:
        return -4
    r = colour[0] // 8
    g = colour[1] // 8
    b = colour[2] // 8
    c = (((b << 5) + g) << 5) + r
    return c


# windows

class window(io.window):
    def __str__(self):
        return 'window ' + str(self.window_id)

    # window properties (window coordinates are measured from 1,1)
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

    # styles
    reverse = False
    bold = False
    italic = False
    fixed = False

    def __init__(self, screen, font):
        self.screen = screen
        self.fontlist = fontlist[:]
        self.setFont(font)
        foreground = convertBasicToRealColour(2)
        background = convertBasicToRealColour(9)
        self.setRealColours(foreground, background)
        self.getFont().resetSize()

    def preFlush(self):
        self.font = self.getFont()
        self.font.setReverse(self.reverse)
        self.font.setBold(self.bold)
        self.font.setItalic(self.italic)

    def testfont(self, font):
        """Checks to see if the givenfont is available for use. Returns 1 if available, 0 if unavailable."""
        if font > len(self.fontlist) - 1:
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
        if (fixedpitchbit or self.fixed) and self.font_number == 1:
            return self.fontlist[4]
        return self.fontlist[self.font_number]

    def resetfontsize(self):
        s = self.old_relative_font_size - self.relative_font_size
        self.setfontsize(s)

    def atMargin(self):
        """Checks to see if the cursor is at the left margin"""
        if self.getCursor()[0] == self.left_margin + 1:
            return True
        else:
            return False

    def setBasicColours(self, foreground, background):
        self.basic_foreground_colour = foreground
        self.basic_background_colour = background

    def getBasicColours(self):
        return (self.basic_foreground_colour, self.basic_background_colour)

    def setTrueColours(self, foreground, background):
        basic_foreground = convertTrueToBasicColour(foreground)
        basic_background = convertTrueToBasicColour(background)
        self.true_foreground_colour = foreground
        self.true_background_colour = background
        self.setBasicColours(basic_foreground, basic_background)

    def getTrueColours(self):
        return (self.true_foreground_colour, self.true_background_colour)

    def setRealColours(self, foreground, background):
        true_foreground = convertRealToTrueColour(foreground)
        true_background = convertRealToTrueColour(background)
        self.setTrueColours(true_foreground, true_background)
        self.setColours(foreground, background)

    def setMargins(self, left, right):
        self.left_margin = left
        self.right_margin = right
        self.setCursorToMargin()

    def setStyle(self, style):
        self.flushTextBuffer()
        if style == 0:
            self.reverse = False
            self.bold = False
            self.italic = False
            self.fixed = False
        else:
            if style & 1:
                self.reverse = True
            if style & 2:
                self.bold = True
            if style & 4:
                self.italic = True
            if style & 8:
                self.fixed = True

    def getStyle(self):
        s = 0
        if self.reverse:
            s += 1
        if self.bold:
            s += 2
        if self.italic:
            s += 4
        if self.fixed:
            s += 8
        return s

    def setPosition(self, x, y):
        self.x_coord = x
        self.y_coord = y

    def getPosition(self):
        return (self.x_coord, self.y_coord)

    def getCursor(self):
        return (self.x_cursor, self.y_cursor)

    def setCursorToMargin(self):  # makes sure the cursor is inside the margins
        if (self.getCursor()[0] <= self.left_margin) or (self.getCursor()[0] >= (self.getSize()[0] - self.right_margin)):
            self.setCursor(self.left_margin + 1, self.getCursor()[1])

    def setprops(self, zproperty, value):
        """General purpose routine to set the value of a window property by property number. Generally not used."""
        if zproperty == 0:
            self.setPosition(self.getPosition()[0], value)
        elif zproperty == 1:
            self.setPosition(value, self.getPosition()[1])
        elif zproperty == 2:
            self.setSize(self.getSize()[0], value)
        elif zproperty == 3:
            self.setSize(value, self.getSize()[1])
        elif zproperty == 4:
            self.setCursor(self.getCursor()[0], value)
        elif zproperty == 5:
            self.setCursor(value, self.getCursor()[1])
        elif zproperty == 6:
            self.left_margin = value
        elif zproperty == 7:
            self.right_margin = value
        elif zproperty == 8:
            self.newline_routine = value
        elif zproperty == 9:
            self.interrupt_countdown = value
        elif zproperty == 10:
            self.setStyle(value)
        elif zproperty == 11:
            fg = convertBasicToRealColour(value & 255)
            bg = convertBasicToRealColour(value >> 8)
            self.setRealColours(fg, bg)
        elif zproperty == 12:
            self.setFontByNumber(value)
        elif zproperty == 13:
            pass
        elif zproperty == 14:
            self.attributes = value
        elif zproperty == 15:
            self.line_count = value
        elif zproperty == 16:
            pass
        elif zproperty == 17:
            pass
        elif zproperty == 18:
            pass
        else:
            return False

    def getprops(self, zproperty):
        """General purpose routine to retrieve the value of a window property, by property number. Also generally not used."""
        if zproperty == 0:
            return self.getPosition()[1]
        elif zproperty == 1:
            return self.getPosition()[0]
        elif zproperty == 2:
            return self.getSize()[1]
        elif zproperty == 3:
            return self.getSize()[0]
        elif zproperty == 4:
            return self.getCursor()[1]
        elif zproperty == 5:
            return self.getCursor()[0]
        elif zproperty == 6:
            return self.left_margin
        elif zproperty == 7:
            return self.right_margin
        elif zproperty == 8:
            return self.newline_routine
        elif zproperty == 9:
            return self.interrupt_countdown
        elif zproperty == 10:
            return self.getStyle()
        elif zproperty == 11:
            fg, bg = self.getBasicColours()
            return (bg << 8) + fg
        elif zproperty == 12:
            return self.font_number
        elif zproperty == 13:
            return self.font_size
        elif zproperty == 14:
            return self.attributes
        elif zproperty == 15:
            return self.line_count
        elif zproperty == 16:
            return self.true_foreground_colour
        elif zproperty == 17:
            return self.true_background_colour
        elif zproperty == 18:
            return self.font_metrics
        else:
            return False

    # functions to retrieve more meaningful info from properties

    def setattributes(self, flags, operation):
        if operation == 0:  # set attributes to match flags exactly
            self.attributes = flags
        elif operation == 1:  # set attributes in flags, leave others as is
            self.attributes = self.attributes | flags
        elif operation == 2:  # unset attributes in flags, leave others as is
            self.attributes = self.attributes & (flags ^ 15)
        elif operation == 3:  # reverse attributes set in flags, leave others
            self.attributes = self.attributes ^ flags

    def testattribute(self, attribute):
        result = self.attributes & attribute
        if result == attribute:
            return True
        else:
            return False

    textbuffer = ''
    linetextbuffer = []
    stylebuffer = []
    linestylebuffer = []

    def updatestylebuffer(self):
        pass

    def alterTabs(self):  # changes the tab character to various spaces
        x = list(self.textbuffer)
        if len(x) > 0 and x[0] == '\t' and self.atMargin():
            x[0] = '   '
        self.textbuffer = ''.join(x)
        self.textbuffer = self.textbuffer.replace('\t', ' ')

    maxfontheight = 0

    def preNewline(self):
        # call the interrupt routine (if it's time to do so)
        if zcode.header.getterpnum() != 6 or data.getcode(zcode.memory.originaldata) != '393.890714':
            self.cdown = self.countdown()

    def postNewline(self):
        if zcode.header.getterpnum() == 6 and data.getcode(zcode.memory.originaldata) == '393.890714':
            self.cdown = self.countdown()

    def newline(self):
        self.preNewline()
        # move to the new line
        self.setCursor(self.getCursor()[0], self.getCursor()[1] + self.getFont().getHeight())
        if self.getCursor()[1] >= self.getSize()[1] - self.getFont().getHeight():
            if self.testattribute(2):
                self.scroll(self.getFont().getHeight())  # scroll the window region up
                self.setCursor(self.getCursor()[0], self.getCursor()[1] - self.getFont().getHeight())
        if self.line_count != -999 and zcode.header.getscreenheightlines() != 255:
            self.line_count += 1

        # put the cursor at the current left margin
        self.setCursor(self.left_margin + 1, self.getCursor()[1])
        if self.line_count >= (self.getSize()[1] // self.getFont().getHeight()) - 1 and self.testattribute(2):
            self.line_count = 0
            pfont = self.setFontByNumber(4)
            morestring = '[MORE]'
            self.drawText(morestring)
            self.setFontByNumber(pfont)

            while zcode.input.getInput(ignore=True) != 32:
                pass
            x = self.getCursor()[0]  # + self.getPosition()[0] - 1
            y = self.getCursor()[1]  # + self.getPosition()[1] - 1
            w = zcode.screen.currentWindow.getStringLength(morestring)
            h = zcode.screen.currentWindow.getStringHeight(morestring)
            zcode.screen.currentWindow.eraseArea(x, y, w, h)
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
        charwidth = self.getStringLength(char)
        charheight = self.getStringHeight(char)
        self.setCursor(self.getCursor()[0] - charwidth, self.getCursor()[1])
        area = ((self.getPosition()[0] + self.getCursor()[0] - 1), (self.getPosition()[1] + self.getCursor()[1] - 1), charwidth, charheight)
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

    def getFontNumber(self):
        """Returns the number of the current font."""
        return self.font_number

    def getpic(self, picture_number):
        return io.getpic(ioScreen, picture_number)

    def drawpic(self, picture_number, x, y):
        pic = self.getpic(picture_number)
        if pic:
            pic.draw(self, (self.getPosition()[0] + x - 1), (self.getPosition()[1] + y - 1))

    def erasepic(self, picture_data, x, y, scale=1):
        pic = io.image(picture_data)
        newwidth = pic.getWidth() * scale
        newheight = pic.getHeight() * scale

        if self.getColours()[1] != -4:
            area = ((self.getPosition()[0] + x - 1), (self.getPosition()[1] + y - 1), newwidth, newheight)
            ioScreen.erase(self.getColours()[1], area)

    def eraseline(self, length):
        if self.getColours()[1] != -4:
            ioScreen.erase(self.getColours()[1], (self.getPosition()[0] + self.getCursor()[0] - 1, self.getPosition()[1] + self.getCursor()[1] - 1, length, self.getFont().getHeight()))

    fontlist = []


def eraseWindow(winnum):
    if zcode.numbers.signed(winnum) < 0 and currentWindow.getColours()[1][3] == 0:
        pass
    elif zcode.numbers.signed(winnum) == -1:  # this should unsplit the screen, too. And move the cursor.
        ioScreen.erase(currentWindow.getColours()[1])
        split(0)
        for count, value in enumerate(zwindow):
            getWindow(count).setCursor(1, 1)
            getWindow(count).line_count = 0
    elif zcode.numbers.signed(winnum) == -2:  # doesn't unsplit the screen, doesn't move the cursor
        ioScreen.erase(currentWindow.getColours()[1])
    elif getWindow(winnum).getColours()[1][3] != 0:
        getWindow(winnum).erase()
        if zcode.memory.data[0] < 5 and winnum == 0:
            getWindow(0).setCursor(getWindow(0).getCursor()[0], getWindow(0).getSize()[1] - getWindow(0).getFont().getHeight())


def split(size):
    oldycoord = getWindow(0).getPosition()[1]

    getWindow(0).setPosition(1, size + 1)
    getWindow(0).setSize(getWindow(0).getSize()[0], ioScreen.getHeight() - size)

    getWindow(1).setPosition(1, 1)
    getWindow(1).setSize(getWindow(1).getSize()[0], size)

    if zcode.memory.data[0] == 3:
        eraseWindow(1)

    # move the window's cursor to the same absolute position it was in before the split

    difference = getWindow(0).getPosition()[1] - oldycoord
    getWindow(0).setCursor(getWindow(0).getCursor()[0], getWindow(0).getCursor()[1] - difference)

    # if the cursor now lies outside the window, move it to the window origin

    for a in (0, 1):
        if (getWindow(a).getCursor()[1] > getWindow(a).getSize()[1]) or (getWindow(a).getCursor()[1] < 1):
            getWindow(a).setCursor(1, 1)
