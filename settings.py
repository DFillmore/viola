# Copyright (C) 2004 - 2019 David Fillmore
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

# reads settings from the .violarc file

import re
import os

locations = ["$HOME", "$USERPROFILE"]


def getcode(gamedata):
    release = (gamedata[2] << 8) + gamedata[3]
    serial = gamedata[0x12:0x18].decode('latin-1')
    return str(release) + '.' + serial


def findgame():
    c = re.escape(code)
    expr = r"code:[\s\w.]*" + c + ".*?(?=code:|\Z)"
    r = re.compile(expr, re.M | re.S)
    match = r.search(filetext)
    if match == None:
        return None
    return match.string[match.start():match.end()]


def getdefaults():
    expr = r".*?(?=code:|\Z)"
    r = re.compile(expr, re.M | re.S)
    match = r.search(filetext)
    return match.string[match.start():match.end()]


def gettitle(gamesettings):
    expr = r"title:.*?$"
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match == None:
        return None
    else:
        return match.string[match.start() + 6:match.end()].strip()


def getheadline(gamesettings):
    expr = r"headline:.*?$"
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match is None:
        return None
    else:
        return match.string[match.start() + 6:match.end()].strip()


def getauthor(gamesettings):
    expr = r"author:.*?$"
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match is None:
        return None
    else:
        return match.string[match.start() + 6:match.end()].strip()

def getblorb(gamesettings):
    expr = r"blorb:.*?$"
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match == None:
        return None
    else:
        return match.string[match.start() + 6:match.end()].strip()


def getheight(gamesettings):
    expr = r"height:.*?$"
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match == None:
        return None
    else:
        return int(match.string[match.start() + 7:match.end()].strip())


def getwidth(gamesettings):
    expr = r"width:.*?$"
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match == None:
        return None
    else:
        return int(match.string[match.start() + 6:match.end()].strip())


def getterpnum(gamesettings):
    expr = r"terpnum:.*?$"
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match == None:
        return None
    else:
        return match.string[match.start() + 8:match.end()].strip()


def getforeground(gamesettings):
    expr = r"foreground:.*?$"
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match == None:
        return None
    else:
        return match.string[match.start() + 11:match.end()].strip()


def getbackground(gamesettings):
    expr = r"background:.*?$"
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match == None:
        return None
    else:
        return match.string[match.start() + 11:match.end()].strip()


class gameset:
    title = None
    width = None
    height = None
    blorb = None
    terp_number = None
    foreground = None
    background = None
    headline = None
    author = None


    def __init__(self, *, width=None, height=None, blorb=None, terp_number=None,
                 foreground=None, background=None, title=None, headline=None, author=None):
        self.width=width
        self.height=height
        self.blorb=blorb
        self.terp_number = terp_number
        self.foreground = foreground
        self.background = background
        self.title = title
        self.headline = headline
        self.author = author


def getsettings(gamesettings, backup: gameset = None):
    if gamesettings is None:
        set = gameset(width=None, height=None, blorb=None, terp_number=None,
                      foreground=None, background=None, headline=None, author=None)
    else:
        set = gameset(title=gettitle(gamesettings),
                      headline=getheadline(gamesettings),
                      author=getauthor(gamesettings),
                      width=getwidth(gamesettings),
                      height=getheight(gamesettings),
                      blorb=getblorb(gamesettings),
                      terp_number=getterpnum(gamesettings),
                      foreground=getforeground(gamesettings),
                      background=getbackground(gamesettings)
                     )
    if backup:
        if not set.title:
            set.title = backup.title
        if not set.headline:
            set.headline = backup.title
        if not set.author:
            set.author = backup.author
        if not set.width:
            set.width = backup.width
        if not set.height:
            set.height = backup.height
        if not set.blorb:
            set.blorb = backup.blorb
        if not set.terp_number:
            set.terp_number = backup.terp_number
        if not set.foreground:
            set.foreground = backup.foreground
        if not set.background:
            set.background = backup.background
    return set


def setup(gamedata):
    global file, filesize, filetext, code, defaults, gamesettings

    filename: str | None = None
    for l in locations:
        filename = os.path.join(os.path.expandvars(l), ".violarc")
        if os.path.exists(filename) == 1:
            break

    if filename == None:
        filetext = ''
    else:
        file = open(filename, "r")
        filesize = os.stat(filename).st_size
        filetext = file.read(filesize)
        file.close()

    code = getcode(gamedata)
