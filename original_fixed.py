import random


def d6():
    return random.randint(1, 6)


def hunter(target):
    r"""
    function that keeps track of how many rolls & omens before encounter
    occurs returns a tuple to huntercounter()
    """
    sum = 0
    rolls = 0
    omen = False
    die_roll = 0

    while sum < target:
        omen |= sum == 17
        rolls += 1 if die_roll != 6 else 0
        die_roll = d6()
        sum += die_roll
        sum = 17 if sum == target else sum

    return rolls, omen


def huntercounter(hunts):
    r"""
    Primary function keeps track of the counts & calls the hunter function
    """
    roll_counter = {n: 0 for n in range(1, 21)}
    omen_counter = {False: 0, True: 0}

    for _ in range(hunts):
        rolls, omens = hunter(20)
        roll_counter[rolls] += 1
        omen_counter[omens] += 1

    print("Roll Totals")
    print("".join(f"{k}; {v}\n" for k, v in sorted(roll_counter.items())))
    print("\nOmen Totals")
    print("".join(f"{k}; {v}\n" for k, v in sorted(omen_counter.items())))


if __name__ == "__main__":
    huntercounter(100000)
