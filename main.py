import json
import math
import random
from random import randint

included_letters = list("qwfpgjluy;arstdhneio'\"zxcvbkm,.?><:/")

kb_priority = {1: .3, 2: .5, 3: .6, 4: .5, 5: .1, 6: 0, 7: .5, 8: .7, 9: .6, 10: .3, 11: 1, 12: 1, 13: 1,
                14: 1, 15: .5, 16: .6, 17: 1, 18: 1, 19: 1, 20: 1, 21: .3, 22: .4, 23: .6, 24: .6, 25: 0,
                26: .7, 27: .5, 28: .2, 29: .2, 30: .4, 31: .3}
finger_priority = {1: 0.803030303, 2: 0.893939394, 3: 0.893939394, 4: 1, 5: 0.954545455, 6: 0.954545455,
                    7: 0.954545455, 8: 0.878787879}
finger_groups = {1: [1, 11, 21], 2: [2, 12], 3: [3, 13, 22], 4: [4, 14, 15, 23, 24, 25],
                5: [6, 7, 16, 17, 26, 27], 6: [8, 18, 28], 7: [9, 19, 29], 8: [10, 20, 30, 31]}

qwerty = {l: idx+1 for idx, l in enumerate("qwertyuiopasdfghjkl;zxcvbnm',./")}
colemak = {l: idx+1 for idx, l in enumerate("qwfpgjluy;arstdhneiozxcvbkm',./")}


def generate_score(layout):
    score = 0
    data = ""
    with open("data.txt", "r") as f:
        data = f.read().lower()

    words = data.split(' ')

    for i in words:
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

            score += kb_priority[layout[t]]

    return score


def mix(layout, n):
    used = []
    rlayout = {value: key for key, value in layout.items()}
    for i in range(n):
        r1, r2 = randint(1, 31), randint(1, 31)
        while r1 == r2 or r1 in used or r2 in used:
            r1, r2 = randint(1, 31), randint(1, 31)

        used.append(r1)
        used.append(r2)

        tmp1 = rlayout[r1]
        tmp2 = rlayout[r2]

        layout[tmp2] = r1
        layout[tmp1] = r2

    return layout


current = qwerty
current_score = generate_score(current)
reps = 5000

scores = [current_score]


while reps > 1:
    new = mix(current.copy(), max(reps/1000))
    new_score = generate_score(new)
    if new_score > current_score:
        current = new
        current_score = new_score
    else:
        d = ( new_score - current_score / current_score )
        if random.random() * 500 < (1-d) * reps:
            current = new
            current_score = new_score

    reps -= 1

print(current)
print(current_score)

