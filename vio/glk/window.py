import pygame

windows = [None]

class window:
    rock = 0
    def __init__(self, split, method, size, type, rock):
        global windows
        self.rock = rock
        self.type = type
        if split == 0:
            self.ioWindow = io.window(ioScreen, font)
            self.ioWindow.setPosition(0,0)
            self.ioWindow.setSize(self.ioWindow.screen.getWidth(), self.ioWindow.screen.getHeight())




def open(split, method, size, wintype, rock):
    return window(split, method, size, wintype, rock)