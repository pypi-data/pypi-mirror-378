a = [8, 4, 1, 5, 9]
# Loop from the second element of the array
for i in range(1, len(a)):
  key = a[i] # The card we're trying to place
  j = i - 1
  # Move elements of the sorted part that are greater than key
  # to one position ahead of their current position
  while j >= 0 and key < a[j]:
    a[j + 1] = a[j]
    j -= 1
  a[j + 1] = key # Place the key in its correct spot

print("Sorted List:", a)