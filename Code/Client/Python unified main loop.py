# <editor-fold desc="Import">
import random
import pygame
import itertools
import pygame.freetype
# from pygame import *
# import time
# import _mysql
# </editor-fold>
# TODO Throw a try except if no server up
# TODO look up mapping
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
    global last_clicked_on
    last_clicked_on = None
    init_options()


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
        "Main": {"Start Game": Button(90, 39, 180, 78, swap_screen, "Outline", "Start Game", "Game"),
                 "Options": Button(90, 4*39, 180, 78, swap_screen, "Outline",  "Options", "Options"),
                 "Exit Game": Button(90, 7*39, 180, 78, exit, "Outline", "Exit Game")},
        "Options": {"Starting help": Button(90, 39, 180, 78, change_staring_help, "Outline",
                                            "Starting help ("+Help_type[Index_help_type]+")"),
                    "Difficulty": Button(90, 4*39, 180, 78, change_difficulty, "Outline",
                                         "Difficulty ("+str(difficulty)+")"),
                    "Return to Main Menu": Button(90, 7*39, 180, 78, swap_screen, "Outline",
                                                  "Return to \n main menu", "Main")},
        "Game": {"Hint": Button(DIMENSIONS["Game"]["Button_left"], 43, 180, 78, give_hint, "Outline", "Hint"),
                 "Save": Button(DIMENSIONS["Game"]["Button_left"], 43*4, 180, 78, save, "Outline", "Save"),
                 "Return to Main Menu": Button(DIMENSIONS["Game"]["Button_left"], 43*7, 180, 78,
                                               swap_screen, "Outline", "Return to \n main menu", "Main"),
                 "Grid": SudokuGrid()}
                } # TODO add solve button or append it on to help
    swap_screen("Main")
init()
# </editor-fold>


# <editor-fold desc="Classes">
# Done
class Button (pygame.Rect):  # use private increasing values (uuid)
    """
    Class for the on screen buttons (these will be what the user interacts with)
    """
    def __init__(self, left, top, width, height, function, fill_type, text="",
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
        self.init_render_font_to_rect()
        self.update()
        
    def init_render_font_to_rect(self):
        font_sizes = []
        breaks = self.text.count("\n")
        temp_text = self.text
        if breaks:
            for _ in range(breaks+1):
                render_text, temp_text = temp_text[:temp_text.index("\n")], temp_text[temp_text.index("\n"):]
                font_sizes.append(self.calc_font_size(render_text, breaks))
            font_size = min(font_sizes)
            temp_text = self.text
            for count in range(1, breaks+2):
                try:
                    render_text, temp_text = temp_text[:temp_text.index("\n")], temp_text[temp_text.index("\n")+1:]
                    self.render_font_to_rect(render_text, font_size, count, breaks)
                except ValueError:
                    self.render_font_to_rect(temp_text, font_size, count, breaks)

        else:
            font_size = self.calc_font_size(self.text, 0)
            self.render_font_to_rect(self.text, font_size, 1, 0)

    def render_font_to_rect(self, text, font_size, count, breaks):
        font_rect = FONT.get_rect(text, size=font_size)
        FONT.render_to(self.source, (((self.left+self.width / 2)-font_rect.width / 2),
                                     (self.top+(self.height*count/(breaks+2)))-(font_rect.height / 2)),
                       text, self.text_colour, size=font_size)
#        FONT.render_to(self.source,(0,0),self.text,self.text_colour,None,0,0,increment)

    def calc_font_size(self, text, breaks):
        end_while = False
        increment = 10
#        font_sizes = FONT.get_sizes()
        while not end_while:
            font_rect = FONT.get_rect(text, size=increment)  # Could me more efficient
            if font_rect.height > (self.height/(breaks+1)) or font_rect.width > (2/3)*self.width:
                increment -= 1
                end_while = True
            else:
                increment += 1
        return increment

    def update(self):  # maybe do something with this
        pygame.display.update(self)

    def check_clicked_on(self, loc):
        if self.collidepoint(loc):
            return self, self.function, self.args
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

    def get_column(self, index, column_number=False):
        if not column_number:
            index //= 9
        return self.grid[index::9]  # returning the sudoku tiles not values

    def get_row(self, index, row_number=False):
        if not row_number:
            index //= 9
        return self.grid[index*9:(index+1)*9]

    def get_sub_grid(self, index, grid_number=False):
        if not grid_number:
            column_number, row_number = divmod(index, 9)
            column_number //= 3
            row_number //= 3

        else:
            column_number, row_number = divmod(index, 3)

        column_number *= 3
        row_number *= 3
#        First_row = [self.grid[x+y*9:x+y*9+4]]
#        Second_row = [self.grid[x+(y+1)*9:x+(y+1)*9+4]]
#        Third_row = [self.grid[x+(y+2)*9:x+(y+2)*9+4]]
        grid_3_by_3 = [self.grid
                       [column_number+(row_number+row_increment)*9:
                        column_number+(row_number+row_increment)*9+4]
                       for row_increment in range(3)]
        return grid_3_by_3 # TODO WRONG

    def get_grid(self):
        return self.grid

    def define_tiles(self):  # TODO continue doc strings
        for tile in range(81):
            location = self.get_location(tile)
            self.grid.append(SudokuTile(location[1], location[0], None))

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
        for index, rect in enumerate(self.grid):
            if rect.collidepoint(loc):
                print("START TEST", self.get_column(index))
                print(set(self.get_column(index))) #ERROR
                for tile in list(set(list(self.get_column(index)))
                                 .union(list(self.get_row(index)), list(self.get_sub_grid(index)))):
                    tile.set_colour([44, 192, 255])
                return rect, None, loc

        else:
            return False, None, None

    def set_grid_values(self, values):
        for index, value in enumerate(values):
            self.grid[index].set_value(value)

    def generate_new_puzzle(self):
        global difficulty
        # self.set_grid_values(generate_problem(shuffle_grid(get_seed()), difficulty))
        self.set_grid_values(shuffle_grid(eval(input("81 long list"))))
        generate_problem(self)


class SudokuTile(Button):  # 40x40 rough guess
    new_index = 0

    def __init__(self, left, top, value, dummy_values=[False for _ in range(9)], editable=True):
        self.left, self.top = left, top
        self.function = None
        self.value = value
        self.dummy_values = dummy_values
        self.editable = editable
        self.index = SudokuTile.new_index
        SudokuTile.new_index += 1
        self.text_colour = pygame.Color(0, 0, 0)
        self.Colour = pygame.Color(255, 255, 255)
        super().__init__(self.left, self.top, 40, 40, None, "Fill", colour=self.Colour, text_colour=pygame.Color(0, 0, 0))
        # 40 is tile width/height

    def get_value(self):
        return self.value

    def get_index(self):
        return self.index

    def get_dummy_values(self):
        return self.dummy_values

    def get_dummy_list(self):
        dummy_list = []
        for index, test in enumerate(self.dummy_values):
            if test:
                dummy_list.append(index)
        return dummy_list

    def get_editable(self):
        return self.editable

    def change_editable(self):
        self.editable = not self.editable

    def set_value(self, value):  # if want use help and stuff (options)
        self.value = value
        self.dummy_values = [False for _ in range(9)]
        self.change_text(value)

    def set_colour(self, new_colour_rgb):
        self.colour = pygame.Color(new_colour_rgb)
        self.text_colour = pygame.Color(map(minus_255,new_colour_rgb))

    def set_dummy_values(self, dummy_value):
        # if want use help and stuff (options)
        dummy_value = int(dummy_value) - 1
        self.dummy_values = list(self.dummy_values)  # WEW LAD THIS REMOVES POINTERS
        self.dummy_values[dummy_value] = not self.dummy_values[dummy_value]
        self.value = None
        text = ""
        for x_index, x_value in enumerate(self.dummy_values):
            if x_value:
                text += str(x_index+1)

            else:
                text += " "

            text += " "

            if x_index % 3 == 2:
                text += "\n"
        self.change_text(text)

    def set_dummy_values_to(self, values):
        self.dummy_values = values
        self.value = None

    def edit(self, left_click, number):
        # TODO highlight this and other tiles in like a cross
        if self.editable:
            if left_click:
                self.set_value(number)
            else:
                self.set_dummy_values(number)
            self.draw()
# </editor-fold>


def minus_255(number):
    return 255-number

# <editor-fold desc="Swap Screen">
def swap_screen(menu):
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
def input_handle():
    global last_clicked_on
    while True:
        # print((C.tick()**-1)*100) un-comment for fps
        event = pygame.event.poll()
        if event.type == pygame.MOUSEBUTTONUP:
            handle_click(event.button == 1, pygame.mouse.get_pos())
        elif event.type == pygame.KEYDOWN and event.key in range(49, 58):
            try:
                last_clicked_on[0].edit(last_clicked_on[1], event.unicode)
            except AttributeError as e:
                print(e, dir(last_clicked_on))
                pass


def handle_click(left_click, mouse_pos):
    global current_menu, buttons, last_clicked_on
    for button in buttons[current_menu].values():
        clicked_on, function, args = button.check_clicked_on(mouse_pos)
        print(clicked_on)
        if clicked_on:
            last_clicked_on = [clicked_on, left_click]
            print(last_clicked_on)
            if args:
                try:
                    function(args)
                except TypeError:
                    pass
            else:
                function()


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
def shuffle_grid(grid):
    print(grid)
    # some rotations if repeated can dupe keep in mind
    shuffle_type = [rotation, grid_column_swap, set_random_numbers]  # all functions
    # need column_swap
    random.shuffle(shuffle_type)
    for shuffle_method in shuffle_type:
        try:

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
# </editor-fold>


# <editor-fold desc="Solve Sudoku problems">
# TODO check all of these functions not sure any of them work
# TODO still haven't put in automatic dummy values
def basic_dummy_values(grid):
    for tile in grid:
        index = tile.get_index()
        for number in range(1, 9):
            if ((number not in grid.get_sub_grid(index)) and (number not in grid.get_row(index)) and
                    (number not in grid.get_coloumn(index))):

                tile.set_dummy_values(number)


def get_numbers_appearance_by_index(group):
    return [[row for row in range(len(group)) if number in group[row]] for number in range(1, 10)]


def trivial_dummy_values(grid):
    for index, tile in enumerate(grid):
        tile_values = [x for x in range(1, 10)]
        row, column, sub_grid = grid.get_row(index), grid.get_column(index), grid.get_sub_grid(index)
        iter_through = list(set(row).union(set(column), set(sub_grid)))
        tile_values = list(set(tile_values).difference(iter_through))
        tile.set_dummy_values(tile_values)


# <editor-fold desc="Tuple solving">
def get_dummy_values_from_tiles(tiles):
    return [tile.get_dummy_values() for tile in tiles]


def solve_through_tuples(group):
    numbers_appearance_by_index = get_numbers_appearance_by_index(group)
    dummy_values_by_tile = get_dummy_values_from_tiles(group)
    solve_functions = [singles, doubles, triples]
    for function in solve_functions:
        index, value = function(numbers_appearance_by_index)  # TODO double check all of this
        if index:
            remove_naked_tuples(group, value, index)
        else:
            value, index = function(dummy_values_by_tile)
            if index:
                remove_hidden_tuples(group, value, index)


def remove_naked_tuples(group, value, index):
    old_group = list(group)
    for tile in group:
        tile_dummy_values = tile.get_dummy_values()
        if value in tile_dummy_values and tile != group[index]:
            if type(value) == int:
                tile_dummy_values.set_dummy_values(value)
            else:
                tile_dummy_values.set_dummy_values([values for values in value if values in tile_dummy_values])

    if old_group != group:
        return False  # If no change set flag
    else:
        return True  # If no change set flag


def remove_hidden_tuples(group, value, index):
    old_group = list(group)
    if type(index) == int:
        group[index].set_value_to(value)
    else:
        for count in range(len(index)):
            group[index[count]].set_value_to(index[count])
    if old_group != group:
        return False  # If no change set flag
    else:
        return True # If no change set flag


def singles(iter_through):
    overwrite, value = None, None
    lengths = [len(appearances) for appearances in iter_through]
    if 1 in lengths:
        overwrite = lengths.index(1)
        value = lengths.index(1)
        return overwrite, value


def doubles(iter_through):
    overwrite, value = None, None
    for index, appearances in enumerate(iter_through):
        index_of_appearances = [index2 for index2, value in iter_through if index2 == appearances]
        if len(index_of_appearances) == 2 and len(appearances) == 2:
            overwrite = appearances
            values = index_of_appearances
            return [overwrite, values]


def triples(iter_through):
    # Make it return an argument or pass it through a function where I change the values
    # as the test is identical just the list to test is different
    overwrite, value = None, None
    for index, appearances in enumerate(iter_through):
        if len(appearances) == 3:  # Could do all iteration after the current index as it already checked behind it
            appearances_of_appearances = iter_through.count(appearances)
            # 3 3 3
            if appearances_of_appearances == 3:
                overwrite = [index] + \
                          [index2 for index2, value in enumerate(iter_through[index:]) if value == appearances]
                values = appearances
                return overwrite, values

            else:
                subsets = [set(tile).issubset(set(appearances)) for tile in iter_through]
            # 3 3 2
            if appearances_of_appearances == 2 and subsets.count(True)-1 == 1:
                index_of_appearances = [index] + [iter_through[index:].index(appearances)]
                subset_index = subsets.index(True)
                overwrite = [index_of_appearances + [subset_index] for appearance in appearances
                             if appearance in iter_through[subset_index]]
                values = appearances
                return overwrite, values

            # 3 2 2
            if appearances_of_appearances == 1 and subsets.count(True)-1 == 2:
                subset_indexes = [index2 for index2, value in enumerate(subsets) if value]
                overwrite = [[index] + [subset_index for subset_index in subset_indexes
                                        if appearance in iter_through[subset_index]]
                             for appearance in appearances]
                values = appearances
                return overwrite, values

        # 2 2 2
        if len(appearances) == 2: #TODO TEST this
            other_indexes = [index_2d_list_condition(iter_through, appearance, length_list)
                             for appearance in appearances]
            other_values = [iter_through[(other_indexes[index][0])][1-other_indexes[index][1]]
                            for index in range(0, 2)]  # TODO doesn't catch all
            # Doesn't catch when there is another tile that would be taken down to hidden single through this i.e.
            # one of the values removed only had two copies on at the time

            if len(other_indexes) == 2 and other_values[0] == other_values[1]:
                overwrite = [index + other_index for other_index in other_indexes for appearance in appearances
                             if appearance in iter_through[other_index]] + other_indexes
                values = appearances + [other_values]
                return overwrite, values


def index_2d_list_condition(list_2d, key, condition):
    for index, list_1d in enumerate(list_2d):
        if key in list_1d and condition(list_1d):
            return [index, list_1d.index(key)]


def length_list(target_list, target=2):
    return len(target_list) == target


def check_tuples_duplicates(grid):
    rows = [[tile for tile in grid.get_row(row)] for row in range(9)]
    columns = [[tile for tile in grid.get_coloumn(column)] for column in range(9)]
    grids_3_x_3 = [[tile for tile in grid.get_sub_grid(grid_3x3)] for grid_3x3 in range(9)]
    criteria = [rows, columns, grids_3_x_3]
    for criterion in criteria:
        solve_through_tuples(criterion)
# </editor-fold>


# <editor-fold desc="Intersection Removal">


def intersection_removal_call(grid):
    rows, columns, subgrids, rotated_subgrids = [], [], []
    for index in range(9):
        rows.append(grid.get_row(index, True))
        columns.append(grid.get_column(index, True))
        subgrid = grid.get_subgrids(index, True)
        subgrids.append(subgrid)
        rotated_subgrids.append(rotation(subgrid, 90))

    rows_columns = rows + columns
    subgrids = subgrids + rotated_subgrids
    Test_groups = [rows_columns] + [subgrids]
    for x in range(18):
        for test_group_index in range(2):
            test_group = get_numbers_appearance_by_index(Test_groups[test_group_index][x].get_dummy_values())
            tile_index, number = None, None
            tile_index, number = intersection_removal(test_group)
            if number:
                if test_group_index == 0:
                    if x in range(9):
                        grid_index = tile_index//3 + (x//3)*3

                    else:
                        grid_index = x//3 + (tile_index//3)*3

                    group = grid.get_sub_grid(grid_index, True)
                    group_to_remove_values = group[:x % 3] + group[(x + 1) % 3:]

                else:
                    if x in range(9):
                        row_index = tile_index//3 + (x//3)*3
                        group = grid.get_row(row_index, True)
                        group_to_remove_values = group[:x % 3] + group[(x + 1) % 3:]

                    else:
                        column_index_in_3_block = tile_index//3 + (x%3)*3
                        group = grid.get_column(column_index_in_3_block, True)
                        group_to_remove_values = group[:x // 3] + group[(x + 1) // 3:]

                for tile in group_to_remove_values:
                    if number in tile.get_dummy_values():
                        tile.set_dummy_values(number)


def intersection_removal(appearance_grid):
    for index, appearances in enumerate(appearance_grid):
        if len(appearances) in range(2, 4):
            column_appearances = [row_sub_grid_value % 3 for row_sub_grid_value in appearances]
        if all(column_appearances == column_appearances[0]):
            return min(appearances), index

# </editor-fold>


# <editor-fold desc="Generate Problem">
def generate_problem(grid_class):
    # Difficulty is a global variable specifying which functions I can use
    tile_indexes = [x for x in range(81)]
    random.shuffle(tile_indexes)
    for index in tile_indexes:
        value = grid_class.get_values()
        grid_class.set_value(index, None)
        if not try_to_solve(grid_class):
            grid_class.set_value(index, value)

    for tile in grid_class.get_grid():
        if tile.get_value:
            tile.change_editable()


def get_state(grid):
    return [[grid.get_dummy_value(x) for x in range(81)], [grid.get_value(x) for x in range(81)]]


def try_to_solve(grid):
    solving_techniques = [trivial_dummy_values, solve_through_tuples, intersection_removal_call]
    # Will be specified by difficulty
    completed = False
    while not completed:
        [old_dummies, old_values] = get_state(grid)
        for solving_technique in solving_techniques:
            grid = solving_technique(grid)
            if [old_dummies, old_values] != get_state(grid):
                break
                
            if all(grid.get_value(tile_index) for tile_index in range(81)):
                return completed
            
            elif solving_technique == solving_techniques[-1]:
                return False
        solving_techniques.pop(0)

# </editor-fold>

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


def save(grid):
    write_to_file = ""
    for tile in grid:
        value = tile.get_value()
        if value:
            write_to_file += str(value), str(tile.get_editable())
        else:
            write_to_file += str(tile.get_dummy_values()), True
        write_to_file += ","
    write_to_file += "\n"
    # TODO get it to write high scores to file
    with open("Save", 'w') as f:
        f.write(write_to_file)
        f.close()


if __name__ == "__main__":
    init_buttons()
    pygame.display.update()
    input_handle()

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
