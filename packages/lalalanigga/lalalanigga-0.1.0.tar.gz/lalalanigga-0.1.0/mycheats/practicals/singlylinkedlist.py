# AIM:- CREATE A SINGLY LINKED LIST.

# Create the first clue (the 'head' of the list)
head = {'data': 10, 'next': None}
# Create the second and third clues
second = {'data': 20, 'next': None}
third = {'data': 30, 'next': None}

# Link the clues: head's 'next' points to second, second's 'next' points to third
head['next'] = second
second['next'] = third

# Start the treasure hunt from the beginning
temp = head
print("Linked list: ", end="")

# Keep going as long as there is a next clue to follow
while temp is not None:
  # Print the data at the current clue
  print(temp['data'], end=" -> ")
  # Move to the next clue
  temp = temp['next']

# The last clue points to nothing, ending the hunt
print("None")