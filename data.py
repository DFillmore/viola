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

import re
from urllib.request import urlopen


ifdb_url = "https://ifdb.org/search?searchgo=Search+Games&searchfor=ifid:"

legacy_serials = ("00", "01", "02", "03", "04", "05")


def getcode(gamedata):
    release = (gamedata[2] << 8) + gamedata[3]
    serial = gamedata[0x12:0x18].decode('latin-1')
    return str(release) + '.' + serial


def getifid(gamedata):
    serial: list[str] = list(gamedata[0x12:0x18].decode('latin-1'))
    if serial[0] == "8" or serial[0] == "9" or ''.join(serial[0:2]) in legacy_serials:
        pass
    else:
        expr = r"(?<=UUID:\/\/)[a-zA-z\d\-]+(?=\/\/)"
        r = re.compile(expr, re.M | re.S)
        match = r.search(gamedata.decode('latin-1'))
        if match is not None:
            return match.string[match.start():match.end()]
    for a in range(len(serial)):
        if not serial[a].isalnum():
            serial[a] = "-"
    release = int.from_bytes(gamedata[2:4], byteorder="big")
    checksum = int.from_bytes(gamedata[0x1c:0x1e], byteorder="big")
    i = "ZCODE-" + str(release) + "-" + ''.join(serial)

    if serial[0].isnumeric() and serial[0] != "8" and ''.join(serial) not in ("000000", "999999", "------"):
        i += "-" + hex(checksum)[2:]
    return i


def getpage(ifid):
    response = urlopen(ifdb_url+ifid)
    page = response.read().decode('latin-1')
    if 'No results were found.' in page and 'Can\'t find the game you\'re looking for?' in page:
        page = None
    return page


def gettitle(ifdb_page):
    expr = r"(?<=\<h1\>).*(?=\<\/h1\>)"
    r = re.compile(expr, re.M | re.S)
    match = r.search(ifdb_page)
    if match is not None:
        return match.string[match.start():match.end()]
    return None


def getauthor(ifdb_page):
    expr1 = r"(?<=\<a href=\"search\?searchfor=author).*?(?=\<\/a\>)"
    expr2 = r"(?<=\">).*"
    r = re.compile(expr1, re.M | re.S)
    match = r.search(ifdb_page)
    if match is not None:
        m = match.string[match.start():match.end()]
        r = re.compile(expr2, re.M | re.S)
        match = r.search(m)
        if match is not None:
            return match.string[match.start():match.end()]
    return None


if __name__ == '__main__':
    f = open('games/zork1.z3', 'rb')
    d = f.read()
    f.close()
    p = getpage(getifid(d))
    if p:
        print(getifid(d), gettitle(p), getauthor(p))
