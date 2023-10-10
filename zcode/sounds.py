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

import blorb
import vio.zcode as io
import zcode
from zcode.constants import *
from vio.zcode import soundchannels


AVAILABLE = False



def setup(b):
    global device, channel, currentchannel, x, sounds, effectschannel, musicchannel
    global AVAILABLE, blorbs
    try:
        io.initsound()
        soundchannels[0].append(effectsChannel(0))
        soundchannels[1].append(musicChannel(0))
        AVAILABLE = True
    except:
        pass
    blorbs = b

def availablechannels(arg): 
    if AVAILABLE:
        return len(soundchannels[arg])
    return 0 # no sound capablities, no sound channels available

def bleep(type): # Either a high or a low bleep. 1 is high, 2 is low
    if type == 1:
        io.beep()
    if type == 2:
        io.boop()

# It might be a good idea to check the relevant flag in Flags 2 to see
# if the game wants to use sounds. If it does, various sound setting-up stuff can be done (such
# as loading the relevant data from a blorb file)


    
#SOUND



class Channel(io.soundChannel):
    sound = None
    routine = None

    def getbusy(self):
        return False

    def Notify(self):
        if self.getbusy() == False and self.routine != None and self.routine != 0:
            self.stop()
            i = zcode.game.interruptdata(zcode.game.INT_SOUND, self.routine)
            zcode.game.interruptstack.append(i)
            zcode.game.interrupt_call()
            zcode.routines.execloop()
            

class musicChannel(io.musicChannel):
    type = 1

class effectsChannel(io.effectsChannel):
    type = 0

    def Notify(self):
        self.getbusy()
        if self.getbusy() == False and self.routine != None and self.routine != 0:
            #self.stop()
            i = zcode.game.interruptdata(zcode.game.INT_SOUND, self.routine)
            zcode.game.interruptstack.append(i)
            zcode.game.interrupt_call()
            zcode.routines.execloop()


class Sound:
    def __init__(self, sound_number):
        self.number = sound_number
        for a in blorbs:
            sound_data = a.getSnd(sound_number)
            self.type = a.getSndType(sound_number)
        # Standards below 1.1 do not support seperate channels for different sound types, so we 
        # just don't support music in that case
        if zcode.use_standard < STANDARD_11 and self.type != 0: 
            self.sound = None
        elif sound_data:
            self.sound = io.sound(sound_data, self.type)
        else:
            self.sound = None

    def play(self, volume, repeats):
        try:
            self.sound.set_volume(volume)
            self.sound.play(loops=repeats)
        except:
            pass

    def stop(self):
        self.sound.stop()

    type = 0
    routine = 0
    repeats = 1
    playing = 1
    number = 0


currentchannel = [1, 1]

def playsound(sound, effect, volume, repeats, routine): # plays, prepares, stops or finishes with a sound. the 'volume' data from the opcode 'sound_effect' contains both the volume and repeats data needed here    
    if repeats == 255:
        repeats = -1
    else:
        repeats -= 1

    if effect == 1 or effect == 4:
        return False
    elif effect == 2:
        try:
            s = Sound(sound)        
            soundchannels[s.type][currentchannel[s.type]-1].play(s, volume, repeats, routine)
            return True
        except:
            return False
       
    elif effect == 3:
        try:
            s = Sound(sound)
            soundchannels[s.type][currentchannel[s.type]-1].stop(s)
            return True
        except:
            return False


def stopall():
    for a in soundchannels:
        for b in a:
            b.stop(b.sound)

