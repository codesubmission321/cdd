#include <string>
#include "Frontend.h"

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <input_file>\n", argv[0]);
        return 1;
    }

    std::string file = argv[1];
    int tokenCount0 = Frontend::count(file) - 1;

    printf("original tokens: %d\n", tokenCount0);

    return 0;
}
