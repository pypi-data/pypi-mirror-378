a = [10, 20, 30, 40, 50] # MUST BE SORTED
key = 40
low = 0
high = len(a) - 1
found = False

while low <= high:
  mid = (low + high) // 2 # Find the middle index
  if a[mid] == key:
    print("Found at index", mid)
    found = True
    break
  elif key < a[mid]:
    high = mid - 1 # Search the left half
  else:
    low = mid + 1 # Search the right half

if not found:
  print("Not found")