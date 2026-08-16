"""
Randomized case generator for homework 2 (dividir y conquistar), for use by
the generate-test-cases skill. Biased toward small-n structural coverage,
max-n performance stress, and extreme-magnitude values (int32-overflow
territory), per the constraints in tex/tarea/entrada-salida.tex:
  1 <= n <= 10^5
  -2^31 <= c_i <= 2^31 - 1
  -10^5 <= l <= u <= 10^5

Writes case_11.in .. case_NN.in to this directory. Run solucion_tarea_2.py
against each to produce the matching .out (the skill does this, not this
script — it does not know what "correct" output is).
"""

import random
from pathlib import Path

OUT_DIR = Path(__file__).parent
START_INDEX = 11

C_MIN, C_MAX = -2**31, 2**31 - 1
L_MIN, U_MAX = -10**5, 10**5
N_MAX = 10**5


def random_range():
    l = random.randint(L_MIN, U_MAX)
    u = random.randint(l, U_MAX)
    return l, u


def small_case(n_max=8, value_max=10):
    n = random.randint(1, n_max)
    c = [random.randint(-value_max, value_max) for _ in range(n)]
    l, u = random_range()
    return n, c, l, u


def large_case(n=N_MAX, extreme_values=False):
    lo, hi = (C_MIN, C_MAX) if extreme_values else (-1000, 1000)
    c = [random.randint(lo, hi) for _ in range(n)]
    l, u = random_range()
    return n, c, l, u


def write_case(index, cases):
    path = OUT_DIR / f"case_{index:02d}.in"
    lines = [str(len(cases))]
    for n, c, l, u in cases:
        lines.append(str(n))
        lines.append(" ".join(map(str, c)))
        lines.append(f"{l} {u}")
    path.write_text("\n".join(lines) + "\n")
    return path


def main():
    random.seed(2)
    index = START_INDEX

    # Small-n batch: broad structural coverage, one bundled test file.
    small_batch = [small_case() for _ in range(30)]
    write_case(index, small_batch)
    index += 1

    # Max-n performance stress, ordinary magnitude values.
    write_case(index, [large_case(n=N_MAX, extreme_values=False)])
    index += 1

    # Max-n performance stress, extreme (int32-boundary) magnitude values.
    write_case(index, [large_case(n=N_MAX, extreme_values=True)])
    index += 1


if __name__ == "__main__":
    main()
