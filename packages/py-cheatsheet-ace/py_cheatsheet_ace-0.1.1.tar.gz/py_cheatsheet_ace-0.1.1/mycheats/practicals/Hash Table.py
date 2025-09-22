# AIM:- STORE AND RETRIEVE DATA FROM THE HASH TABLE.

# A simple function to decide which "drawer" (index) to use
def hash_func(key):
  return key % 10

# Our filing cabinet with 10 empty drawers
hash_table = [[] for _ in range(10)]

# To put a new file (key-value pair) in the cabinet
def insert(key, value):
  index = hash_func(key)
  hash_table[index].append((key, value))

# To find a file using its key
def search(key):
  index = hash_func(key)
  # Look through the specific drawer for our key
  for k, v in hash_table[index]:
    if k == key:
      return v
  return None # Not found

insert(5, 'Apple')
insert(15, 'Banana') # Banana goes in the same drawer as Apple (15 % 10 = 5)
insert(2, 'Cherry')

print(search(5))
print(search(15))
print(search(2))
