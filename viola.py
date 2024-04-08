#!/usr/bin/env python

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

import vio.zcode as io
import sys
import getopt
import settings
import zcode
import blorb
import babel
from zcode.constants import specs

blorbs = []
height = None
width = None
title = None
terpnum = None


def checkgamefile(gamefile):
    gamefile.seek(0)
    gameid = gamefile.read(4)
    if gameid.decode('latin-1') == 'FORM':  # The file is an IFF FORM file
        gamefile.seek(8)
        if gamefile.read(4).decode('latin-1') == 'IFRS':  # The file is a Blorb resource file
            return 'blorb'
        else:
            return 'unknown'
    elif gameid.decode('latin-1') == 'GLUL':
        return 'glulx'
    elif 1 <= gameid[0] <= 8:
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
    f = io.findfile(filename, gamefile=True)
    if f == False:
        print("Error opening game file", file=sys.stderr)
        sys.exit()
    try:
        gamefile = open(f, 'rb')
    except:
        print("Error opening game file", file=sys.stderr)
        sys.exit()

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


def handle_parameters(argv):  # handles command line parameters
    global blorbfiles
    global height, width, title, transcriptfile, usespec, recordfile, playbackfile
    # viola [options] gamefile [resourcefile]
    if len(argv) <= 1:
        print('Syntax: viola [options] game-file [resource-file]\n'
              '  -d  print debug messages\n'
              '  -w <pixels>  screen width\n'
              '  -h <pixels>  screen height\n'
              '  -T <filename>  output transcript file\n'
              '  -t <period>  milliseconds between timer calls (default 100)\n'
              '  -R <filename>  record input commands to file\n'
              '  -P <filename>  playback input commands from file\n'
              '  -B  force blorb file to work even if it does not match the game'
              )
        sys.exit()

    if len(argv) <= 1:
        return None

    args = getopt.getopt(argv[1:], 'Bdh:w:T:t:R:P:', 'zspec=')

    options = args[0]
    args = args[1]
    transcriptfile = False
    recordfile = False
    playbackfile = False
    usespec = 3

    for a in options:
        if a[0] == '-d':
            zcode.debug = True
        elif a[0] == '-h':
            height = int(a[1])
        elif a[0] == '-w':
            width = int(a[1])
        elif a[0] == '-T':
            transcriptfile = a[1]
        elif a[0] == '-t':
            io.timer_period = int(a[1])
        elif a[0] == '-R':
            recordfile = a[1]
        elif a[0] == '-P':
            playbackfile = a[1]
        elif a[0] == '-B':
            blorb.forceblorb = True
        elif a[0] == '--zspec':
            specversion = a[1]
            if specversion not in specs:
                print("The specification selected must be one of:")
                for a in specs:
                    print(a)
                sys.exit()
            usespec = specs.index(specversion)

    if playbackfile and recordfile:
        print('Cannot record commands and playback commands at the same time (-P and -R).')
        sys.exit()

    gamedata = getgame(args[0])
    for a in range(len(args[1:])):
        blorbs.append(blorb.Blorb(args[1:][a], gamedata))

    return gamedata


def setupmodules(gamefile):
    global terpnum, title, transcriptfile

    realForeground = zcode.screen.convertBasicToRealColour(foreground)
    realBackground = zcode.screen.convertBasicToRealColour(background)

    io.setup(width, height, blorbs, title, realForeground, realBackground)
    zcode.use_standard = usespec
    if not zcode.memory.setup(gamefile):
        return False

    # set up the various modules
    zcode.game.setup()
    zcode.routines.setup()
    zcode.screen.setup()
    zcode.input.setup(playbackfile)
    zcode.output.setup((False, True, transcriptfile, False, recordfile))
    zcode.optables.setup()
    zcode.sounds.setup(blorbs)
    zcode.header.setup()
    zcode.objects.setup()
    zcode.text.setup()
    if terpnum is not None:
        zcode.header.setterpnum(int(terpnum))

    return True


def rungame(gamedata):
    global height, width, title, terpnum, foreground, background
    settings.setup(gamedata)
    defset = settings.getsettings(settings.getdefaults())
    gameset = settings.getsettings(settings.findgame())

    for a in range(len(gameset)):
        if gameset[a] == None:
            gameset[a] = defset[a]

    if height is None:
        height = gameset[2]
    if width is None:
        width = gameset[1]

    try:
        foreground = zcode.screen.basic_colours[gameset[5]]
    except:
        foreground = 2

    try:
        background = zcode.screen.basic_colours[gameset[6]]
    except:
        background = 9

    if gameset[3] is not None:
        blorbs.append(io.findfile(gameset[3]))

    for a in range(len(blorbs)):
        if not blorbs[a]:
            blorbs.pop(a)

    bwidth = 0
    bheight = 0
    for a in blorbs:
        try:
            bwidth, bheight = a.getWinSizes()[:2]
        except:
            pass

    if bwidth == 0:
        wrat = 1
        bwidth = width
    else:
        wrat = width / bwidth
    if bheight == 0:
        hrat = 1
        bheight = height
    else:
        hrat = height / bheight

    if wrat < hrat:
        rat = wrat
    else:
        rat = hrat
    try:
        width = round(bwidth * rat)
    except:
        width = 1024
    try:
        height = round(bheight * rat)
    except:
        height = 768

    terpnum = gameset[4]

    if title is None:
        title = gameset[0]

    if title is None:
        for a in blorbs:
            iFiction = a.getmetadata()
            if iFiction:
                title = babel.gettitle(iFiction)
                headline = babel.getheadline(iFiction)
                author = babel.getauthor(iFiction)
                if title is None:
                    title = ''
                if headline is not None:
                    title = title + ' (' + headline + ')'
                if author is not None:
                    title += ' by ' + author

    if title == '' or title is None:
        title = 'Viola'
    else:
        title = 'Viola - ' + title

    if not setupmodules(gamedata):
        zcode.error.fatal('Couldn\'t open gamefile ' + sys.argv[1])

    zcode.routines.execstart()
    return 1


if __name__ == '__main__':
    gamedata = handle_parameters(sys.argv)

    if zcode.profile:
        import cProfile
        import pstats

        with cProfile.Profile() as pr:
            rungame(gamedata)

        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.dump_stats(filename='viola.prof')
    else:
        rungame(gamedata)
