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

import random
import sys

import zcode

# this file appears to be complete. Not intensively tested, but it seems to work.


# Due to the fact that the z-machine is generally considered to round numbers
# towards 0, and python always rounds numbers towards minus infinity, we need
# to mess around a bit. This code is stolen from old viola, because it works
# and I couldn't be bothered to figure it all out again

def div(a, b): # divide a by b
    if b == 0:
        error.fatal('Tried to divide by zero')
    else:
        x = a / b
        y = round(x)
        if (y < 0) and (y < x):
            y += 1
        if (y > 0) and (y > x):
            y -= 1
        z = int(y)
    return z

def mod(a, b): # divide a by b and return the remainder
    if b == 0:
        error.fatal('Tried to divide by zero')
    else:
        x = a / b
        y = round(x)
        if (y < 0) and (y < x):
            y += 1
        if (y > 0) and (y > x):
            y = y - 1
            y = int(y)
        z = int((0 -((y * b) - a)))
        return z

def add(a, b):
    x = a + b



def reduce(num): # reduces out of range numbers
    num = unneg(num)
    if num > 0xFFFF:
        num = num % 0x10000
    num = neg(num)
    return num

mode = 0 # 0 is random mode. 1 is predictable mode.
seed = 0
sequence = 1

# since the z-machine uses 16-bit numbers and python uses 32-bit numbers,
# we have to convert back and forth a bit. If we want to do signed maths with
# numbers from memory, we have to convert them using neg. If we want to store
# the result of a calculation in memory, we have to convert it using unneg.

def neg(negnum): 
    if (negnum & 32768 == 32768) and (negnum != 0): 
        negnum -= 0x10000
    return negnum

def unneg(negnum):
    if (negnum < 0):
        negnum += 0x10000
    return negnum

def randomize(zseed): # seeds the z-machine random number generator
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
        
def getrandom(max): # returns a number from the z-machine random number generator. Max should not be more than 32767
    global seed
    global sequence
    if mode == 0:
        if max == 1:
            value = 1
        else:
            value = random.randrange(1, max+1)
    elif seed < 1000: #  if the mode is predictable and the seed is less than 100, max is ignored (it should be the same as seed in any case)
        value = sequence
        sequence += 1
        if sequence > seed:
            sequence = 1
    else:
        value = random.randrange(1,max+1)
    return value
