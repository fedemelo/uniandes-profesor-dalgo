"""
Randomized case generator for homework 2 (dividir y conquistar), for use by
the generate-test-cases skill. Biased toward small-n structural coverage and
max-n performance/overflow stress, per the constraints in
tex/tarea/entrada-salida.tex:
  1 <= n <= 10^5
  -2^31 <= c_i <= 2^31 - 1
  -10^5 <= l <= u <= 10^5

Writes case_06.in .. case_20.in to this directory, one test case per file
(matching the handcrafted cases' shape). Run solucion_tarea_2.py against each
to produce the matching .out (the skill does this, not this script — it does
not know what "correct" output is).
"""

import random
from pathlib import Path

OUT_DIR = Path(__file__).parent
START_INDEX = 6
SMALL_COUNT = 11
N_MAX = 10**5

C_MIN, C_MAX = -2**31, 2**31 - 1
L_MIN, U_MAX = -10**5, 10**5


def random_range():
    l = random.randint(L_MIN, U_MAX)
    u = random.randint(l, U_MAX)
    return l, u


def small_case(n_max=50, value_max=1000):
    n = random.randint(1, n_max)
    c = [random.randint(-value_max, value_max) for _ in range(n)]
    l, u = random_range()
    return n, c, l, u


def large_case(value_range):
    lo, hi = value_range
    c = [random.randint(lo, hi) for _ in range(N_MAX)]
    l, u = random_range()
    return N_MAX, c, l, u


def write_case(index, n, c, l, u):
    path = OUT_DIR / f"case_{index:02d}.in"
    path.write_text(f"1\n{n}\n{' '.join(map(str, c))}\n{l} {u}\n")
    return path


def main():
    random.seed(2)
    index = START_INDEX

    for _ in range(SMALL_COUNT):
        write_case(index, *small_case())
        index += 1

    # Max-n performance stress, ordinary magnitude values.
    write_case(index, *large_case((-1000, 1000)))
    index += 1

    # Max-n performance stress, extreme (int32-boundary) magnitude values.
    write_case(index, *large_case((C_MIN, C_MAX)))
    index += 1

    # Max-n, mixed ordinary/extreme magnitude values in the same array.
    c = [
        random.choice([random.randint(-1000, 1000), random.randint(C_MIN, C_MAX)])
        for _ in range(N_MAX)
    ]
    l, u = random_range()
    write_case(index, N_MAX, c, l, u)
    index += 1

    # Max-n, ordinary magnitude values but a wide safe range -- pushes the
    # match count up (more work for the merge step's two-pointer scan).
    c = [random.randint(-1000, 1000) for _ in range(N_MAX)]
    write_case(index, N_MAX, c, L_MIN, U_MAX)
    index += 1

    assert index == START_INDEX + SMALL_COUNT + 4 == 21


if __name__ == "__main__":
    main()
