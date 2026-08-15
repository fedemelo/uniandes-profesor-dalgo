import sys


def contar_periodos(cambios: list[int], lower: int, upper: int) -> int:
    prefijos = [0]
    for c in cambios:
        prefijos.append(prefijos[-1] + c)

    return contar_periodos_aux(prefijos, 0, len(prefijos) - 1, lower, upper)


def contar_periodos_aux(prefijos: list[int], lo: int, hi: int, lower: int, upper: int) -> int:
    if lo >= hi:
        return 0

    mid = (hi - lo) // 2 + lo

    left_count = contar_periodos_aux(prefijos, lo, mid, lower, upper)
    right_count = contar_periodos_aux(prefijos, mid + 1, hi, lower, upper)
    merge_count = merge_and_count(prefijos, lo, mid, hi, lower, upper)

    return left_count + right_count + merge_count


def merge_and_count(prefijos: list[int], lo: int, mid: int, hi: int, lower: int, upper: int) -> int:
    left = prefijos[lo:mid + 1]
    right = prefijos[mid + 1:hi + 1]

    lo_ptr = hi_ptr = 0
    periodos_count = 0
    for p in left:
        while lo_ptr < len(right) and right[lo_ptr] < p + lower:
            lo_ptr += 1
        while hi_ptr < len(right) and right[hi_ptr] <= p + upper:
            hi_ptr += 1
        periodos_count += hi_ptr - lo_ptr

    l = 0
    r = 0

    while l < len(left) and r < len(right):
        if left[l] <= right[r]:
            prefijos[lo + l + r] = left[l]
            l += 1
        else:
            prefijos[lo + l + r] = right[r]
            r += 1

    while l < len(left):
        prefijos[lo + l + r] = left[l]
        l += 1

    while r < len(right):
        prefijos[lo + l + r] = right[r]
        r += 1

    return periodos_count


def main() -> None:
    data = sys.stdin.read().split()
    t = int(data[0])
    pos = 1
    salidas = []
    for _ in range(t):
        n = int(data[pos])
        pos += 1
        cambios = [int(x) for x in data[pos:pos + n]]
        pos += n
        lower, upper = int(data[pos]), int(data[pos + 1])
        pos += 2

        salidas.append(str(contar_periodos(cambios, lower, upper)))
    print("\n".join(salidas))


if __name__ == "__main__":
    main()
