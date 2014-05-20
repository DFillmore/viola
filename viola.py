#!/usr/bin/python
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


import zio.pygame as io
import sys
import getopt
import os
import settings
import zcode
import blorb
import babel

blorbs = []
height = None
width = None
title = None
terpnum = None
debug = False


def checkgamefile(gamefile):
    gamefile.seek(0)
    id = gamefile.read(4)
    if id.decode('latin-1') == 'FORM': # The file is an IFF FORM file
        gamefile.seek(8)
        if gamefile.read(4).decode('latin-1') == 'IFRS': # The file is a Blorb resource file
            return 'blorb'
        else:
            return 'unknown'
    elif id.decode('latin-1') == 'GLUL':
        return 'glulx'
    elif id[0] >= 1 and id[0] <= 8:
        return 'zcode'
    else:
        return 'unknown'

class UnknownGameType(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class UnsupportedGameType(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def getgame(filename):
    global blorbs
    f = io.findfile(filename)
    if f == False:
        print("Error opening game file", file=sys.stderr)
        sys.exit()
    try:
        gamefile = open(f, 'rb')
    except:
        print("Error opening game file", file=sys.stderr)
        sys.exit()
    x = gamefile.read()
    gamefile.seek(0)

        
    # check to see if it's actually a blorb file

    gametype = checkgamefile(gamefile)
    gamefile.seek(0)
    if gametype == 'blorb':
        blorbs = [blorb.Blorb(filename)]
        game = blorbs[0].getExec(0)
    elif gametype == 'unknown':
        raise UnknownGameType("Viola does not recognise the format of the game file.")
    else:
        game = gamefile.read()

    if game[:4] == 'GLUL':
        raise UnsupportedGameType("Viola does not support Glulx games at this time.")

    return game

specs = ['0', '0.2', '1.0', '1.1', '1.2']

def handle_parameters(argv): # handles command line parameters
    global blorbfiles
    global height, width, title, transcriptfile, usespec
    global debug
    # viola [options] gamefile [resourcefile]
    if len(argv) <= 1:
        print('Syntax: viola [options] game-file [resource-file]\n  -d debug messages\n  -w <pixels> screen width\n  -h <pixels> screen height\n  -T <filename> output transcript file')
        sys.exit()

    if len(argv) <= 1:
        return None
    
    args = getopt.getopt(argv[1:], 'dh:w:T:', 'spec=')
    options = args[0]
    args = args[1]
    transcriptfile = False
    usespec = 3
    for a in options:
        if a[0] == '-d':
            debug = True
        elif a[0] == '-h':
            height = int(a[1])
        elif a[0] == '-w':
            width = int(a[1])
        elif a[0] == '-T':
            transcriptfile = a[1]
        elif a[0] == '--spec':
            specversion = a[1]
            if specversion not in specs:
                print("The spec selected must be one of:")
                for a in specs:
                    print(a)
                sys.exit()
            usespec = specs.index(specversion)
    


    gamedata = getgame(args[0])
    for a in range(len(args[1:])):
        blorbs.append(blorb.Blorb(args[1:][a], gamedata))

    return gamedata

def setupmodules(gamefile):
    global terpnum, title, transcriptfile
    io.setup()
    zcode.use_standard = usespec
    if zcode.memory.setup(gamefile) == False:
        return False

    
    # set up the various modules
    zcode.game.setup()
    zcode.routines.setup()
    zcode.screen.setup(blorbs, width, height, title=title)
    zcode.input.setup()
    zcode.output.setup([False, True, transcriptfile])

    zcode.objects.setup()
    

    zcode.optables.setup()
    zcode.sounds.setup(blorbs)
    zcode.header.setup()
    zcode.text.setup()
    if terpnum != None:
        zcode.header.setterpnum(int(terpnum))

    return True

def rungame(gamedata):
    global height, width, title, terpnum
    settings.setup(gamedata)
    defset = settings.getsettings(settings.getdefaults())
    gameset = settings.getsettings(settings.findgame())
        
    for a in range(len(gameset)):
        if gameset[a] == None:
            gameset[a] = defset[a]
    
    if height == None:
        height = gameset[2]
    if width == None:
        width = gameset[1]
    
    if gameset[3] != None:
        blorbs.append(io.findfile(gameset[3]))

    for a in range(len(blorbs)):
        if blorbs[a] == False:
            blorbs.pop(a)

        
    terpnum = gameset[4]

    if title == None:
        title = gameset[0]
    icon = None
    if title == None:
        for a in blorbs:
            iFiction = a.getmetadata()
            if iFiction:
                title = babel.gettitle(iFiction)
                headline = babel.getheadline(iFiction)
                author = babel.getauthor(iFiction)
                if headline != None:
                    title = title + ': ' + headline
                if author != None:
                    title += ' by ' + author
                if title == None:
                    title = ''
                else:
                    title = ' - ' + title

    if title == None:
        title = 'Viola'
    else:
        title = 'Viola - ' + title

    if setupmodules(gamedata) == False:
        zcode.error.fatal('Couldn\'t open gamefile ' + sys.argv[1])  
       


    for a in blorbs:
        icon = a.gettitlepic()
    if icon:
        io.setIcon(icon)
    


    zcode.routines.execstart(debug)
    return 1

gamedata = handle_parameters(sys.argv)
rungame(gamedata)