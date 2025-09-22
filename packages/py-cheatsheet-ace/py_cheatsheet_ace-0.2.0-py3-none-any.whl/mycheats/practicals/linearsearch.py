a = [10, 20, 30, 40, 50]
key = 20
found = False
for i in range(len(a)):
  if a[i] == key:
    print("Found at index", i)
    found = True
    break
if not found:
  print("Not found")