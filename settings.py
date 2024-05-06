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

from __future__ import annotations

import copy
import re
import os
import data

locations = ["$HOME", "$USERPROFILE"]

base_expression = r"(\\#|.)*?(?=$|#)"


def findgame(gamecode):
    expr = r"(?:code: | ifid:)[\s\w.]*" + gamecode + r"(?:.|\n)*?(?=code:|ifid:|\Z)"
    r = re.compile(expr, re.M | re.S)
    match = r.search(filetext)
    if match is None:
        return None
    return match.string[match.start():match.end()]


def getdefaults():
    expr = r"(?:.*?(\n|\Z))*?(?=code:|ifid:|\Z)"
    r = re.compile(expr, re.M | re.S)
    match = r.search(filetext)
    return match.string[match.start():match.end()]


def gettitle(gamesettings):
    expr = r"title:" + base_expression
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match is None:
        return None
    else:
        return match.string[match.start() + 6:match.end()].strip()


def getheadline(gamesettings):
    expr = r"headline:" + base_expression
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match is None:
        return None
    else:
        return match.string[match.start() + 6:match.end()].strip()


def getauthor(gamesettings):
    expr = r"author:" + base_expression
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match is None:
        return None
    else:
        return match.string[match.start() + 6:match.end()].strip()


def getblorb(gamesettings):
    expr = r"blorb:" + base_expression
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match is None:
        return None
    else:
        return match.string[match.start() + 6:match.end()].strip()


def getheight(gamesettings):
    expr = r"height:" + base_expression
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match is None:
        return None
    else:
        return int(match.string[match.start() + 7:match.end()].strip())


def getwidth(gamesettings):
    expr = r"width:" + base_expression
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match is None:
        return None
    else:
        return int(match.string[match.start() + 6:match.end()].strip())


def getterpnum(gamesettings):
    expr = r"terpnum:" + base_expression
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match is None:
        return None
    else:
        return match.string[match.start() + 8:match.end()].strip()


def getforeground(gamesettings):
    expr = r"foreground:" + base_expression
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match is None:
        return None
    else:
        return match.string[match.start() + 11:match.end()].strip()


def getbackground(gamesettings):
    expr = r"background:" + base_expression
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match is None:
        return None
    else:
        return match.string[match.start() + 11:match.end()].strip()


# priority of settings: command line > game-specific settings > data from ifdb > default settings > viola defaults

class gameset:
    priority = 0
    title = None
    width = None
    height = None
    blorb = None
    terp_number = None
    foreground = None
    background = None
    headline = None
    author = None

    def __init__(self, *, priority=0, width=None, height=None, blorb=None, terp_number=None,
                 foreground=None, background=None, title=None, headline=None, author=None):
        self.priority = priority
        self.width = width
        self.height = height
        self.blorb = blorb
        self.terp_number = terp_number
        self.foreground = foreground
        self.background = background
        self.title = title
        self.headline = headline
        self.author = author

    def merge(self, gset: gameset) -> gameset:
        setA = copy.deepcopy(self)
        setB = copy.deepcopy(gset)
        if self.priority < gset.priority:
            setA = copy.deepcopy(gset)
            setB = copy.deepcopy(self)

        if setA.width:
            setB.width = setA.width
        if setA.height:
            setB.height = setA.height
        if setA.blorb:
            setB.blorb = setA.blorb
        if setA.terp_number:
            setB.terp_number = setA.terp_number
        if setA.foreground:
            setB.foreground = setA.foreground
        if setA.background:
            setB.background = setA.background
        if setA.title:
            setB.title = setA.title
        if setA.headline:
            setB.headline = setA.headline
        if setA.author:
            setB.author = setA.author

        return setB


def getsettings(gamecode=None):
    if not gamecode:
        gamesettings = getdefaults()
        priority = 1
    else:
        gamesettings = findgame(gamecode)
        priority = 3

    if gamesettings is None:
        gset = gameset(priority=priority, width=None, height=None, blorb=None, terp_number=None,
                       foreground=None, background=None, headline=None, author=None)
    else:
        gset = gameset(priority=priority,
                       title=gettitle(gamesettings),
                       headline=getheadline(gamesettings),
                       author=getauthor(gamesettings),
                       width=getwidth(gamesettings),
                       height=getheight(gamesettings),
                       blorb=getblorb(gamesettings),
                       terp_number=getterpnum(gamesettings),
                       foreground=getforeground(gamesettings),
                       background=getbackground(gamesettings)
                      )
    return gset


def setup():
    global file, filesize, filetext, defaults

    filename: str | None = None
    for loc in locations:
        filename = os.path.join(os.path.expandvars(loc), ".violarc")
        if os.path.exists(filename) == 1:
            break

    if filename is None:
        filetext = ''
    else:
        file = open(filename, "r")
        filesize = os.stat(filename).st_size
        filetext = file.read(filesize)
        file.close()
