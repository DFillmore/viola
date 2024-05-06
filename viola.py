#!/usr/bin/env python

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

from __future__ import annotations

import data
import vio.zcode as io
import sys
import getopt
import settings
import zcode
from ififf import blorb
from ififf import babel
from zcode.constants import specs

blorbs = []
height = None
width = None
title = None
terpnum: None | int = None
gamecode = None

# priority of settings: command line > game-specific settings > data from ifdb > default settings > viola defaults

command_settings = settings.gameset(priority=4)
ifdb_settings = settings.gameset(priority=2)
base_settings = settings.gameset(width=1024,
                                 height=768,
                                 terp_number=zcode.header.TERP_IBM,
                                 foreground='black',
                                 background='white'
                                )


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
    if not f:
        print("Error opening game file", file=sys.stderr)
        sys.exit()
    gamefile = open(f, 'rb')
    gamefile.seek(0)

    # check to see if it's actually a blorb file

    gametype = checkgamefile(gamefile)
    gamefile.seek(0)
    if gametype == 'blorb':
        blorbs = [blorb.blorb(blorb.blorb_chunk(gamefile.read()))]
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
    global height, width, title, transcriptfile, usespec, recordfile, playbackfile, gamecode
    global command_settings, ifdb_settings
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
              '  -B  force blorb file to work even if it does not match the game\n'
              '  -D  download game information (title and author)'
              )
        sys.exit()

    if len(argv) <= 1:
        return None

    args = getopt.getopt(argv[1:], 'BdDh:w:T:t:R:P:', ['zspec='])

    options = args[0]
    args = args[1]
    transcriptfile = False
    recordfile = False
    playbackfile = False
    usespec = 3
    datagrab: bool = False

    for a in options:
        if a[0] == '-d':
            zcode.debug = True
        elif a[0] == '-h':
            command_settings.height = int(a[1])
        elif a[0] == '-w':
            command_settings.width = int(a[1])
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
        elif a[0] == '-D':
            datagrab = True

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
    gamecode = data.getcode(gamedata)
    if datagrab:
        ifid = data.getifid(gamedata)
        ifdb_page = data.getpage(ifid)
        if ifdb_page:
            command_settings.title = data.gettitle(ifdb_page)
            command_settings.author = data.getauthor(ifdb_page)

    for a in args[1:]:
        f = open(a, 'rb')
        blorb_data = f.read()
        f.close()
        blorbs.append(blorb.blorb(blorb.blorb_chunk(blorb_data)))

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
    zcode.text.setup(gamecode)
    if terpnum is not None:
        zcode.header.setterpnum(int(terpnum))

    return True


def rungame(gamedata):
    global height, width, title, terpnum, foreground, background
    settings.setup()
    defset = settings.getsettings()
    gameset = settings.getsettings(data.getcode(gamedata))
    if not gameset:
        gameset = settings.getsettings(data.getifid(gamedata))

    gameset = gameset.merge(defset)
    gameset = gameset.merge(ifdb_settings)
    gameset = gameset.merge(command_settings)
    gameset = gameset.merge(base_settings)

    height = gameset.height
    width = gameset.width

    if gameset.foreground and gameset.foreground.lower() in zcode.screen.colours:
        foreground = zcode.screen.colours[gameset.foreground.lower()]
    else:
        try:
            foreground = int(gameset.foreground)
        except TypeError:
            foreground = 2

    if gameset.background and gameset.background.lower() in zcode.screen.colours:
        background = zcode.screen.colours[gameset.background.lower()]
    else:
        try:
            background = int(gameset.background)
        except TypeError:
            background = 9

    if gameset.blorb is not None:
        blorbs.append(io.findfile(gameset.blorb))

    for a in range(len(blorbs)):
        if not blorbs[a]:
            blorbs.pop(a)

    bwidth = 0
    bheight = 0
    for a in blorbs:
        bwidth, bheight = a.getWinSizes()[:2]

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

    width = round(bwidth * rat)
    height = round(bheight * rat)

    terpnum = gameset.terp_number

    # title, headline and author in settings file take precedence over information from blorb metadata

    try:
        iFiction = blorbs[0].getMetaData()
    except IndexError:
        iFiction = None

    if iFiction:
        blorb_settings = settings.gameset(priority=gameset.priority-1, title=babel.getTitle(iFiction),
                                          author=babel.getAuthor(iFiction), headline=babel.getHeadline(iFiction)
                                         )
        gameset = gameset.merge(blorb_settings)

    title = gameset.title
    headline = gameset.headline
    author = gameset.author

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
