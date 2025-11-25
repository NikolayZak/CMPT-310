import sys



def getMoney():
    amt= input(">>>")
    if amt.startswith('q'):
        sys.exit()
    try:
        return int(amt)
    except:
        return None


def place_monkey(tower, coord):
    x,y = coord
    print(f"place monkey {x},{y}: {tower}")

def upgrade(upgrade, coord):
    x,y = coord
    print(f"upgrade {x},{y}: {upgrade}")

def noOp():
    print("doing nothing")
