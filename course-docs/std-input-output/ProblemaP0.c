#include <stdio.h>
#include <stdlib.h>

#define MAX_LINE 65536

int main(void) {
    char line[MAX_LINE];

    if (!fgets(line, sizeof(line), stdin)) {
        return 0;
    }
    int casos = atoi(line);

    for (int i = 0; i < casos; i++) {
        if (!fgets(line, sizeof(line), stdin)) {
            break;
        }

        int cp = 0;
        long long sp = 0;
        char *ptr = line;
        char *endptr;

        while (1) {
            long n = strtol(ptr, &endptr, 10);
            if (endptr == ptr) {
                break;
            }
            if (n % 2 == 0) {
                cp++;
                sp += n;
            }
            ptr = endptr;
        }

        printf("%d %lld\n", cp, sp);
    }

    return 0;
}
