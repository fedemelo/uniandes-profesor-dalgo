import sys


def formas(n, i, j):
    if n == 0: return 1
    if n < 0: return 0
    return formas(n - i, i, j) + formas(n - j, i, j)


def main():
    data = sys.stdin.read().split()
    t = int(data[0])
    pos = 1
    salidas = []
    for _ in range(t):
        i, j, n = (int(x) for x in data[pos:pos + 3])
        pos += 3
        salidas.append(str(formas(n, i, j)))
    print("\n".join(salidas))


if __name__ == "__main__":
    main()