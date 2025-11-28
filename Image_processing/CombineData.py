import csv
import sys

def is_predecessor(prev, curr):
    _, p1, p2, p3 = prev
    _, c1, c2, c3 = curr

    d1 = c1 - p1
    d2 = c2 - p2
    d3 = c3 - p3

    return ( # check that the upgrade is the predacesor
        ((d1 == 1) + (d2 == 1) + (d3 == 1)) == 1 and
        d1 >= 0 and d2 >= 0 and d3 >= 0
    )


tower_types = (
    "dart_monkey", "boomerang_monkey", "bomb_shooter", "tack_shooter", 
    "ice_monkey", "glue_gunner", "desperado", "sniper_monkey", "monkey_sub", 
    "monkey_buccaneer", "monkey_ace", "heli_pilot", "mortar_monkey", "dartling_gunner", 
    "wizard_monkey", "super_monkey", "ninja_monkey", "alchemist", "druid", "mermonkey", 
    "banana_farm", "spike_factory", "monkey_village", "engineer_monkey", "beast_handler"
)

# tower mapping
tower_enum = {name: idx for idx, name in enumerate(tower_types)}


def load_money_file(path):
    money = {}
    with open(path, newline='') as f:
        reader = csv.reader(f)
        for frame, amount in reader:
            money[int(frame)] = int(amount)

    max_frame = max(money.keys())

    # Reverse fill: frames to extrapolate missing values
    current = 0
    filled = {}

    for frame in range(max_frame, 1 - 1, -1):
        if frame in money:
            current = money[frame]
        filled[frame] = current

    return filled

def load_tower_file(path):
    towers = []  # list of (frame, name, x, y)
    with open(path, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            frame = int(row[0])
            name = row[1]
            x = int(row[2])
            y = int(row[3])
            towers.append((frame, name, x, y))
    return towers

def load_upgrade_file(path):
    upgrades = []  # list of (frame, name, u1, u2, u3)
    with open(path, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            upgrades.append((int(row[0]), row[1], int(row[2]), int(row[3]), int(row[4])))
    return upgrades


if len(sys.argv) != 5:
        print("Usage: python CombineData.py <Money_Output> <Tower_Output> <Upgrade_Output> <Final_Output>")
        sys.exit(1)

money_file = sys.argv[1]
tower_file = sys.argv[2]
upgrade_file = sys.argv[3]
output_file = sys.argv[4]

money_data = load_money_file(money_file)
tower_events = load_tower_file(tower_file)
upgrade_events = load_upgrade_file(upgrade_file)



# find the max frame
max_frame = max(
    max(money_data.keys(), default=0),
    max((t[0] for t in tower_events), default=0),
    max((u[0] for u in upgrade_events), default=0),
)

active_towers = []

# sort events by frame
tower_events.sort(key=lambda x: x[0])
upgrade_events.sort(key=lambda x: x[0])

ti = 0
ui = 0

with open(output_file, "w") as out:
    for frame in range(1, max_frame + 1):
        # if there is a tower event, append the tower event
        while ti < len(tower_events) and tower_events[ti][0] == frame:
            _, name, x, y = tower_events[ti]
            active_towers.append({
                "name": name,
                "x": x,
                "y": y,
                "u1": 0,
                "u2": 0,
                "u3": 0
            })
            ti += 1

        # if there is an upgrade event, append the upgrade event
        while ui < len(upgrade_events) and upgrade_events[ui][0] == frame:
            _, name, u1, u2, u3 = upgrade_events[ui]

            candidates = [t for t in active_towers if t["name"] == name]

            new = (name, u1, u2, u3)

            # find tower whose upgrades are predecessor
            match = None
            for t in candidates:
                prev = (name, t["u1"], t["u2"], t["u3"])
                if is_predecessor(prev, new):
                    match = t
                    break

            if match:
                match["u1"] = u1
                match["u2"] = u2
                match["u3"] = u3

            ui += 1

        # take the median frame money as money for that frame
        values = []
        for df in (-2, -1, 0, 1, 2):
            f2 = frame + df
            values.append(money_data.get(f2, 0))

        values.sort()
        money = values[len(values) // 2]  # median of 5


        # append existing towers and upgrades
        tower_strings = []
        for t in active_towers:
            tower_id = tower_enum.get(t["name"], 0)
            tower_strings.append(
                f"{tower_id},{t['x']},{t['y']},{t['u1']},{t['u2']},{t['u3']}"
            )

        # save the output
        towers_output = ",".join(tower_strings)
        out.write(f"{frame},{money},{towers_output}\n")