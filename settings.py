# Copyright (C) 2004 David Fillmore
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

# reads settings from the .violarc file

import re
import os


title = ""
height = 480
width = 640
code = ""
filename = os.path.join(os.path.expandvars("$HOME"), ".violarc")
#filename = r"C:\Documents and Settings\Marvin\Desktop\wips\viola\violarc-example"

if os.path.exists(filename) != 1:
    filename = None


def getcode(gamedata):
    release = (gamedata[2] << 8) + gamedata[3]
    serial = gamedata[0x12:0x18].decode('ascii')
    print('getcode', str(release))
    return str(release) + '.' + serial

def findgame():
    c = re.escape(code)
    expr = r'code:[\s\w\.]*' + c + '.*?(^%%|\Z)'
    r = re.compile(expr, re.M | re.S)
    match = r.search(filetext)
    if match == None: 
        return None
    return match.string[match.start():match.end()]
    
def getdefaults():
    expr = r'.*?(^%%|\Z)'
    r = re.compile(expr, re.M | re.S)
    match = r.search(filetext)
    return match.string[match.start():match.end()]

def gettitle(gamesettings):
    expr = r'title:.*?$'
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match == None:
        return None
    else:
        return match.string[match.start()+6:match.end()].strip()

def getblorb(gamesettings):
    expr = r'blorb:.*?$'
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match == None:
        return None
    else:
        return match.string[match.start()+6:match.end()].strip()

def getheight(gamesettings):
    expr = r'height:.*?$'
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match == None:
        return None
    else:
        return match.string[match.start()+7:match.end()].strip()

def getwidth(gamesettings):
    expr = r'width:.*?$'
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match == None:
        return None
    else:
        return match.string[match.start()+6:match.end()].strip()

def getterpnum(gamesettings):
    expr = r'terpnum:.*?$'
    r = re.compile(expr, re.M)
    match = r.search(gamesettings)
    if match == None:
        return None
    else:
        return match.string[match.start()+8:match.end()].strip()

def getsettings(gamesettings):
    if gamesettings == None:
        return [None, None, None, None, None]
    set = []
    set.append(gettitle(gamesettings))
    set.append(getwidth(gamesettings))
    set.append(getheight(gamesettings))
    set.append(getblorb(gamesettings))
    set.append(getterpnum(gamesettings))
    return set
        
def setup(gamedata):
    global file, filesize, filetext, code, defaults, gamesettings
    if filename == None:
        filetext = ''
    else:
        file = open(filename, "rb")
        filesize = os.stat(filename).st_size
        filetext = file.read(filesize)
        file.close()

    code = getcode(gamedata)

