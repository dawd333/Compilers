N = 1000;

# skip even numbers, end iteration when over 26
for N = 1 : N / 2 {
    if ((N / 2) * 2 == N)
        continue;
    print N;

    if (N > 26) {
        break;
    }
}