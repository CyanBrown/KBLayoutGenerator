import math
import random
import time

from matplotlib import pyplot as plt
from threading import Thread

# the keys that are ok to be changed
included_letters = list("qwfpgjluy;arstdhneio'\"zxcvbkm,.?><:/")

"""
this is the # association
Q: 1
W: 2
E: 3
R: 4
T: 5
Y: 6
U: 7
I: 8
O: 9
P: 10
A: 11
S: 12
D: 13
F: 14
G: 15
H: 16
J: 17
K: 18
L: 19
;: 20
Z: 21
X: 22
C: 23
V: 24
B: 25
N: 26
M: 27
': 28
,: 29
.: 30
/: 31
"""

# my personal rating of how easy I think it is to press each key 0-1 where 1 is highest
kb_priority = {1: .3, 2: .5, 3: .6, 4: .5, 5: .1, 6: 0, 7: .5, 8: .7, 9: .6, 10: .3, 11: 1, 12: 1, 13: 1,
               14: 1, 15: .5, 16: .6, 17: 1, 18: 1, 19: 1, 20: 1, 21: .3, 22: .4, 23: .6, 24: .6, 25: 0,
               26: .7, 27: .5, 28: .2, 29: .2, 30: .4, 31: .3}

# how fast each of my fingers can type normalized - 1 is left pinky, 8 is right pinky
finger_priority = {1: 0.803030303, 2: 0.893939394, 3: 0.893939394, 4: 1, 5: 0.954545455, 6: 0.954545455,
                   7: 0.954545455, 8: 0.878787879}

# these hold association of key # to what finger presses it
finger_groups = {1: [1, 11, 21], 2: [2, 12], 3: [3, 13, 22], 4: [4, 5, 14, 15, 23, 24, 25],
                 5: [6, 7, 16, 17, 26, 27], 6: [8, 18, 28], 7: [9, 19, 29], 8: [10, 20, 30, 31]}
keys_to_finger = {}
for key, value in finger_groups.items():
    for i in value:
        keys_to_finger[i] = key

# two popular layouts
qwerty = {l: idx + 1 for idx, l in enumerate("qwertyuiopasdfghjkl;zxcvbnm',./")}
colemak = {l: idx + 1 for idx, l in enumerate("qwfpgjluy;arstdhneiozxcvbkm',./")}

# this is the training data a split into 8 lists to optimize threading
data = []
with open("data.txt", "r", encoding="utf8") as f:
    read = [i.lower() for i in f.readlines()]
    for i in read:
        q = len(i) // 4
        data.append(list(i[:q]))
        data.append(list(i[q:q * 2]))
        data.append(list(i[q * 2:q * 3]))
        data.append(list(i[q * 3:]))


def calc_line(layout, line, results):
    score = 0

    for i in line:
        prior_letter = ""
        for c in i:
            if c not in included_letters:
                continue

            if c == '"':
                t = "'"
            elif c == ":":
                t = ";"
            elif c == "<":
                t = ","
            elif c == ">":
                t = "."
            elif c == "?":
                t = "/"
            else:
                t = c

            # add points for position
            score += kb_priority[layout[t]] * 2

            # add points for finger speed
            score += finger_priority[keys_to_finger[layout[t]]] * .3

            if prior_letter == "":
                prior_letter = t
                continue

            # don't want to use same finger twice in row so lose points
            if keys_to_finger[layout[t]] == keys_to_finger[layout[prior_letter]]:
                score -= 0.3

            # ideally want keypresses to switch hands each time (this is my own personal preference)
            if (keys_to_finger[layout[t]] in range(1, 5) and keys_to_finger[layout[prior_letter]] in range(5, 9)) or (
                    keys_to_finger[layout[t]] in range(5, 9) and keys_to_finger[layout[prior_letter]] in range(1, 5)):
                score += 0.1

            prior_letter = t

    results.append(score)


# @jit(target_backend="cuda")
def generate_score(layout):
    score = 0

    # start threading for each dataset
    threads = []
    results = []
    for i in range(len(data)):
        t = Thread(target=calc_line, args=(layout, data[i], results))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    score += math.fsum(results)

    # we want to keep important ctrl shortcuts close - could include z in the future
    if layout["c"] in [11, 12, 13, 14, 21, 22, 23, 24, 25]:
        score += 3000
    if layout["v"] in [11, 12, 13, 14, 21, 22, 23, 24, 25]:
        score += 3000
    if layout["x"] in [11, 12, 13, 14, 21, 22, 23, 24, 25]:
        score += 3000

    return score


def mix(layout, n):
    # switches n # of pairs on layout
    available = list(range(1, 32))
    rlayout = {value: key for key, value in layout.items()}
    for i in range(n):
        r1 = random.choice(available)
        available.remove(r1)
        r2 = random.choice(available)
        available.remove(r2)

        tmp1 = rlayout[r1]
        tmp2 = rlayout[r2]

        layout[tmp2] = r1
        layout[tmp1] = r2

    return layout


current = qwerty
current_score = generate_score(current)
best = qwerty
best_score = current_score

# initial max for simulated annealing
reps = 500000
temp = reps

scores = [current_score]

now = time.time()

while temp > 1:
    # generate "adjacent" layout
    new = mix(current.copy(), math.ceil(temp / reps * 6))
    new_score = generate_score(new)

    if temp % 100 == 0:
        print(temp, current_score, current)
        scores.append(new_score)

    # take higher value kb for next iteration
    if new_score > current_score:
        current = new
        current_score = new_score
        if best_score < current_score:
            best = new
            best_score = current_score
    else:
        # allow for worse layout to be accepted relative to temp and how different the layouts are in score
        d = abs((new_score - current_score) / current_score)
        if random.random() * reps < (1 - d) * (temp / 2):
            current = new
            current_score = new_score

    temp -= 1

print(best)
print(best_score)

print(time.time() - now)

plt.plot(range(len(scores)), scores)
plt.show()

# This is the layout generated I call it ROSE after the left side of the homerow
# {'q': 28, 'w': 30, 'e': 14, 'r': 11, 't': 17, 'y': 15, 'u': 3, 'i': 18, 'o': 12, 'p': 7, 'a': 19, 's': 13, 'd': 26, 'f': 4, 'g': 27, 'h': 16, 'j': 1, 'k': 31, 'l': 8, ';': 5, 'z': 25, 'x': 21, 'c': 23, 'v': 24, 'b': 2, 'n': 20, 'm': 9, "'": 29, ',': 22, '.': 10, '/': 6}
