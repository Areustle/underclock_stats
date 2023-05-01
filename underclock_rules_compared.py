import matplotlib.pyplot as plt
import numpy as np


def underclock(rule, n, d=6, tries=20):
    """
    Generic driver of underclock rules.

    Step through ticks of the underclock tracking random rolls and how they
    affect the behavior given a user-defiend rule.

    histogram bin the ticks and omens, and return
    """
    clock = np.full(n, 20)
    ticks = np.ones(n, dtype=int)
    omens = np.zeros(n, dtype=bool)
    run = np.ones(n, dtype=bool)

    for _ in range(tries):
        rolls = np.random.choice(np.arange(1, d + 1), n)
        clock, ticks, omens, run = rule(rolls, clock, ticks, omens, run, d)

    tick_count, tick_bins = np.histogram(ticks, bins=np.arange(1, 22), density=True)

    omen_sum = np.sum(omens)
    omen_count = np.array([omen_sum, n - omen_sum])
    return tick_bins, tick_count, omen_count


def original_rule(rolls, clock, ticks, omens, run, d, x=3):
    """
    Goblinpunch underclock rule.
    - Encounter triggered when clock goes negative.
    - Ticks repeat on a Max roll (6 for d6)
    - Clock resets to x(=3) at exactly zero
    - Omens triggered when clock == x(=3)
    """
    clock -= rolls
    run[clock < 0] = False
    ticks[run & (rolls != d)] += 1
    clock[run & (clock == 0)] = x
    omens[run & (clock == x)] = True
    return clock, ticks, omens, run


def alternative_rule(rolls, clock, ticks, omens, run, d, x):
    """
    Alternatice underclock rule.
    - Encounter triggered when clock reaches zero (or goes negative.)
    - Ticks repeat on a Max roll (6 for d6)
    - Clock resets to x whenever below x but still running
    - Omens triggered when clock <= x
    """
    clock -= rolls
    run[clock <= 0] = False
    ticks[run & (rolls != d)] += 1
    clock[run & (clock < x) & (clock > 0)] = x
    omens[run & (clock <= x)] = True
    return clock, ticks, omens, run


def classic_random_encounter(rolls, clock, ticks, omens, run, *args):
    r"""
    A classic random encounter system where every turn the random encounter die
    is rolled. On a 1 the encounter is triggered. On a 2 an omen is triggered.
    """
    run[rolls == 1] = False
    ticks[run] += 1
    omens[run & (rolls == 2)] = True
    return clock, ticks, omens, run


def plot_ticks(ax, bins, counts, color, label):
    """
    Histogram plot each of the rule tick results on provided ax.
    """
    ave = np.average(bins[:-1], weights=counts)
    ax.bar(
        bins[:-1],
        counts * 100,
        fill=False,
        edgecolor=color,
        label=label + f": mean {ave:2.3}",
    )


if __name__ == "__main__":
    N = int(1e6)
    d = 6
    classic = underclock(lambda *args: classic_random_encounter(*args), N, d)
    orig = underclock(lambda *args: original_rule(*args, x=3), N, d)
    a4 = underclock(lambda *args: alternative_rule(*args, x=4), N, d)
    a3 = underclock(lambda *args: alternative_rule(*args, x=3), N, d)
    a2 = underclock(lambda *args: alternative_rule(*args, x=2), N, d)

    # ::::::::::::::::::: Plots :::::::::::::::::::
    labels = ["Classic", "Alt 2", "Alt 3", "Alt 4", "Goblinpunch Rule"]
    fig, axs = plt.subplots(1, 2, figsize=(14, 7), layout="constrained")
    fig.suptitle(
        "Underclock Rule Comparisons\n" f" Dice = d{d}\n" f"{N:,} Samples Each"
    )

    # Encounter Frequency Histogram
    axs[0].set_title("Clock Ticks Until Encounter")
    axs[0].set_xticks(np.arange(1, 21))
    axs[0].set_xlabel("Roll Count")
    axs[0].set_ylabel("Frequency (Percentage)")
    plot_ticks(axs[0], *classic[0:2], "lightgray", labels[0])
    plot_ticks(axs[0], *a2[0:2], "green", labels[1])
    plot_ticks(axs[0], *a3[0:2], "orange", labels[2])
    plot_ticks(axs[0], *a4[0:2], "red", labels[3])
    plot_ticks(axs[0], *orig[0:2], "blue", labels[4])
    axs[0].legend()

    # Encounter Foreshadowing plot.
    axs[1].set_title("Encounter Foreshadowing")
    omens = np.stack((classic[2], a2[2], a3[2], a4[2], orig[2]), 1)
    x = np.arange(len(labels))
    multiplier = 0

    for la, om in zip(["Forshadowed", "Surprised"], omens):
        offset = 0.25 * multiplier
        rects = axs[1].bar(x + offset, om / N * 100, 0.25, label=la)
        axs[1].bar_label(rects, padding=3)
        multiplier += 1

    axs[1].set_xticks(x + 0.25, labels)
    axs[1].set_xlabel("Underclock Rule")
    axs[1].set_ylabel("Frequency (Percentage)")
    axs[1].legend(loc="upper left", ncols=2)
    plt.show()
