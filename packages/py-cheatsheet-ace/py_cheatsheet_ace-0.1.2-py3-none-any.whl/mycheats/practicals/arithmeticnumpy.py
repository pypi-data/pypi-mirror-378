import numpy as np

a = input("Enter 3 numbers for array 1 (separated by spaces): ")
b = input("Enter 3 numbers for array 2 (separated by spaces): ")

# Assuming input numbers are separated by spaces
arr1 = np.array([int(x) for x in a.split()])
arr2 = np.array([int(x) for x in b.split()])

print("Array 1:", arr1)
print("Array 2:", arr2)

print("Addition:", arr1 + arr2)
print("Substraction:", arr2 - arr1)
print("Multiplication:", arr1 * arr2)
print("Division:", arr1 / arr2)