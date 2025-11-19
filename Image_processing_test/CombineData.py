import csv
import sys


tower_types = (
    "dart_monkey", "boomerang_monkey", "bomb_shooter", "tack_shooter", 
    "ice_monkey", "glue_gunner", "desperado", "sniper_monkey", "monkey_sub", 
    "monkey_buccaneer", "monkey_ace", "heli_pilot", "mortar_monkey", "dartling_gunner", 
    "wizard_monkey", "super_monkey", "ninja_monkey", "alchemist", "druid", "mermonkey", 
    "banana_farm", "spike_factory", "monkey_village", "engineer_monkey", "beast_handler"
)

# Tower mapping
tower_enum = {name: idx for idx, name in enumerate(tower_types)}


def load_money_file(path):
    import csv

    # Read raw money entries
    money = {}
    with open(path, newline='') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header if present
        for frame, amount in reader:
            money[int(frame)] = int(amount)

    # If no entries, nothing to fill
    if not money:
        return money

    # Determine max frame
    max_frame = max(money.keys())

    # Reverse fill: frames missing get the "next" known value
    current = 0
    filled = {}

    for frame in range(max_frame, 1 - 1, -1):  # from max_frame down to 1
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

def main(money_file, tower_file, upgrade_file, output_file):
    money_data = load_money_file(money_file)
    tower_events = load_tower_file(tower_file)
    upgrade_events = load_upgrade_file(upgrade_file)

    # Determine max frame
    max_frame = max(
        max(money_data.keys(), default=0),
        max((t[0] for t in tower_events), default=0),
        max((u[0] for u in upgrade_events), default=0),
    )

    # Tower state tracking
    active_towers = {}  # name -> {x,y,u1,u2,u3}

    # Sort events by frame
    tower_events.sort(key=lambda x: x[0])
    upgrade_events.sort(key=lambda x: x[0])

    ti = 0
    ui = 0

    with open(output_file, "w") as out:
        out.write("frame,money,towers\n")

        for frame in range(1, max_frame + 1):

            # apply tower spawns
            while ti < len(tower_events) and tower_events[ti][0] == frame:
                _, name, x, y = tower_events[ti]
                active_towers[name] = {"x": x, "y": y, "u1": 0, "u2": 0, "u3": 0}
                ti += 1

            # apply upgrades
            while ui < len(upgrade_events) and upgrade_events[ui][0] == frame:
                _, name, u1, u2, u3 = upgrade_events[ui]
                if name in active_towers:
                    active_towers[name]["u1"] = u1
                    active_towers[name]["u2"] = u2
                    active_towers[name]["u3"] = u3
                ui += 1

            # money for this frame
            money = money_data.get(frame, 0)

            # Build tower string
            tower_strings = []
            for name, data in active_towers.items():
                tower_id = tower_enum.get(name, 0)  # use 'name', not data['name']
                tower_strings.append(
                    f"{tower_id},{data['x']},{data['y']},{data['u1']},{data['u2']},{data['u3']}"
                )


            towers_output = ";".join(tower_strings)

            out.write(f"{frame},{money},{towers_output}\n")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python CombineData.py <Money_Output> <Tower_Output> <Upgrade_Output> <Final_Output>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
