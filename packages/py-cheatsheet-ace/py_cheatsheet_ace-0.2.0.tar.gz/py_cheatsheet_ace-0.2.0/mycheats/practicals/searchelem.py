from array import array
arr = array('i', [15, 25, 35, 45, 55])

key = int(input("Enter element to search: "))

found = False # A flag to track if we've found it
# This loop goes through each car's position (index)
for i in range(len(arr)):
  # If the value in the car matches our key...
  if arr[i] == key:
    print(f"Element found at position {i}")
    found = True
    break # ...we can stop looking

if not found:
  print("Element not found")