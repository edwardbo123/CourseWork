# <editor-fold desc="Import">
import random
import pygame
import itertools
import pygame.freetype
import threading
# from pygame import *
# import time
# import _mysql
# </editor-fold>
# TODO Throw a try except if no server up
# <editor-fold desc="Initial measurement definitions">
# https://docs.python.org/3/library/functions.html
# max maybe help Julian
global DIMENSIONS, Index_help_type, difficulty
DIMENSIONS = {
    "Main": {"X": 360,
             "Y": 390},
    "Game": {"X": 740,
             "Y": 430,
             "Button_left": 560}}
Index_help_type = "Medium"
difficulty = "Medium"
# TODO work on importing difficulty, Index_help_type from files and how you work with them in save
# </editor-fold>


# <editor-fold desc="Initialisation">
def init():
    """
    Initialises all the constants and global variables
    """
    pygame.init()
    pygame.freetype.init()
    global Screen
    Screen = pygame.display.set_mode((DIMENSIONS["Main"]["X"], DIMENSIONS["Main"]["Y"]))
    Screen.convert_alpha(Screen)
    Screen.fill((190, 190, 190))
    global FONT
    FONT = pygame.freetype.Font("comic.ttf")
    init_options()
    global stop_loop
    stop_loop = False


def init_options():  # have option to pull from database
    """
    Initialises all the constants and global variables
    """
    global Help_type, Index_help_type, Difficulty
    # Help_type = [easy, medium, difficult]  # functions
    Help_type = ["easy", "medium", "difficult"]  # TODO replace these with functions
    Index_help_type = 1
    Difficulty = "Medium"


def init_buttons():
    global buttons
    global Index_help_type
    global difficulty
    buttons = {
        "Main": {"Start Game": Button(90, 39, 180, 78, "Start Game", swap_screen, "Outline", "Game"),
                 "Options": Button(90, 4*39, 180, 78, "Options", swap_screen, "Outline", "Options"),
                 "Exit Game": Button(90, 7*39, 180, 78, "Exit Game", exit, "Outline")},
        "Options": {"Starting help": Button(90, 39, 180, 78, "Starting help ("+Help_type[Index_help_type]+")",
                                            change_staring_help, "Outline"),
                    "Difficulty": Button(90, 4*39, 180, 78, "Difficulty ("+str(difficulty)+")",
                                         change_difficulty, "Outline"),
                    "Return to Main Menu": Button(90, 7*39, 180, 78, "Return to Main Menu",
                                                  swap_screen, "Outline", "Main")},
        "Game": {"Hint": Button(DIMENSIONS["Game"]["Button_left"], 43, 180, 78, "Hint", give_hint, "Outline"),
                 "Save": Button(DIMENSIONS["Game"]["Button_left"], 43*4, 180, 78, "Save", save, "Outline"),
                 "Return to Main Menu": Button(DIMENSIONS["Game"]["Button_left"], 43*7, 180, 78, "Return to Main Menu",
                                               swap_screen, "Outline", "Main"),
                 "Grid": SudokuGrid()}
                }
    swap_screen(["Main"])
init()
# </editor-fold>


# <editor-fold desc="Classes">
# Done
class Button (pygame.Rect):  # use private increasing values (uuid)
    """
    Class for the on screen buttons (these will be what the user interacts with)
    """
    # TODO sort out multiple lines of text
    def __init__(self, left, top, width, height, text, function, fill_type,
                 args=None, colour=pygame.Color(0, 0, 0), source=Screen, text_colour=pygame.Color(0, 0, 0)):
        super().__init__(self)
        self.left, self.top, self.width, self.height = left, top, width, height
        self.text = text
        self.function = function
        self.fill_type = fill_type  # Consider replacing with fill function
        self.Colour = colour  # Consider replacing with fill function
        self.args = args
        self.source = source
        self.text_colour = text_colour

    def draw(self):
        pygame.draw.rect(self.source, (190, 190, 190), self)
        if self.fill_type == "Outline":
            pygame.draw.rect(self.source, self.Colour, self, 5)
        else:
            pygame.draw.rect(self.source, self.Colour, self)
        self.render_font_to_rect()
        self.update()

    def render_font_to_rect(self):
        end_while = False
        increment = 10
#        font_sizes = FONT.get_sizes()
        while not end_while:
            font_rect = FONT.get_rect(self.text, 0, 0, increment)  # Could me more efficient
            if font_rect.height > self.height or font_rect.width > (2/3)*self.width:
                increment -= 1
                end_while = True
            else:
                increment += 1
        font_rect = FONT.get_rect(self.text, 0, 0, increment)
        FONT.render_to(self.source, (((self.left+self.width/2)-font_rect.width / 2),
                                     (self.top+self.height/2)-font_rect.height / 2),
                       self.text, self.text_colour, None, 0, 0, increment)
#        FONT.render_to(self.source,(0,0),self.text,self.text_colour,None,0,0,increment)

    def update(self):  # maybe do something with this
        pygame.display.update(self)

    def check_clicked_on(self, loc):
        if self.collidepoint(loc):
            return True, self.function, self.args
        else:
            return False, None, None

    def change_text(self, new_text):
        self.text = new_text


class SudokuGrid(pygame.Rect):  # note this could inherit from Button
    """
    Class for the whole Sudoku grid that users with interact with in game
    """
    def __init__(self, source=Screen):
        super().__init__(self)
        self.left, self.top, self.width, self.height = 87, 22, 386, 386
        self.grid = []
        self.source = source

    def get_values(self):
        return [tile.get_value for tile in self.grid]

    def get_column(self, column_no):

        return self.grid[column_no::9]  # returning the sudoku tiles not values

    def get_row(self, row):
        return self.grid[row*9:row*9+9]  # returning the sudoku tiles not values

    def get_grid(self, x, y):
        x *= 3
        y *= 3
#        First_row = [self.grid[x+y*9:x+y*9+4]]
#        Second_row = [self.grid[x+(y+1)*9:x+(y+1)*9+4]]
#        Third_row = [self.grid[x+(y+2)*9:x+(y+2)*9+4]]
        grid_3_by_3 = [self.grid[x+(y+z)*9:x+(y+z)*9+4]for z in range(3)]
#        return First_row+Second_row+Third_row
        return grid_3_by_3

    def define_tiles(self):  # TODO continue doc strings
        for tile in range(81):
            location = self.get_location(tile)
            self.grid.append(SudokuTile(location[1], location[0], None, None, True))

    def draw(self):
        if self.grid == []:
            self.define_tiles()
        pygame.draw.rect(self.source, pygame.Color(0, 0, 0), self)
        for tile in self.grid:
            tile.draw()

    def get_location(self, number_tile):
        # lists reads top, left
        location = [self.top+1, self.left+1]
        number_of_tile_spacing = [number_tile // 9, number_tile % 9]
        large_gaps = [(x//3) + 1 for x in number_of_tile_spacing]
        small_gaps = [number_of_tile_spacing[x]-large_gaps[x] for x in range(len(number_of_tile_spacing))]
        for x in range(len(location)):
            location[x] += large_gaps[x] * 5 + small_gaps[x] + 40 * number_of_tile_spacing[x]
            # 5 is outline spacing of grid, smaller spacing is 1, 40 is the size of the tile
        return location

    def update(self, area):
        if area == "all":
            pygame.display.update(self)
        for tile in self.grid:
            tile.update()

    def check_clicked_on(self, loc):
        if self.collidepoint(loc):
            return True, self.edit_clicked_on_tile_value, loc
        else:
            return False, None, None

    def edit_clicked_on_tile_value(self, args):
        loc = args[0]
        left_click = args[1]
        for tile in self.grid:
            if tile.check_clicked_on(loc):  # TODO add help stuff from menus, Thread and break on Esc or click off
                # TODO maybe change colours of nearby tiles
                # TODO backspace deletes value and removes largest dummy values
                # I think it is a little slow
                if tile.get_editable():
                    tile.edit(left_click)

    def set_grid_values(self, values):
        for index, value in enumerate(values):
            self.grid[index].set_value(value)

    def generate_new_puzzle(self):
        global difficulty
        self.set_grid_values(generate_problem(shuffle_grid(get_seed()), difficulty))


class SudokuTile(Button):  # 40x40 rough guess
    # give index values
    _index = 0  # TODO if no indexes are ever used remove

    def __init__(self, left, top, value, dummy_values, editable):  # width/height needs to be replaced
        self.left, self.top = left, top
        self.text = ""
        self.function = None
        self.value = value
        self.dummy_values = dummy_values
        self.editable = editable
        SudokuTile._index += 1
        self.index = SudokuTile._index
        super().__init__(self.left, self.top, 40, 40, "", None, "Fill", None, pygame.Color(255, 255, 255))
        # 40 is tile width/height
        #  TODO work on this ( function and args are left as blank)

    def get_value(self):
        return self.value

    def get_dummy_values(self):
        return self.dummy_values

    def get_editable(self):
        return self.editable

    def set_value(self, value):  # if want use help and stuff (options)
        self.value = value
        self.dummy_values = []
        self.change_text(value)

    def set_dummy_values(self, *dummy_values):  # dummy_values a 9 long list containing bools
        # if want use help and stuff (options)
        self.dummy_values = [(dummy_values[i] ^ self.dummy_values[i]) for i in range(len(dummy_values))]
        self.value = None
        self.change_text(dummy_values)  # TODO change this after multiple lines of text have been sorted out

    def check_clicked_on(self, loc):
        global change
        if self.collidepoint(loc):
            return True
        else:
            return False

    def edit(self, left_click):
        while True:  # TODO allow mouse clicks to break as well
            numbers,stop = number_input()  # TODO I have move number_input() outside of the class
            if numbers:
                if left_click:
                    self.set_value(numbers[0])
                else:
                    self.set_dummy_values(numbers[0])
                self.draw()
            if stop_loop or stop:
                break

# </editor-fold>


# <editor-fold desc="Swap Screen">
def swap_screen(args):
    menu = args[0]
    global Screen, DIMENSIONS, current_menu
    current_menu = menu
    if menu in DIMENSIONS.keys():
        new_screen_size = (DIMENSIONS[menu]["X"], DIMENSIONS[menu]["Y"])
    else:
        new_screen_size = (DIMENSIONS["Main"]["X"], DIMENSIONS["Main"]["Y"])

    if Screen.get_size() != new_screen_size:
        Screen = pygame.display.set_mode(new_screen_size)
        Screen.fill((190, 190, 190))
        pygame.display.update()

    display_buttons(menu)


def display_buttons(menu):
    global buttons, Screen
    Screen.fill((190, 190, 190))  # could just cover buttons
    for button in buttons[menu].values():
        button.draw()
        try:
            button.update()
        except TypeError:
            button.update("all")  # TODO generate a new problem as well
# </editor-fold>


# <editor-fold desc="Options menu functions">
# TODO add more options / add a scroll bar
# For scroll bar https://code.google.com/archive/p/ezscroll/downloads
def change_staring_help():
    global Help_type, Index_help_type
    Index_help_type = (Index_help_type + 1) % len(Help_type)
    buttons["Options"]["Starting help"].change_text("Starting help ("+Help_type[Index_help_type]+")")
    buttons["Options"]["Starting help"].draw()


def change_difficulty():
    global Difficulty, buttons
    options = ["Easy", "Medium", "Hard", "Fiendish"]
    Difficulty = options[(options.index(Difficulty)+1) % len(options)]
    buttons["Options"]["Difficulty"].change_text("Difficulty ("+str(Difficulty)+")")
    buttons["Options"]["Difficulty"].draw()
# </editor-fold>


# <editor-fold desc="Game functions">
# TODO work on these after working on PI

def number_input():  # TODO do handle changes to function here
    numbers = []
    while not numbers or not stop_loop:
        event = pygame.event.poll()
        if event.type == pygame.KEYDOWN:
            if event.key in range(48, 58):
                numbers.append(event.unicode)
    return numbers, stop_loop


def give_hint(sudokugrid):
    # TODO work on this after solve_grid
    # views board, randomly selects solvable tile, gives step by step solutions to obtain tile
    # first hint is always fill in dummy values (all the values a tile could be) for every tile
    # next hints will be to optimise dummy tiles, i.e. remove values when doubles
    # ways of solving a tile include:
    # chain rule
    # only possible value for tile
    # only unique number in grid or row/column
    print("give_hint function incomplete")
    pass


def solve_grid(sudokugrid):  # solves the grid

    print("solve_grid function incomplete")
    pass
# </editor-fold>


# <editor-fold desc="Main loop">
def main():
    global current_menu, buttons, stop_loop
    pygame.display.update()
    thread = None
    C = pygame.time.Clock()  # un-comment for fps
    C.tick() # un-comment for fps
    while True:
        try:
            print((C.tick()**-1)*100)  # un-comment for fps
        except ZeroDivisionError:
            print(9999999)
        event = pygame.event.poll()
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                left_mouse = True
            else:
                left_mouse = False
            mouse_pos = pygame.mouse.get_pos()
            for button in buttons[current_menu].values(): # TODO this code doesn't work and I don't know why
                clicked_on, function, args = button.check_clicked_on(mouse_pos)
                if clicked_on:
                    try:
                        if thread.is_alive():
                            stop_loop = True
                        print(thread.is_alive())
                    except AttributeError:
                        pass
                    
                    if args:  # Thread the function, then kill it as soon as another function is started
                        new_args = [args, left_mouse]
                        thread = threading.Thread(target=function, args=(new_args, ))
                        thread.start()
                    else:
                        thread = threading.Thread(target=function)
                        thread.start()

                    stop_loop = False


def game_main(sudoku_gird):  # runs the main loop of the sudoku grid
    # TODO work on this
    for tile in sudoku_gird:
        tile.draw()
        tile.update()
    print("sudoku_main function incomplete")
    pass
# </editor-fold>


# <editor-fold desc="Generate problem from seed">
# TODO work on this after pi
def make_SudokuGrid(finished_grid):  # returns sudoku gird in a 1 dimensional array (easy of use)
    global Difficulty
    finished_grid = shuffle_grid(finished_grid)
    problem = generate_problem(finished_grid, Difficulty)
    # display after
    # pull seed
    # generate problem based on difficulty
    ##
    print("make_SudokuGrid function incomplete")
    pass


def shuffle_grid(grid):
    print(grid)
    # some rotations if repeated can dupe keep in mind
    shuffle_type = [rotation, grid_column_swap, set_random_numbers]  # all functions
    # need column_swap
    random.shuffle(shuffle_type)
    for shuffle_method in shuffle_type:
        try: # TODO re-write this
            grid = shuffle_method(grid)
        except TypeError:
            grid = shuffle_method(grid, random.choice([0, 90, 180]))

    return grid
    
    
def rotation(array, rotation_angle):  # uses matrix rotation
    if rotation_angle == 90:
        def rotate_to(x, y):
            new_x = 8-y
            new_y = x
            return new_y, new_x
        
        new_array = turn(array, rotate_to)
    elif rotation_angle == 180:
        def rotate_to(x, y):
            new_x = 8-x
            new_y = 8-y
            return new_y, new_x
        new_array = turn(array, rotate_to)
    elif rotation_angle == 270:
        def rotate_to(x, y):
            new_x = y
            new_y = 8-x
            return new_y, new_x
        new_array = turn(array, rotate_to)
    try: # TODO re-write this
        return new_array
    except NameError:
        return array


def turn(array, rotate_to):
    new_array = [None for _ in itertools.repeat(81)]
    for index, index_value in enumerate(array):
        y, x = divmod(index, 9)
        new_y, new_x = (rotate_to(x, y))
        new_index = new_y*9+new_x
        new_array[new_index] = index_value
    return new_array


def set_random_numbers(array):
    values = [x for x in range(1, 10)]
    random.shuffle(values)
    set_values = [x for x in range(1, 10)]  # store as alphabet characters
    swap = {set_values[x]: values[x] for x in range(9)}
    print(type(array))
    new_array = [swap[x] for x in array]
    return new_array


def grid_column_swap(grid):
    print(grid)
    grid = list(tuple(grid))  # remove pointers
    grid_columns = [0, 3, 6]
    random.shuffle(grid_columns)
    for y in range(0, 9):
        # temp_row = Grid[y*9+Grid_columns[0]:y*9+Grid_columns[0]+3]
        grid[y*9+grid_columns[0]:y*9+grid_columns[0]+3], grid[y*9+grid_columns[1]:y*9+grid_columns[1]+3] \
            = grid[y*9+grid_columns[1]:y*9+grid_columns[1]+3], grid[y*9+grid_columns[0]:y*9+grid_columns[0]+3]
        #  Grid[y*9+Grid_columns[1]:y*9+Grid_columns[1]+3] = temp_row
        return grid


def generate_problem(grid, difficulty):
    # TODO work on this after PI
    pass
# </editor-fold>


# <editor-fold desc="Interaction with SQL server">
# TODO work on this after pi
def get_seed():  # pull random seed (find a server storage thing)
    pass


def submit_high_score_to_server(actions, time, name):
    # submits users high score to server after they finish puzzle
    # id could be pair of name + mac address of computer or just force names to be unqiue
    # like downloading sudoku grids, only do once 100% done
    print("submit_high_score_to_server function incomplete")
    pass
# </editor-fold>


def save():
    # TODO work on this
    # Current state of board = high score + current filled in values + preset values
    #  saves game and then when game is next started asks if want to resume from save
    print("save function incomplete")
    pass

if __name__ == "__main__":
    init_buttons()
    main()

# <editor-fold desc="Test thing">
"""
def test():
    import pygame
    Screen = pygame.display.set_mode((300, 300))
    def run():
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                print(event)
    while True:
        run()
"""
# </editor-fold>
