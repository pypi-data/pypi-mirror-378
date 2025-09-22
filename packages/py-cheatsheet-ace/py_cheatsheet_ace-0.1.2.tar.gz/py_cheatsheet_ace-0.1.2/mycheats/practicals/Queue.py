# AIM:- IMPLEMENT A QUEUE USING AN ARRAY.

# We use a list as our queue
queue = []

# To add an item to the back of the queue
def enqueue(item):
  queue.append(item)

# To remove an item from the front of the queue
def dequeue():
  if not is_empty():
    # .pop(0) removes the FIRST item
    return queue.pop(0)
  else:
    return "Queue is empty"

def is_empty():
  return len(queue) == 0

def display():
  print("Queue:", queue)

enqueue(10)
enqueue(20)
enqueue(30)
display()
print("Removed:", dequeue())
display()