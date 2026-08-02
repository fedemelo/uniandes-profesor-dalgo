import sys


numero_casos = int(sys.stdin.readline())
for __ in range(numero_casos):
    case_list = list(map(int, sys.stdin.readline().split()))
    np = 0
    sp = 0
    for n in case_list:
        if n % 2 == 0:
            np = np + 1
            sp = sp + n
    print(np, sp)

