a = [29, 10, 14, 37, 13]
for i in range(len(a)):
  min_idx = i # Assume the first element is the smallest
  # Loop through the rest of the list to find the actual smallest
  for j in range(i + 1, len(a)):
    if a[j] < a[min_idx]:
      min_idx = j
  # Swap the found minimum element with the first element
  a[i], a[min_idx] = a[min_idx], a[i]

print("Sorted List:", a)