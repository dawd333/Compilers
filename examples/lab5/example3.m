arr1 = eye(4);
arr2 = ones(4);

print arr1 .+ arr2;
print arr1 .- arr2;

arr3 = arr2 .+ arr2;

print arr1 .* arr3;
print arr3 ./ arr2;
print arr1 .+ arr1 .+ arr2;

arr1 = arr1 .+ arr1;

print "";
print "matrix mul:";
print arr1, " x ";
print arr2, " = ";
print arr1 * arr2;