#include <iostream>
#include <sstream>
#include <string>

int main() {
    int casos;
    std::cin >> casos;
    std::cin.ignore();

    std::string line;
    for (int i = 0; i < casos && std::getline(std::cin, line); i++) {
        std::istringstream stream(line);
        int cp = 0;
        long long sp = 0;
        int n;

        while (stream >> n) {
            if (n % 2 == 0) {
                cp++;
                sp += n;
            }
        }

        std::cout << cp << " " << sp << "\n";
    }

    return 0;
}
