# AIM:- IMPLEMENT A STACK USING AN ARRAY.

# We use a simple list as our stack
stack = []

# To add an item to the top of the stack
def push(item):
  stack.append(item)
  print(f"Pushed: {item}")

# To remove an item from the top of the stack
def pop():
  if not stack:
    print("Stack is empty!")
  else:
    # .pop() without an index removes the LAST item
    print(f"Popped: {stack.pop()}")

def display():
  # We reverse the list to show the top item first
  print("Stack (top to bottom):", stack[::-1])

push(10)
push(20)
push(30)
display()
pop()
display()