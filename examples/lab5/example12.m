A = ones(3, 4);
B = ones(3, 5);
C = [1,2,3,4; 1,2,3,4; 1,2,3,4];

F = [1,2,3,4];

D = A .+ B;
print A, B;
print D;
E = B .+ C;
print E;