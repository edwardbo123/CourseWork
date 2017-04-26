# <editor-fold desc="Import">
import random
import pygame
import pygame.freetype
import mysql.connector
from time import time, sleep
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
    help_type = ["easy", "medium", "difficult"]
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
        "Game": {#"Hint": Button(DIMENSIONS["Game"]["Button_left"], 43, 180, 78, give_hint, "Outline", "Hint"),
                 "Save": Button(DIMENSIONS["Game"]["Button_left"], 43*4, 180, 78, save, "Outline", "Save"),
                 "Return to Main Menu": Button(DIMENSIONS["Game"]["Button_left"], 43*7, 180, 78,
                                               swap_screen, "Outline", "Return to \n main menu", "Main"),
                 "Grid": SudokuGrid()},
        "High_Score_Input": {"High_Score_Message": Button(0, 39, 360, 78, None, "Fill",
                                                          colour=pygame.Color(190, 190, 190)),
                             "Get Name": TextBox(90, 7*39, 180, 78, upload_new_high_score)},
        "High_score_Tables": {}
                }
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
        self.text = str(new_text)


class TextBox(Button):
    def __init__(self, left, top, width, height, function, args=None, max_values=10, text="",
                 colour=pygame.Color(0, 0, 0), source=Screen, text_colour=pygame.Color(0, 0, 0)):
        self.left, self.top, self.width, self.height = left, top, width, height
        self.text = text
        self.Colour = colour
        self.source = source
        self.text_colour = text_colour
        self.max_values = max_values
        self.function = function
        self.args = args
        super().__init__(self.left, self.top, self.width, self.height, self.function, "Outline",
                         colour=self.Colour, text_colour=self.text_colour)

    def check_clicked_on(self, loc):
        if self.collidepoint(loc):
            return self, None, None
        else:
            return False, None, None

    def draw(self):
        pygame.draw.rect(self.source, (190, 190, 190), self)
        pygame.draw.rect(self.source, self.Colour, self, 5)
        self.render_font_to_rect(self.text, 16, 1, 0)
        self.update()

    def edit(self, left_click, event):
        if event.key == 8 or event.key == 127 or event.key == 266:
            if len(self.text) > 0:
                self.text = "".join(list(self.text)[:-1])
                self.draw()

        elif event.key == 13:
            self.function(self.text, self.args)
            swap_screen("High_score_Tables")

        elif len(self.text) != 10:
            self.text += event.unicode
            self.draw()

    def set_args(self, new_args_list):
        self.args = new_args_list


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
        global help_type
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
        return [tile.get_value() for tile in self.grid]

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
            row_number, column_number = divmod(index, 9)
            column_number //= 3
            row_number //= 3

        else:
            row_number, column_number = divmod(index, 3)

        column_number *= 3
        row_number *= 3
        sub_grid = [self.grid
                    [column_number+(row_number+row_increment)*9:
                    column_number+(row_number+row_increment)*9+3]
                    for row_increment in range(3)]
        return tuple(sum(sub_grid, []))

    def get_high_score(self):
        return [sum([tile.changes for tile in self.grid]) + self.pre_changes,
                self.pre_time_elapsed + time() - self.start_time]

    def get_grid(self):
        return tuple(self.grid)

    def define_tiles(self):
        SudokuTile.new_index = 0
        for tile in range(81):
            location = self.get_location(tile)
            self.grid.append(SudokuTile(location[1], location[0], ""))

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
        self.set_grid_values(shuffle_grid(get_completed_grid_values()))
        generate_problem(self)

    def write_to_text(self, file):
        with open(file, "w"):
            file.truncate()
            file.write("High score: %s \n" % str(self.highscore))
            file.write("Unchangeable: %s \n" % str([index for index, tile in enumerate(self.grid)
                                                    if tile.editable]))
            file.write("Grid: %s" % str(self.get_all_values()))

    def read_from_file(self, file):
        with open(file, "r"):
            # "High score: " + self.highscore+ " \n" = file.readline() TODO keep working on this
            file.write("Unchangeable: %s \n" % str([index for index, tile in enumerate(self.grid)
                                                    if tile.editable]))
            file.write("Grid: %s" % str(self.get_all_values()))
            file.truncate()

    def is_completed(self):
        tile_values = self.get_all_values()
        if all(tile_values):
            for index, tile_value in enumerate(tile_values):
                tile_values[index] = ""
                if tile_value in tile_values[index % 9::9]:  # If same value in column
                    return False

                if tile_value in tile_values[index//9:(index//9 + 1)*9]:  # If same value in row
                    return False

                column_number, row_number = divmod(index, 9)
                column_number //= 3
                row_number //= 3
                column_number *= 3
                row_number *= 3
                sub_grid = sum([tile_values[(row_number + (column_number + row_increment) * 9):
                                            (row_number + (column_number + row_increment) * 9 + 3)]
                                for row_increment in range(3)], [])
                if tile_value in sub_grid:  # If same value in sub_grid
                    return False

            return True
        else:
            return False


class SudokuTile(Button):  # 40x40 rough guess
    new_index = 0

    def __init__(self, left, top, value, dummy_values=[], editable=True, changes=0):
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

    def set_value(self, value, user_input=False):  # if want use help and stuff (options)
        global buttons
        if user_input:
            self.changes += 1
        self.value = value
        if any(self.dummy_values):
            self.dummy_values = []
        self.change_text(value)
        if buttons["Game"]["Grid"].is_completed() and user_input:
            swap_screen("High_Score_Input")
            return True
        return False

    def set_color(self, new_colour_rgb):
        self.Colour = new_colour_rgb

    def set_text_colour(self, new_colour_rgb):
        self.text_colour = new_colour_rgb

    def set_dummy_values(self, dummy_value, user_input=False, replace_dummies=True):
        # if want use help and stuff (options)
        # dummy_value = int(dummy_value) - 1
        if user_input:
            self.changes += 1
        self.dummy_values = list(self.dummy_values)  # WEW LAD THIS REMOVES POINTERS
        if dummy_value in self.dummy_values:
            self.dummy_values.remove(dummy_value)
        else:
            if len(self.dummy_values) != 0:
                insertion = len(self.dummy_values)
                for index, value in enumerate(self.dummy_values):
                    if dummy_value < value:
                        insertion = index
                        break
                self.dummy_values = self.dummy_values[:insertion] + [dummy_value] + self.dummy_values[insertion:]

            else:
                self.dummy_values = [dummy_value]
        if len(self.dummy_values) == 1 and (not user_input) or replace_dummies:
            self.set_value(self.dummy_values[0])
        else:
            self.value = ""
            self.set_text_for_dummy_values()

    def set_dummy_values_to(self, values, replace_dummies=True):
        if len(values) == 1 and replace_dummies:
            self.value = values[0]
            self.dummy_values = []
        else:
            self.dummy_values = values
            self.value = ""

        self.set_text_for_dummy_values()

    def set_text_for_dummy_values(self):
        text = ""
        for x_index, x_value in enumerate(self.dummy_values):
            if x_value:
                text += str(x_value)

            else:
                text += " "

            text += " "

            if x_index % 3 == 2:
                text += "\n"
        self.change_text(text)

    def edit(self, left_click, event):

        if event.key in range(49, 58):
            number = event.unicode
            if self.editable:
                if left_click:
                    if self.set_value(number, True):
                        self.changes += 1
                        return True
                else:
                    self.set_dummy_values(number, True)
                self.draw()
                self.changes += 1

        elif event.key == 8 or event.key == 127 or event.key == 266:
            if self.editable:
                if self.value:
                    self.value = ""
                elif self.dummy_values:
                    self.dummy_values = self.dummy_values[:-1]
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
    if menu == "High_Score_Input":
        initialise_high_scores(buttons["Game"]["Grid"])
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
# def give_hint(sudoku grid):
#    # TODO work on this after solve_grid
    # views board, randomly selects solvable tile, gives step by step solutions to obtain tile
    # first hint is always fill in dummy values (all the values a tile could be) for every tile
    # next hints will be to optimise dummy tiles, i.e. remove values when doubles
    # ways of solving a tile include:
    # chain rule
    # only possible value for tile
    # only unique number in grid or row/column
#    print("give_hint function incomplete")
#    pass
# </editor-fold>


# <editor-fold desc="Main loop">
def input_handle():
    global last_clicked_on
    while True:
        # print((C.tick()**-1)*100) un-comment for fps
        event = pygame.event.poll()
        if event.type == pygame.MOUSEBUTTONUP:
            handle_click(event.button == 1, pygame.mouse.get_pos())
        elif event.type == pygame.KEYDOWN:  # TODO add backspace i.e. remove most recent value
            try:
                last_clicked_on[0].edit(last_clicked_on[1], event)
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
                except TypeError as e:
                    print(e)
                    pass
            else:
                try:
                    function()
                except TypeError as e:
                    print(e)
                    pass
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


def rotation(array, rotation_angle, length=9):  # uses matrix rotation

    if rotation_angle == 90:
        def rotate_to(x, y):
            new_x = length-1-y
            new_y = x
            return new_y, new_x

        new_array = turn(array, rotate_to, length)
    elif rotation_angle == 180:
        def rotate_to(x, y):
            new_x = length-1-x
            new_y = length-1-y
            return new_y, new_x
        new_array = turn(array, rotate_to, length)
    elif rotation_angle == 270:
        def rotate_to(x, y):
            new_x = y
            new_y = length-1-x
            return new_y, new_x
        new_array = turn(array, rotate_to, length)
    try:  # TODO re-write this
        return new_array
    except NameError:
        return array


def turn(array, rotate_to, length):
    new_array = [None for _ in range(length**2)]
    for index, index_value in enumerate(array):
        y, x = divmod(index, length)
        new_y, new_x = (rotate_to(x, y))
        new_index = new_y*length+new_x
        new_array[new_index] = index_value
    return new_array


def set_random_numbers(array):
    values = [x for x in range(1, 10)]
    random.shuffle(values)
    # set_values = [x for x in range(1, 10)]  # store as alphabet characters
    swap = {x+1: values[x] for x in range(9)}
    new_array = [swap[int(x)] for x in array]
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
def basic_dummy_values(grid, replace_dummies):
    for tile in grid:
        index = tile.get_index()
        for number in range(1, 9):
            if ((number not in grid.get_sub_grid(index)) and (number not in grid.get_row(index)) and
                    (number not in grid.get_coloumn(index))):
                tile.set_dummy_values(number, replace_dummies=replace_dummies)


def get_numbers_appearance_by_index(group):  # WRONG
    return [[row for row in range(len(group)) if number in group[row]] for number in range(1, 10)]


def trivial_dummy_values(grid, replace_dummies):
    for index, tile in enumerate(grid.get_grid()):
        if not tile.get_value():
            row, column, sub_grid = grid.get_row(index), grid.get_column(index), grid.get_sub_grid(index)
            tile_values_to_remove = set((group_tile.get_value() for group_tile in row+column+sub_grid))
            tile_old_dummies = tile.get_dummy_values()
            tile_values = list(set(tile_old_dummies).difference(tile_values_to_remove))
            tile_values.sort()
            if tile_old_dummies != tile_values:
                tile.set_dummy_values_to(tile_values, replace_dummies=replace_dummies)
                return True

    return False


# <editor-fold desc="Tuple solving">
def get_dummy_values_from_tiles(tiles):
    return [tile.get_dummy_values() for tile in tiles]


def solve_through_tuples(group, replace_dummies):
    dummy_values_by_tile = get_dummy_values_from_tiles(group)
    numbers_appearance_by_index = get_numbers_appearance_by_index(dummy_values_by_tile)
    solve_functions = [singles, doubles, triples]
    function_index = 0
    while True:
        function = solve_functions[function_index]
        change = False
        indexes, values = function(dummy_values_by_tile)
        if indexes:
            change = remove_naked_tuples(group, indexes, values, function, replace_dummies)
        else:
            indexes, values = function(numbers_appearance_by_index)
            if indexes:
                change = remove_hidden_tuples(group, indexes, values, replace_dummies)
        if not change:
            if function_index == len(solve_functions)-1:
                return False
            function_index += 1

        else:
            return True


def remove_naked_tuples(group, indexes, values, function, replace_dummies):
    old_group = [tile.get_dummy_values() for tile in group]
    if function == doubles:
        for index, tile in enumerate(group):
            if index not in indexes:
                for value in values:
                    tile_dummies = tile.get_dummy_values()
                    if value in tile_dummies:
                        tile.set_dummy_values(value, replace_dummies=replace_dummies)
    for tile in group:
        tile_dummy_values = tile.get_dummy_values()
        if values in tile_dummy_values and tile != group[indexes]:
            if type(values) == int:
                tile.set_dummy_values(values, replace_dummies=replace_dummies)
            else:
                for values in values:
                    if values in tile_dummy_values:
                        tile.set_dummy_values(values, replace_dummies=replace_dummies)

    if any(old_group[tile_index] != group[tile_index].get_dummy_values() for tile_index in range(len(group))):
        # TODO could be more efficient
        return True
    else:
        return False


def remove_hidden_tuples(group, indexes, values, replace_dummies):  # 10 values that index can be 0 through 9
    old_group = [tile.get_dummy_values() for tile in group]
    if type(indexes) == int and replace_dummies:
        group[indexes].set_value(values+1)
    elif type(indexes) != int:
        for index in indexes:
            group[index].set_dummy_values_to([value+1 for value in values if value+1 in group[index].get_dummy_values()],
                                             replace_dummies=replace_dummies)

    if any(old_group[tile_index] != group[tile_index].get_dummy_values() for tile_index in range(len(group))):
        # TODO could be more efficient
        return True
    else:
        return False


def singles(iter_through):
    overwrite, value = "", ""
    lengths = [len(appearances) for appearances in iter_through]
    if 1 in lengths:
        overwrite = lengths.index(1)
        value = iter_through[overwrite][0]

    return overwrite, value


def doubles(iter_through):
    for index, appearances in enumerate(iter_through):
        index_of_appearances = [index2 for index2, value in enumerate(iter_through) if value == appearances]
        if len(index_of_appearances) == 2 and len(appearances) == 2:
            overwrite = appearances
            values = [index_of_appearance for index_of_appearance in index_of_appearances]
            return [values, overwrite]

    return "", ""


def triples(iter_through):
    # Make it return an argument or pass it through a function where I change the values
    # as the test is identical just the list to test is different
    indexes, value = "", ""
    for index, appearances in enumerate(iter_through):
        if len(appearances) == 3:  # Could do all iteration after the current index as it already checked behind it
            appearances_of_appearances = iter_through.count(appearances)
            # 3 3 3
            if appearances_of_appearances == 3:
                indexes = [index] + \
                          [index2 for index2, value in enumerate(iter_through[index:]) if value == appearances]
                return indexes, appearances

            else:
                subsets = [set(tile).issubset(set(appearances)) if tile and tile != appearances else False
                           for tile in iter_through]
            # 3 3 2
            if appearances_of_appearances == 2 and subsets.count(True)-1 == 1:
                index_of_appearances = [index] + [iter_through[index+1:].index(appearances)]
                subset_index = subsets.index(True)
                indexes = [index_of_appearances + [subset_index] for appearance in appearances
                           if appearance in iter_through[subset_index]]
                return indexes, appearances

            # 3 2 2
            if appearances_of_appearances == 1 and subsets.count(True)-1 == 2:
                subset_indexes = [index2 for index2, value in enumerate(subsets) if value]
                indexes = [[index] + [subset_index for subset_index in subset_indexes
                                        if appearance in iter_through[subset_index]]
                           for appearance in appearances]
                return indexes, appearances

        # 2 2 2
        if len(appearances) == 2 and appearances not in iter_through[index + 1:]:
            other_indexes = [other_index_2d_list_condition(iter_through, appearance, index, length_list)
                             for appearance in appearances]
            if other_indexes[0] and other_indexes[1]:
                other_values = [iter_through[(other_indexes[other_index][0])][1-other_indexes[other_index][1]]
                            for other_index in range(0, 2)]  # TODO doesn't catch all
                # Doesn't catch when there is another tile that would be taken down to hidden single through this i.e.
                # one of the values removed only had two copies on at the time

                if len(other_indexes) == 2 and other_values[0] == other_values[1]:
                    indexes = [other_index[0] for other_index in other_indexes] + [index]
                    values = appearances + [other_values[0]]
                    return indexes, values
    return "", ""


def other_index_2d_list_condition(list_2d, key, start_index, condition):
    for index, list_1d in enumerate(list_2d[start_index+1:]):
        if key in list_1d and condition(list_1d):
            return [start_index + index + 1, list_1d.index(key)]


def length_list(target_list, target=2):
    return len(target_list) == target


def get_sub_grid_from_list(grid, index):  # TODO DELETE THIS
    column_number, row_number = divmod(index, 3)
    column_number *= 3
    row_number *= 3
    sub_grid = [grid
                [row_number + (column_number + row_increment) * 9:
                 row_number + (column_number + row_increment) * 9 + 3]
                for row_increment in range(3)]
    return sum(sub_grid, [])


def check_tuples_duplicates(grid, replace_dummies):  # TODO sort out commenting
    rows = [list(grid.get_row(row, True)) for row in range(9)]
    columns = [list(grid.get_column(column, True)) for column in range(9)]
    sub_grids = [list(grid.get_sub_grid(grid_3x3, True)) for grid_3x3 in range(9)]
    criteria = rows + columns + sub_grids
    for index in range(len(criteria)):
        criterion = criteria[index]
        change = solve_through_tuples(criterion, replace_dummies)
        if change:
            return True
    return False
# </editor-fold>


# <editor-fold desc="Intersection Removal">


def intersection_removal_call(grid, replace_dummies):  # TODO add changes
    rows, columns, subgrids, rotated_subgrids = [], [], [], []
    for index in range(9):
        rows.append(grid.get_row(index, True))
        columns.append(grid.get_column(index, True))
        subgrid = grid.get_sub_grid(index, True)
        subgrids.append(subgrid)
        rotated_subgrids.append(rotation(subgrid, 90, 3))
    rows_columns = rows + columns
    subgrids += rotated_subgrids
    test_groups = [rows_columns] + [subgrids]
    for x in range(18):
        for test_group_index in range(2):
            test_group = get_numbers_appearance_by_index([test_tile.get_dummy_values()
                                                          for test_tile in test_groups[test_group_index][x]])
            tile_index, number = "", ""
            if any(test_group):
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

                    old_dummies = [tile.get_dummy_values() for tile in grid.get_grid()]
                    for tile in group_to_remove_values:
                        if number in tile.get_dummy_values():
                            tile.set_dummy_values(number, replace_dummies=replace_dummies)

                    if [tile.get_dummy_values() for tile in grid.get_grid()] == old_dummies:
                        return True
    return False


def intersection_removal(appearance_grid):
    for index, appearances in enumerate(appearance_grid):
        if len(appearances) in range(2, 4):
            column_appearances = [row_sub_grid_value % 3 for row_sub_grid_value in appearances]
            if column_appearances == column_appearances[0]:# TODO IDK
                return min(appearances), index
    return "", ""
# </editor-fold>
# </editor-fold>


# <editor-fold desc="Generate Problem">
def generate_problem(grid_class):
    # difficulty is a global variable specifying which functions I can use
    list_of_tiles = list(grid_class.get_grid())
    random.shuffle(list_of_tiles)
    blank_tiles = []
    for tile in list_of_tiles:
        value = tile.get_value()
        if list_of_tiles.index(tile) == 80: #TODO delete this
            pass
        tile.set_value("")
        if try_to_solve(grid_class):
            blank_tiles.append(tile)

        else:
            tile.set_value(value)

        for blank_tile in blank_tiles:
            blank_tile.set_value("")

    for tile in list_of_tiles:
        if tile not in blank_tiles:
            tile.change_editable()


def get_state(grid):
    tile_list = grid.get_grid()
    return [[tile_list[x].get_dummy_values() for x in range(81)], [tile_list[x].get_value() for x in range(81)]]


def check_identical_grids(completed_grid, un_completed_grid):
    for index in range(len(completed_grid)):
        if un_completed_grid[index] != "":
            if completed_grid[index] != un_completed_grid[index]:
                return False
    return True


def try_to_solve(grid, replace_dummies=True):
    solving_techniques = [trivial_dummy_values, check_tuples_duplicates, intersection_removal_call]
    # Will be specified by difficulty
    for tile in grid.get_grid():
        if not tile.get_value():
            tile.set_dummy_values_to([x for x in range(1, 10)])
    solving_techniques_index = 0
    while True:
        solving_technique = solving_techniques[solving_techniques_index]
        change = solving_technique(grid, replace_dummies)

        if not change:
            if solving_techniques_index == len(solving_techniques) - 1:
                return False
            solving_techniques_index += 1
        else:
            if all(grid.get_all_values()):
                return True
            solving_techniques_index = 0
# </editor-fold>

# TODO work on making sure grid is correct ie the user has completed the game


# <editor-fold desc="Interaction with SQL server">
def establish_connection():
    global CONNECTION, HOSTS
    # raise EOFError
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
    db.start_transaction(isolation_level='READ COMMITTED')
    cur = db.cursor(buffered=True)
    return [db, cur]


def get_completed_grid_values(connection=establish_connection):  # pull random seed (find a server storage thing)
    # noinspection PyGlobalUndefined
    global TABLE
    [db, cur] = connection()
    cur.execute("SELECT grid FROM " + TABLE + " ORDER BY RAND() LIMIT 1")
    completed_grid_values = cur.fetchall()
    db.close()
    completed_grid_values = list(completed_grid_values[0][0])
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
        "UPDATE " + column + " FROM " + TABLE + " VALUES " + str(field_values) + " WHERE grid = " + grid)


def upload_new_high_score(name, new_high_scores, connection=establish_connection):
    global buttons
    [db, cur] = connection()
    # TODO replace NONE in high_scores_names with the name argument
    high_scores_to_upload = new_high_scores
    new_high_scores = [high_score.replace("None", name) for high_score in new_high_scores]
    for column_number, field_values in enumerate(new_high_scores):
        upload_high_score(cur, "".join(map(str, (buttons["Game"]["Grid"].get_all_values()))), column_number, field_values)
    db.commit()
    db.close()


def check_user_high_score(sudoku_grid, connection=establish_connection):
    global TABLE
    [db, cur] = connection()
    grid = "".join(map(str, sudoku_grid.get_all_values()))
    high_scores, high_scores_names = get_high_scores(cur, TABLE, grid)
    player_changes, player_time = sudoku_grid.get_high_score()
    user_high_scores = [player_changes, player_time]
    if any(high_score for high_score in high_scores):
        new_high_scores = [make_new_top_5(user_high_scores[high_score_index], high_scores[high_score_index],
                                          "None", high_scores_names[high_score_index])
                           for high_score_index in range(2)
                           if user_high_scores[high_score_index] < high_scores[high_score_index][-1]]

    else:
        new_high_scores = [str(user_high_score) + "|" + "None" for user_high_score in user_high_scores]
    # TODO check this
    db.commit()
    db.close()
    return new_high_scores


def get_high_scores(cur, table, grid):  # TODO allow nicknames
    cur.execute("SELECT highTime FROM " + table + " WHERE grid = " + grid)
    high_time = cur.fetchall()
    cur.execute("SELECT highChanges FROM " + table + " WHERE grid = " + grid)
    high_changes = cur.fetchall()
    high_scores = [high_changes + high_time]
    if any(high_score for high_score in high_scores):
        high_scores = [high_score[:high_score.index("|")] for high_score in high_scores]
        high_score_names = [high_score[high_score.index("|")]  for high_score in high_scores]
        return high_scores, high_score_names
    return [], []


def initialise_high_scores(grid):
    global buttons
    new_high_scores = check_user_high_score(grid)
    high_scores_in = ["None" in new_high_scores[index] for index in range(2)]
    if any(high_scores_in):
        buttons["High_Score_Input"]["Get Name"].set_args(new_high_scores)  # get name

        if all(high_scores_in):  # TODO change text displayed
            buttons["High_Score_Input"]["High_Score_Message"].change_text("Well done you  made the leader board for\n"
                                                                          "both speed, and mistakes")
        elif high_scores_in[0]:
            buttons["High_Score_Input"]["High_Score_Message"].change_text("Well done you  made the leader board\n"
                                                                          "for mistakes")
        else:
            buttons["High_Score_Input"]["High_Score_Message"].change_text("Well done you  made the leader\n"
                                                                          "board for speed")
    else:
        swap_screen("High_score_Tables")  # pass in new_high_scores somehow

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
    try:
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
    except FileNotFoundError:
        return False, False

if __name__ == "__main__":
    init_buttons()
    pygame.display.update()
    input_handle()
