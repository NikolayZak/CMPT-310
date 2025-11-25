import pyautogui
import time
from pynput.keyboard import Key, Controller
import numpy as np
import money


### GAME HOTKEYS / DATA VALUES 

MONKEY_KEYS = [
    "u",  # 0 - Hero
    "q",  # 1 - Dart
    "w",  # 2 - Boomerang
    "e",  # 3 - Bomb
    "r",  # 4 - Tack
    "t",  # 5 - Ice
    "y",  # 6 - Glue
    "p",  # 7 - Desparado
    "z",  # 8 - Sniper
    "x",  # 9 - Sub
    "c",  # 10 - Pirate
    "v",  # 11 - Ace
    "b",  # 12 - Heli
    "n",  # 13 - Mortar
    "m",  # 14 - Dartling
    "a",  # 15 - Wizard
    "s",  # 16 - Super
    "d",  # 17 - Ninja
    "f",  # 18 - Alch
    "g",  # 19 - Druid
    "o",  # 20 - Mermonkey
    "h",  # 21 - Farm
    "j",  # 22 - Spike
    "k",  # 23 - Village
    "l",  # 24 - Engineer
    "i"   # 25 - beast handler
]

DIFF_MULTIES = [
    0.85,# easy
    1, #normal - default
    1.08, # Hard
    1.2 # impoppable
]

NORMAL_COSTS = [
    99999, #hero
    200, #dart
    315, #boomer
    375, #bomb
    260, #tack
    400, #ice
    225, #glue
    300, # desperado
    350, #sniper
    325, #sub
    400, #pirate buccaneer
    800, # ace
    1500, #heli
    600, #mortar
    850, # dartling
    250, #wizard
    2500, #super
    400, # ninja
    550, #alchemist
    400, #druid
    375 , #mermonkey
    1250, #banana
    1000, #spike
    1200, #village
    350, #engineer
    250 #Beast handler
]

NORMAL_UPGRADES = [
    [ # HERO
     [99999,99999,99999,99999,99999],
     [99999,99999,99999,99999,99999],
     [99999,99999,99999,99999,99999]   
    ],     
    [ # Dart monkey
     [140, 200, 320, 1800, 15000],
     [100, 190, 450, 7200, 45000],
     [90, 200, 575, 2050, 21500]   
    ],
    [ # Boomerang
     [200,280,600,2000,32500],
     [175,250,1250,4200,35000],
     [100,300,1300,2400,50000]   
    ],  
    [ # Bomb Shooter
     [250, 650, 1100, 2800, 55000],
     [250, 400, 1000, 3450, 28000],
     [200, 300, 700, 2500, 23000]   
    ],  
    [ # Tack Shooter
     [150, 300, 600, 3500, 45500],
     [100, 225, 550, 2700, 15000],
     [110, 110, 450, 3200, 20000]   
    ],  
    [ # Ice monkey
     [150, 350, 1500, 2300, 28000],
     [200, 300, 2750, 4000, 16000],
     [150, 200, 1900, 2750, 30000]   
    ],  
    [ # Glue gunner
     [200, 300, 2000, 5000, 22500],
     [100, 970, 1950, 4000, 16000],
     [280, 400, 3600, 4000, 24000]   
    ],
    [ # Desperado
     [200,200,1200,4800,17500],
     [150,350,3000,6500,42000],
     [220,280,2100,8500,31000]   
    ],
    [ # Sniper
     [350, 1300, 2500, 6000, 32000],
     [250, 450, 2100, 7600, 12000],
     [450, 450, 2700, 4100, 14900]   
    ],  
    [ # Monkey sub
     [130, 500, 700, 2300, 28000],
     [450, 300, 1350, 13000, 29000],
     [450, 1000, 1100, 2500, 25000]   
    ],  
    [ # Monkey Buccaneer (Pirate)
     [275, 425, 3050, 8000, 24500],
     [550, 500, 900, 3900, 27000],
     [200, 350, 2400, 5500, 23000]   
    ],  
    [ # Monkey Ace 
     [450, 550, 1000, 3300, 42500],
     [200, 350, 900, 18000, 26000],
     [500, 550, 2550, 23400, 85000]   
    ],  
    [ # Heli Pilot
     [800, 500, 1850, 19600, 45000],
     [300, 600, 3500, 9500, 30000],
     [250, 350, 3400, 8500, 35000]   
    ], 
    [ # Mortar monkey
     [300, 500, 825, 7000, 36000],
     [400, 500, 900, 6500, 38000],
     [200, 400, 1100, 9500, 40000]   
    ],
    [ # Dartling gunner
     [300, 900, 3000, 11750, 75000],
     [250, 950, 4500, 5850, 65000],
     [150, 1200, 3400, 12000, 58000]   
    ],
    [ # Wizard monkey
     [175, 450, 1450, 10000, 32000],
     [300, 800, 3300, 6000, 50000],
     [300, 300, 1500, 2800, 26500]   
    ], 
    [ # Super
     [2000, 2500, 20000, 100000, 500000],
     [1500, 1900, 7500, 25000, 70000],
     [3000, 1200, 5600, 55555, 165650]   
    ], 
    [ # Ninja
     [350, 350, 900, 2750, 35000],
     [250, 400, 1200, 5200, 22000],
     [300, 450, 2250, 5000, 40000]   
    ], 
    [ # Alchemist
     [250, 350, 1400, 2850, 48000],
     [250, 475, 2800, 4200, 45000],
     [650, 450, 1000, 2750, 40000]   
    ],
    [ # Druid
     [350, 850, 1700, 4500, 60000],
     [250, 350, 1050, 4900, 35000],
     [100, 300, 600, 2350, 45000]   
    ],  
    [ # Mermonkey
     [150,250,1600,4200,23000],
     [200,300,1900,8000,48000],
     [300,380,2000,7600,25000]   
    ],
    [ # Banana Farm
     [500, 600, 3000, 19000, 115000],
     [300, 800, 3650, 7200, 100000],
     [250, 400, 2700, 15000, 70000]   
    ],
    [ # Spike factory
     [800, 600, 2300, 9500, 125000],
     [600, 800, 2500, 7000, 41000],
     [150, 400, 1300, 3600, 30000]   
    ],
    [ # monkey village
     [400, 1500, 800, 2500, 25000],
     [250, 2000, 7500, 20000, 40000],
     [500, 500, 10000, 3000, 5000]   
    ], 
    [ # Engineer monkey
     [500, 400, 575, 2500, 32000],
     [250, 350, 900, 13500, 72000],
     [450, 220, 450, 3600, 45000]   
    ], 
    [ # Beast handler
     [160, 810, 2010, 12500, 45000],
     [175, 830, 2065, 9500, 60000],
     [190, 860, 2120, 9000, 30000]   
    ]
]

def monkey_hotkey(index):
    return MONKEY_KEYS[index]

def get_upgrade_cost(monkey_index, upgrades, difficulty=1):
    upgrade_list = NORMAL_UPGRADES[monkey_index]
    mult = DIFF_MULTIES[difficulty]

    costs = [
        [int(cost * mult) for cost in upgrade_list[0]],
        [int(cost * mult) for cost in upgrade_list[1]],
        [int(cost * mult) for cost in upgrade_list[2]]
    ]
    top, mid, bot = upgrades

    return [costs[0][top], costs[1][mid], costs[2][bot]]

def round_to_5(n):
    return int(round(n / 5) * 5)

def get_monkey_cost(difficulty=1):
    mult = DIFF_MULTIES[difficulty]
    return [round_to_5(cost * mult) for cost in NORMAL_COSTS]

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
    screenshot = pyautogui.screenshot()  
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

def getMoney():
    return money.getMoney(capture_screen())

def noOp():
    pass 
