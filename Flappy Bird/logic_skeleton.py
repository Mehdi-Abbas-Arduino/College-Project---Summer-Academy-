import random

"""
FLAPPY BIRD LOGIC 
==========================================

STUDENTS: Your job is to complete the functions below using the basic python concepts.

The main.py file will use your logic to run the game.
"""

# ==========================================
# FUNCTION 1: DICTIONARIES
# ==========================================
def create_bird():
    """
    Creates the initial state of the bird using a DICTIONARY.
    
    TODO: Return a dictionary with these key-value pairs:
    - 'x': 100 (horizontal position)
    - 'y': 300 (vertical position)
    - 'width': 34
    - 'height': 24
    - 'velocity': 0 (vertical speed, starts at 0)
    
    HINT: Dictionary syntax is {'key': value, 'key': value}
    """
    # TODO: Write your logic here and return the dictionary
    pass


# ==========================================
# FUNCTION 2: CONDITIONALS + DICTIONARIES
# ==========================================
def update_bird(bird, is_jumping):
    """
    Updates the bird's position based on gravity and jumping.
    
    TODO:
    1. Use an IF-ELSE statement to check if 'is_jumping' is True.
       - IF jumping: Set bird['velocity'] to a negative number (e.g., -7) to go UP
       - ELSE: Add 0.4 to bird['velocity'] to apply gravity (pulls DOWN)
    2. Add bird['velocity'] to bird['y'] to update position
    3. Return the updated bird dictionary
    
    CONCEPTS: Conditionals (if/else), Dictionary access
    """
    # TODO: Write your logic here
    pass


# ==========================================
# FUNCTION 3: DICTIONARIES
# ==========================================
def create_pipe(screen_width, screen_height):
    """
    Creates a new pipe using a DICTIONARY and RANDOM numbers.
    
    TODO:
    1. Create a variable 'gap_size' and set it to 200
    2. Use random.randint() to generate a random 'gap_top' value between 50 and (screen_height - gap_size - 50)
    3. Calculate 'gap_bottom' by adding 'gap_size' to 'gap_top'
    4. Return a dictionary with:
       - 'x': screen_width (spawns off-screen on the right)
       - 'width': 60
       - 'gap_top': the random value you generated
       - 'gap_bottom': the calculated value
       - 'passed': False (boolean flag for scoring)
    
    CONCEPTS: Dictionaries, random module, computation
    """
    # TODO: Write your logic here and return the dictionary
    pass


# ==========================================
# FUNCTION 4: LISTS + LOOPS
# ==========================================
def update_pipes(pipes, pipe_speed, screen_width, screen_height):
    """
    Moves all pipes left, removes off-screen pipes, and adds new ones.
    
    TODO:
    1. Use a FOR LOOP to move all pipes: subtract 'pipe_speed' from each pipe's 'x'
    2. Create a NEW empty LIST called 'active_pipes'
    3. Use another FOR LOOP to check each pipe:
       - IF the pipe is still on screen (pipe['x'] + pipe['width'] > 0):
         - Add it to 'active_pipes' using .append()
    4. Use an IF statement to check if we need a new pipe:
       - IF 'active_pipes' is empty OR the last pipe's 'x' < (screen_width - 350):
         - Call create_pipe() and add it to 'active_pipes'
    5. Return the 'active_pipes' list
    
    CONCEPTS: Lists, For loops, Conditionals, List methods (.append)
    """
    # TODO: Write your logic here
    pass


# ==========================================
# FUNCTION 5: NESTED CONDITIONALS + LOOPS
# ==========================================
def check_collision(bird, pipes, screen_height):
    """
    Checks if the bird crashed into floor, ceiling, or pipes.
    
    TODO:
    1. Use an IF statement to check floor/ceiling collision:
       - IF bird['y'] <= 0 OR bird['y'] + bird['height'] >= screen_height:
         - Return True (game over!)
    
    2. Use a FOR LOOP to check each pipe in the 'pipes' list
    3. Inside the loop, use NESTED IF statements:
       - IF bird overlaps horizontally:
         (bird['x'] + bird['width'] > pipe['x'] AND bird['x'] < pipe['x'] + pipe['width'])
         - IF bird hits vertically:
           (bird['y'] < pipe['gap_top'] OR bird['y'] + bird['height'] > pipe['gap_bottom'])
           - Return True (collision!)
    
    4. If no collisions found, return False
    
    CONCEPTS: Nested conditionals, For loops, Boolean logic (AND/OR)
    """
    # TODO: Write your logic here
    pass


# ==========================================
# FUNCTION 6: LOOPS + CONDITIONALS
# ==========================================
def update_score(bird, pipes):
    """
    Checks if the bird passed a pipe to increase the score.
    
    TODO:
    1. Use a FOR LOOP to check each pipe in the 'pipes' list
    2. Inside the loop, use an IF statement to check TWO conditions:
       - The pipe's 'passed' flag is False (not scored yet)
       - The bird has passed the pipe: bird['x'] > pipe['x'] + pipe['width']
    3. IF both conditions are true:
       - Set pipe['passed'] = True (mark as scored)
       - Return 1 (add 1 point)
    4. If loop finishes with no pipe passed, return 0
    
    CONCEPTS: For loops, Conditionals, Boolean flags
    """
    # TODO: Write your logic here
    pass