import pyautogui
import time
from pynput.keyboard import Key, Controller
import mss
import numpy as np
from PIL import Image
import os

### GAME HOTKEYS / DATA VALUES 

MONKEY_KEYS = [
    "u",  # 0 - Hero
    "q",  # 1 - Dart
    "w",  # 2 - Boomerang
    "e",  # 3 - Bomb
    "r",  # 4 - Tack
    "t",  # 5 - Ice
    "y",  # 6 - Glue
    "z",  # 7 - Sniper
    "x",  # 8 - Sub
    "c",  # 9 - Pirate
    "v",  # 10 - Ace
    "b",  # 11 - Heli
    "n",  # 12 - Mortar
    "m",  # 13 - Dartling
    "a",  # 14 - Wizard
    "s",  # 15 - Super
    "d",  # 16 - Ninja
    "f",  # 17 - Alch
    "g",  # 18 - Druid
    "h",  # 19 - Farm
    "j",  # 20 - Spike
    "k",  # 21 - Village
    "l",  # 22 - Engi
]

def monkey_hotkey(index):
    return MONKEY_KEYS[index]

### GAME FUNCTIONS

def place_monkey(index, point):
    keyB = Controller()
    key = monkey_hotkey(index)

    keyB.press(key)
    time.sleep(0.15)
    keyB.release(key)
    time.sleep(0.15)

    pyautogui.moveTo(*point)
    pyautogui.click(*point)


def upgrade_hotkey(index):
    if index == 0:
        return ","
    if index == 1:
        return "."
    if index == 2:
        return "/"

def upgrade(index, point):
    keyB = Controller()
    pyautogui.click(*point)
    key = upgrade_hotkey(index)

    keyB.press(key)
    time.sleep(0.2)
    keyB.release(key)

    keyB.press(Key.esc)
    time.sleep(0.1)
    keyB.release(Key.esc)

def sell_tower(point):
    keyB = Controller()
    pyautogui.click(*point)
    keyB.press(Key.backspace)
    time.sleep(0.1)
    keyB.release(Key.backspace)

### PLAY FUNCTIONS
def focus_btd6(): # used for testing
    time.sleep(0.1)
    pyautogui.keyDown("alt")
    pyautogui.press("tab")
    pyautogui.keyUp("alt")

def capture_screen():
    screenshot = pyautogui.screenshot()  # region=None → full screen
    img = np.array(screenshot)
    return img

# USING THIS FUNCTION IF WE ARENT USING AUTOPLAY / OUR AI CHOOSES ITS OPTIONS ONLY AT THE END OF ROUND?

def round_over(start_button_path):
    screen = pyautogui.screenshot()
    found = list(pyautogui.locateAll(start_button_path, screen))
    return len(found) != 0


def next_round():
    keyB = Controller()
    keyB.press(Key.space)
    time.sleep(0.1)
    keyB.release(Key.space)
    capture_screen()


class Monkey:
    def __init__(self, name, key_index, position):
        self.name = name
        self.key_index = key_index
        self.position = position
        self.upgrades = [0, 0, 0]  # [top, middle, bottom]
    
    def place(self):
        place_monkey(self.key_index, self.position)
    
    def upgrade(self, path_index):
        upgrade(path_index, self.position)
        self.upgrades[path_index] += 1

    def sell(self):
        sell_tower(self.position)
