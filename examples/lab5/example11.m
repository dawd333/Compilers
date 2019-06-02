# assignment operators
# binary operators
# transposition
A = 3;
B = [[1]];

C = -A;     # assignemnt with unary expression
A = [[A]];
C = A+B ;   # assignemnt with binary addition
C = A.+B ;  # add element-wise A to B
C = A.-B ;  # substract B from A
C = A.*B ;  # multiply element-wise A with B
C = A./B ;  # divide element-wise A by B

A = 300.0;
B = 5;
C = 0;
C += 10 * B ;  # add B to C
print C, C;
C -= B ;  # substract B from C
print C;
C *= A ;  # multiply A with C
print C;
C /= A ;  # divide A by C
print C;