# <editor-fold desc="Import">
import random
import pygame
import itertools
import pygame.freetype
import mysql.connector
from time import time
# from pygame import *
# import time
# import _mysql
# </editor-fold>
# <editor-fold desc="Initial measurement definitions">
# https://docs.python.org/3/library/functions.html

# global DIMENSIONS, index_help_type, difficulty, HOSTS, CONNECTION
DIMENSIONS = {
    "Main": {"X": 360,
             "Y": 390},
    "Game": {"X": 740,
             "Y": 430,
             "Button_left": 560}}
index_help_type = "Medium"
difficulty = "Medium"
# TODO work on importing difficulty, index_help_type from files and how you work with them in save
# </editor-fold>


# <editor-fold desc="Initialisation">
def init():
    """
    Initialises all the constants and global variables
    """
    pygame.init()
    pygame.freetype.init()
    # noinspection PyGlobalUndefined
    global Screen
    Screen = pygame.display.set_mode((DIMENSIONS["Main"]["X"], DIMENSIONS["Main"]["Y"]))
    Screen.convert_alpha(Screen)
    Screen.fill((190, 190, 190))
    # noinspection PyGlobalUndefined
    global FONT
    FONT = pygame.freetype.Font("comic.ttf")
    # noinspection PyGlobalUndefined
    global last_clicked_on
    last_clicked_on = None
    init_options()


def init_options():  # have option to pull from database
    """
    Initialises all the constants and global variables
    """
    # noinspection PyGlobalUndefined
    global help_type, index_help_type, difficulty
    # help_type = [easy, medium, difficult]  # functions
    help_type = ["easy", "medium", "difficult"]  # TODO replace these with functions
    index_help_type = 1
    difficulty = "Medium"


def init_buttons():
    # noinspection PyGlobalUndefined
    global buttons
    global index_help_type
    global difficulty
    buttons = {
        "Main": {"Start Game": Button(90, 39, 180, 78, swap_screen, "Outline", "Start Game", "Game"),
                 "Options": Button(90, 4*39, 180, 78, swap_screen, "Outline",  "Options", "Options"),
                 "Exit Game": Button(90, 7*39, 180, 78, exit, "Outline", "Exit Game")},
        "Options": {"Starting help": Button(90, 39, 180, 78, change_staring_help, "Outline",
                                            "Starting help ("+help_type[index_help_type]+")"),
                    "difficulty": Button(90, 4*39, 180, 78, change_difficulty, "Outline",
                                         "difficulty ("+str(difficulty)+")"),
                    "Return to Main Menu": Button(90, 7*39, 180, 78, swap_screen, "Outline",
                                                  "Return to \n main menu", "Main")},
        "Game": {"Hint": Button(DIMENSIONS["Game"]["Button_left"], 43, 180, 78, give_hint, "Outline", "Hint"),
                 "Save": Button(DIMENSIONS["Game"]["Button_left"], 43*4, 180, 78, save, "Outline", "Save"),
                 "Return to Main Menu": Button(DIMENSIONS["Game"]["Button_left"], 43*7, 180, 78,
                                               swap_screen, "Outline", "Return to \n main menu", "Main"),
                 "Grid": SudokuGrid()},
        "High_score": {}
                }  # TODO add solve button or append it on to help
    swap_screen("Main")
init()
# </editor-fold>


# <editor-fold desc="Connection info">
HOSTS = ["192.168.1.124", "86.166.206.240"]
# HOST = "10.0.72.132"
USER = "Client"
PASSWORD = "za:cJ)2Hc~Y;%F5r"
DB = 'SudokuDB'
TABLE = "Sudoku_seeds"
CONNECTION = {
    'host': HOSTS[0],
    'port': 3306,
    'database': DB,
    'user': USER,
    'password': PASSWORD,
    'charset': 'utf8',
    'use_unicode': True,
    'get_warnings': True,
}
# </editor-fold>


# <editor-fold desc="Classes">
# Done
class Button (pygame.Rect):
    """
    Class for the on screen buttons (these will be what the user interacts with)
    """
    def __init__(self, left, top, width, height, function, fill_type, text="",
                 args=None, colour=pygame.Color(0, 0, 0), source=Screen, text_colour=pygame.Color(0, 0, 0)):
        super().__init__(self)
        self.left, self.top, self.width, self.height = left, top, width, height
        self.text = text
        self.function = function
        self.fill_type = fill_type
        self.Colour = colour
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

    def calc_font_size(self, text, breaks):
        end_while = False
        increment = 10
        while not end_while:
            font_rect = FONT.get_rect(text, size=increment)
            if font_rect.height > (self.height/(breaks+1)) or font_rect.width > (2/3)*self.width:
                increment -= 1
                end_while = True
            else:
                increment += 1
        return increment

    def update(self):
        pygame.display.update(self)

    def check_clicked_on(self, loc):
        if self.collidepoint(loc):
            return self, self.function, self.args
        else:
            return False, None, None
        
    def change_text(self, new_text):
        self.text = new_text


class SudokuGrid(pygame.Rect):
    """
    Class for the whole Sudoku grid that users with interact with in game
    """
    def __init__(self, source=Screen):
        super().__init__(self)
        self.left, self.top, self.width, self.height = 87, 22, 386, 386
        self.grid = []
        self.source = source
        self.pre_time_elapsed = 0
        self.start_time = int
        self.pre_changes = 0

    def initialise_values(self):
        self.define_tiles()
        tile_values, high_score = load()
        if tile_values:
            for index, tile in enumerate(self.grid):
                if len(tile_values[index][0]) == 1:
                    tile.value = tile_values[index][0]
                else:
                    tile.set_dummy_values([value for value in tile_values[index][0]])
                if tile_values[index][1] == "False":
                    tile.change_editable()
                self.pre_changes = high_score[0]
                self.pre_time_elapsed = high_score[1]
        else:
            self.generate_new_puzzle()

        self.start_time = time()

    def get_all_values(self):
        return [tile.get_value for tile in self.grid]

    def get_column(self, index, column_number=False):
        if not column_number:
            index %= 9
        return tuple(self.grid[index::9])

    def get_row(self, index, row_number=False):
        if not row_number:
            index //= 9
        return tuple(self.grid[index*9:(index+1)*9])

    def get_sub_grid(self, index, grid_number=False):
        if not grid_number:
            column_number, row_number = divmod(index, 9)
            column_number //= 3
            row_number //= 3

        else:
            column_number, row_number = divmod(index, 3)

        column_number *= 3
        row_number *= 3
        sub_grid = [self.grid
                    [row_number+(column_number+row_increment)*9:
                     row_number+(column_number+row_increment)*9+3]
                    for row_increment in range(3)]
        return tuple(sum(sub_grid, []))

    def get_high_score(self):
        return [sum([tile.changes for tile in self.grid]) + self.pre_changes,
                self.pre_time_elapsed + time() - self.start_time]

    def get_grid(self):
        return tuple(self.grid)

    def define_tiles(self):  # TODO continue doc strings
        SudokuTile.new_index = 0
        for tile in range(81):
            location = self.get_location(tile)
            self.grid.append(SudokuTile(location[1], location[0], None))

    def draw(self):
        # noinspection PySimplifyBooleanCheck
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
                return rect, self.highlight_adjacent, [index, pygame.Color(44, 192, 255)]

        else:
            return False, None, None

    def highlight_adjacent(self, index_color):
        [index, color] = index_color
        for tile in list(set(self.get_column(index))
                         .union(set(self.get_row(index)), set(self.get_sub_grid(index)))):
            tile.set_color(color)
            tile.draw()
            tile.update()

    def un_highlight(self, tile):
        self.highlight_adjacent([self.grid.index(tile), pygame.Color(255, 255, 255)])

    def set_grid_values(self, values):
        for index, value in enumerate(values):
            self.grid[index].set_value(value)

    def generate_new_puzzle(self):
        global difficulty
        self.set_grid_values(generate_problem(shuffle_grid(get_completed_grid_values(establish_connection())),
                                              difficulty))

    def write_to_text(self, file):  # TODO use JSON files
        with open(file, "w"):
            file.truncate()
            file.write("High score: %s \n" % str(self.highscore))
            file.write("Unchangeable: %s \n" % str([index for index, tile in enumerate(self.grid)
                                                    if tile.editable]))
            file.write("Grid: %s" % str(self.get_all_values()))

    def read_from_file(self, file):
        with open(file, "r"):
            # "High score: " + self.higscore+ " \n" = file.readline() TODO keep working on this
            file.write("Unchangeable: %s \n" % str([index for index, tile in enumerate(self.grid)
                                                    if tile.editable]))
            file.write("Grid: %s" % str(self.get_all_values()))
            file.truncate()

    def is_completed(self):
        tile_values = self.get_all_values()
        for index, tile_value in enumerate(tile_values):
            if not tile_value:  # If blank
                return False

            if tile_value in tile_values[index % 9::9]:  # If same value in column
                return False

            if tile_value in tile_values[index//9:(index//9 +1)*9]:  # If same value in row
                return False

            column_number, row_number = divmod(index, 3)
            column_number *= 3
            row_number *= 3
            sub_grid = sum([tile_values[(row_number + (column_number + row_increment) * 9):
                                        (row_number + (column_number + row_increment) * 9 + 3)]
                            for row_increment in range(3)], [])
            if tile_value in sub_grid:  # If same value in sub_grid
                return False

        return True


class SudokuTile(Button):  # 40x40 rough guess
    new_index = 0

    def __init__(self, left, top, value, dummy_values=[False for _ in range(9)], editable=True, changes=0):
        self.left, self.top = left, top
        self.function = None
        self.value = value
        self.dummy_values = dummy_values
        self.editable = editable
        self.index = SudokuTile.new_index
        SudokuTile.new_index += 1
        self.text_colour = pygame.Color(0, 0, 0)
        self.Colour = pygame.Color(255, 255, 255)
        super().__init__(self.left, self.top, 40, 40, None, "Fill",
                         colour=self.Colour, text_colour=pygame.Color(0, 0, 0))
        self.changes = changes
        # 40 is tile width/height

    def __hash__(self):
        return hash(self.index)

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
        global buttons
        self.value = value
        self.dummy_values = [False for _ in range(9)]
        self.change_text(value)
        if buttons["Game"][3].is_completed:
            swap_screen("High_score")

    def set_color(self, new_colour_rgb):
        self.Colour = new_colour_rgb

    def set_text_colour(self, new_colour_rgb):
        self.text_colour = new_colour_rgb

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
            self.changes += 1
# </editor-fold>


# <editor-fold desc="Swap Screen">
def swap_screen(menu):
    # noinspection PyGlobalUndefined
    global Screen, DIMENSIONS, current_menu, buttons
    current_menu = menu
    if menu in DIMENSIONS.keys():
        new_screen_size = (DIMENSIONS[menu]["X"], DIMENSIONS[menu]["Y"])
        if menu == "Game":
            buttons[menu]["Grid"].initialise_values()
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
            button.update("all")

# </editor-fold>


# <editor-fold desc="Options menu functions">
# TODO add more options / add a scroll bar
# For scroll bar https://code.google.com/archive/p/ezscroll/downloads
def change_staring_help():
    global help_type, index_help_type
    index_help_type = (index_help_type + 1) % len(help_type)
    buttons["Options"]["Starting help"].change_text("Starting help ("+help_type[index_help_type]+")")
    buttons["Options"]["Starting help"].draw()


def change_difficulty():
    global difficulty, buttons  
    options = ["Easy", "Medium", "Hard", "Fiendish"]
    difficulty = options[(options.index(difficulty)+1) % len(options)]
    buttons["Options"]["difficulty"].change_text("difficulty ("+str(difficulty)+")")
    buttons["Options"]["difficulty"].draw()
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

                # TODO check if user completed
            except AttributeError:
                pass


def handle_click(left_click, mouse_pos):
    global current_menu, buttons, last_clicked_on
    for button in buttons[current_menu].values():
        clicked_on, function, args = button.check_clicked_on(mouse_pos)
        if clicked_on:
            if current_menu == "Game":
                try:
                    buttons["Game"]["Grid"].un_highlight(last_clicked_on[0])
                except ValueError:
                    pass
            last_clicked_on = [clicked_on, left_click]
            if args:
                try:
                    function(args)
                except TypeError:
                    pass
            else:
                function()
# </editor-fold>


# <editor-fold desc="Generate problem from seed">
def shuffle_grid(grid):
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
    new_array = [swap[x] for x in array]
    return new_array


def grid_column_swap(grid):
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
    # difficulty is a global variable specifying which functions I can use
    tile_indexes = [x for x in range(81)]
    random.shuffle(tile_indexes)
    for index in tile_indexes:
        value = grid_class.get_all_values()
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

# TODO work on making sure grid is correct ie the user has completed the game


# <editor-fold desc="Interaction with SQL server">
def establish_connection():
    global CONNECTION, HOSTS
    while True:
        try:
            db = mysql.connector.Connect(**CONNECTION)
        except mysql.connector.errors.InterfaceError:
            if CONNECTION['host'] != HOSTS[1]:
                CONNECTION['host'] = HOSTS[1]
                print("Server unreachable, trying local IP")
                continue
            else:
                print("Server down please try again")
                exit()
        break
    print("Connection established")
    db.start_transaction(isolation_level='READ COMMITTED')
    cur = db.cursor(buffered=True)
    return [db, cur]


def get_completed_grid_values(connection):  # pull random seed (find a server storage thing)
    # noinspection PyGlobalUndefined
    global table
    db = connection[0]
    cur = connection[1]
    cur.execute("SELECT grid FROM " + table + " ORDER BY RAND() LIMIT 1")
    completed_grid_values = cur.fetchall()
    db.close()
    return completed_grid_values


def make_new_top_5(user_score, current_high_scores, user_name, current_names):
    for index, value in enumerate(current_high_scores):
        if user_score > value:
            user_index = index
            break
    new_highs_scores = current_high_scores[:user_index] + user_score + current_high_scores[user_index:]
    new_names = current_names[:user_index] + user_name + current_names[user_index:]
    stuff_to_upload = ["".join(new_highs_scores[index]) + "|" + "".join(new_names[index]) for index in range(5)]
    return stuff_to_upload


def upload_high_score(cur, grid, column_number, field_values):
    if column_number:
        column = "highChange"
    else:
        column = "highTime"

    cur.execute(
        "UPDATE " + column + " FROM " + table + " VALUES" + str(field_values) + "WHERE grid = " + grid)


def check_and_upload_user_high_scores(connection, sudoku_grid):
    global table
    db = connection[0]
    cur = connection[1]
    grid = "".join(sudoku_grid.get_all_values)
    high_scores, high_scores_names = get_high_scores(db, cur, table, grid)
    player_changes, player_time = sudoku_grid.get_high_score()
    user_high_scores = [player_changes, player_time]
    if any(user_high_scores[high_score_index] < high_scores[high_score_index][-1] for high_score_index in range(2)):
        # TODO get user name somehow
        if all(user_high_scores[high_score_index] < high_scores[high_score_index][-1] for high_score_index in range(2)):
            for index, high_score_table in enumerate(high_scores):
                stuff_to_upload = make_new_top_5(player_changes, high_score_table, user_name, high_scores_names[index])
                upload_high_score(cur, grid, index, stuff_to_upload)

        else:
            for index, high_score_table in enumerate(high_scores):
                if user_high_scores[index] < high_score_table[-1]:
                    stuff_to_upload = make_new_top_5(player_changes, high_score_table, user_name,
                                                     high_scores_names[index])
                    upload_high_score(cur, grid, index, stuff_to_upload)
    else:
        # display unfortunately you didn't reach a top score
        pass

    # display top scores
    db.commit()

    db.close()


def get_high_scores(db, cur, table, grid):  # TODO allow nicknames
    cur.execute("SELECT highTime FROM " + table + "WHERE grid = " + grid)
    high_time = cur.fetchall()
    cur.execute("SELECT highChanges FROM " + table + "WHERE grid = " + grid)
    high_changes = cur.fetchall()
    high_scores = [high_changes + high_time]
    high_scores = [[value for value in high_score[:high_score.index("|")]]
                   for high_score in high_scores]
    high_score_names = [[value for value in high_score[high_score.index("|"):]]
                        for high_score in high_scores]
    return high_scores, high_score_names

# </editor-fold>


def save(grid):
    write_to_file = ""
    for tile in grid:
        value = tile.get_value()
        if value:
            write_to_file += str(value) + "|" + str(tile.get_editable())
        else:
            write_to_file += "".join(tile.get_dummy_values) + "|" + "True"
        write_to_file += ","
    write_to_file += "\n"
    high_score = grid.get_high_score()
    write_to_file += str(high_score[0]) + "|" + str(high_score[1])

    # TODO get it to write high scores to file
    with open("Save", 'w') as f:
        f.write(write_to_file)
        f.close()


def load():
    with open("Save", "r+") as f:
        lines = f.readlines()
        if not lines[0]:
            return False
        else:
            tiles_info = lines[0].spilt(',')
            tiles_info = [tile_info.spilt('|') for tile_info in tiles_info]
            high_score = lines[1].spilt('|')
        f.truncate()
        return tiles_info, high_score

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
