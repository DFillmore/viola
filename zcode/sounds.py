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

import pygame
import blorb
import zio as io

import zcode


AVAILABLE = False

soundchannels = [[],[]]

def setup(b):
    global device, channel, currentchannel, x, sounds, effectschannel, musicchannel
    global AVAILABLE, blorbs
    try:
        pygame.mixer.init()
        for a in range(io.pygame.maxeffectschannels()):
            soundchannels[0].append(effectsChannel(a))
        for a in range(io.pygame.maxmusicchannels()):
            soundchannels[1].append(musicChannel(a))
        AVAILABLE = True
    except:
        pass
    blorbs = b

def availablechannels(arg): 
    if AVAILABLE:
        return len(soundchannels[arg])
    return 0 # no sound capablities, no sound channels available

def beep(type): # Either a low or a high beep. 1 is low, 2 is high
    pass

# It might be a good idea to check the relevant flag in Flags 2 to see
# if the game wants to use sounds. If it does, various sound setting-up stuff can be done (such
# as loading the relevant data from a blorb file)


    
#SOUND


def soundhandler():
    for a in soundchannels:
        for b in a:
            b.Notify()

class Channel(io.pygame.soundChannel):
    sound = None
    routine = None

    def getbusy(self):
        return False

    def Notify(self):
        if self.getbusy() == False and self.routine != None and self.routine != 0:
            self.stop()
            zcode.game.interruptstack.append(self.routine)
            zcode.game.interrupt_call()
            zcode.routines.input = 0
            zcode.routines.execloop()
            

class musicChannel(Channel):
    type = 1

    def getbusy(self):
        return pygame.mixer.music.get_busy()

    def play(self, sound, volume, repeats, routine):
        self.sound = sound
        if self.sound.type != 1:
            self.sound = None
            return False
        self.routine = routine
        self.sound.play(volume, repeats)
        self.setup(soundhandler)
    
    def setvolume(self, volume):
        pygame.mixer.music.set_volume(volume)

    def stop(self, sound):
        if self.sound.number == sound.number:
            self.sound.stop()
            self.sound = None
            self.cleanup()



class effectsChannel(Channel):
    type = 0

    def __init__(self, id):
        self.id = id
        self.channelobj = pygame.mixer.Channel(id)

    channelobj = None

    def getbusy(self):
        try:
            busy = self.channelobj.get_busy()
        except:
            busy = False
        return busy

    def play(self, sound, volume, repeats, routine):
        self.sound = sound
        if self.sound.type != 0:
            self.sound = None
            return False      
        self.routine = routine
        self.setvolume(volume)
        self.channelobj.play(self.sound.sound, repeats)
        self.setup(soundhandler)

    def setvolume(self, volume):
        self.channelobj.set_volume(volume)

    def stop(self, sound):
        if self.sound.number == sound.number:
            self.channelobj.stop()
            self.sound = None
            self.routine = None
            self.cleanup()

    def Notify(self):
        self.getbusy()
        if self.getbusy() == False and self.routine != None and self.routine != 0:
            #self.stop()
            zcode.game.interruptstack.append(self.routine)
            zcode.game.interrupt_call()
            zcode.routines.input = 0
            zcode.routines.execloop()


class Sound:
    def __init__(self, sound_number):
        self.number = sound_number
        for a in blorbs:
            sound_data = a.getSnd(sound_number)
            self.type = a.getSndType(sound_number)
        if sound_data:
            self.sound = io.pygame.sound(sound_data, self.type)
        else:
            self.sound = None

    def play(self, volume, repeats):
        try:
            self.sound.set_volume(volume)
            self.sound.play(loops=repeats)
        except:
            pass

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
            print('currentchannel', currentchannel[s.type])
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


