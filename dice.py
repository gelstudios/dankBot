# roll the dice function

import random

def roll_the_dice(stuff = ""):
    if stuff == "": # Empty string handler
        result = "Bro, insert some words to get a random choice, or a number for a random number (1-#)"
    else:
        if stuff[0] == "-": # If the first character of string is "-"
            result = "There's no such thing as a negative die, bro."
        else:
            if stuff.isdigit(): # If the string is all digits, will return true
                size = int(stuff) # Because stuff is a string, we need a integer
                if size == 0: # If the integer is 0
                    result = "Cannot roll 0, bro. Come on, think of a 0 sided die."
                else:
                    result = random.randint(1,size) # Random int from 1 to size
            else: # If not all digits, do other stuff, returns false
                result = random.choice(stuff.split(" ")) # Uses a space as the split sperator
    return str(result)
