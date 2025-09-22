a = [10, 3, 7, 1, 9]
n = len(a)
# Outer loop for passes
for i in range(n):
  # Inner loop for comparisons and swaps
  for j in range(0, n - i - 1):
    # If the item on the left is bigger than the item on the right...
    if a[j] > a[j+1]:
      # ...swap them!
      a[j], a[j+1] = a[j+1], a[j]

print("Sorted List:", a)