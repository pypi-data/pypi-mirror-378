import numpy as np

nums = input("Enter numbers (separated by spaces): ")
arr = np.array([int(x) for x in nums.split()])

print("Array:", arr)
print("Maximum value:", np.max(arr))
# Corrected the label from "Maximum value" to "Minimum value"
print("Minimum value:", np.min(arr))

print("First element:", arr[0])
print("Third element:", arr[2])
print("Last element:", arr[-1])
# Corrected slice syntax from [:,3] to [:3] for 1D array
print("First three elements:", arr[:3])
print("Last two elements:", arr[-2:])