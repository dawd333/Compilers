x = 1;
while (x < 20) {
    x += 2;

    if (x == 7)
        continue;
    else if (x == 13)
        break;

    print x;
}
print "finished while", x;