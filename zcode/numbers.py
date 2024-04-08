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

import random

import zcode


# Due to the fact that the Z-machine is generally considered to round numbers
# towards 0, and Python always rounds numbers towards minus infinity, we need
# to mess around a bit. This code is stolen from old Viola, because it works
# and I couldn't be bothered to figure it all out again. As such it is probably
# the only code surviving from the original, very messy version of Viola.

def div(a, b):  # divide a by b
    if b == 0:
        zcode.error.fatal('Tried to divide by zero')
    else:
        x = a / b
        y = round(x)
        if (y < 0) and (y < x):
            y += 1
        if (y > 0) and (y > x):
            y -= 1
        z = int(y)
    return z


def mod(a, b):  # divide a by b and return the remainder
    if b == 0:
        zcode.error.fatal('Tried to divide by zero')
    else:
        x = a / b
        y = round(x)
        if (y < 0) and (y < x):
            y += 1
        if (y > 0) and (y > x):
            y = y - 1
            y = int(y)
        z = int((0 - ((y * b) - a)))
        return z


def reduce(num):  # reduces out of range numbers
    num = unsigned(num)
    if num > 0xFFFF:
        num = num % 0x10000
    num = signed(num)
    return num


mode = 0  # 0 is random mode. 1 is predictable mode.
seed = 0
sequence = 1


# since the z-machine uses 16-bit numbers and python uses 32-bit numbers,
# we have to convert back and forth a bit. If we want to do signed maths with
# numbers from memory, we have to convert them using signed(). If we want to store
# the result of a calculation in memory, we have to convert it using unsigned().

def signed(negnum):
    return negnum - ((negnum & 0x8000) * 2)


def unsigned(negnum):
    if (negnum < 0):
        negnum += 0x10000
    return negnum


def randomize(zseed):  # seeds the z-machine random number generator
    global seed
    global mode
    global sequence
    if zseed == 0:
        random.seed()
    elif zseed < 1000:
        seed = zseed
        mode = 1
        sequence = 1
    else:
        seed = zseed
        mode = 1
        random.seed(seed)


def getrandom(max):  # returns a number from the z-machine random number generator. Max should not be more than 32767
    global seed
    global sequence
    if mode == 0:
        if max == 1:
            value = 1
        else:
            value = random.randrange(1, max + 1)
    elif seed < 1000:  #  if the mode is predictable and the seed is less than 1000, max is ignored (it should be the same as seed in any case)
        value = sequence
        sequence += 1
        if sequence > seed:
            sequence = 1
    else:
        value = random.randrange(1, max + 1)
    return value
