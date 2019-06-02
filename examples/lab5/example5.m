x = "a string";
print "outer scope:", x;
{
    x = 100;
    print "inner scope:", x;
}

print "outer scope again:", x;