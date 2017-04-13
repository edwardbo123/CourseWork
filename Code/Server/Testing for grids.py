import itertools
import random
import mysql.connector
from functools import partial

# <editor-fold desc="Connection info">
HOST = "192.168.1.124"
# HOST = "86.166.206.240"
USER = "seedUpload"
PASSWORD = "Lemon26"
DB = 'SudokuDB'
TABLE = "Sudoku_seeds"
CONNECTION = {
    'host': HOST,
    'port': 3306,
    'database': DB,
    'user': USER,
    'password': PASSWORD,
    'charset': 'utf8',
    'use_unicode': True,
    'get_warnings': True,
}
# </editor-fold>


# <editor-fold desc="Test grids functions">
def rotation(rotation_angle, array, length=9):  # uses matrix rotation
    try:
        length = length[0]
    except (AttributeError, TypeError):
        pass
    if rotation_angle == 90:
        def rotate_to(x, y):
            return x, length - y

        rotated_array = turn(array, rotate_to, length)
    elif rotation_angle == 180:
        def rotate_to(x, y):
            return length - y, length - x

        rotated_array = turn(array, rotate_to, length)
    elif rotation_angle == 270:
        def rotate_to(x, y):
            return length - x, y

        rotated_array = turn(array, rotate_to, length)
    try:
        return rotated_array

    except NameError:
        return array


def turn(array, rotate_to, length):
    rotated_array = [None for _ in range((length + 1) ** 2)]
    for index, index_value in enumerate(array):
        y, x = divmod(index, length + 1)
        new_y, new_x = (rotate_to(x, y))
        new_index = new_y * (length + 1) + new_x
        rotated_array[new_index] = index_value
    return rotated_array


def set_numbers(values, array):
    set_values = [x for x in range(1, 10)]  # store as alphabet characters
    swap = {set_values[x]: values[x] for x in range(9)}
    new_array = [swap[int(x)] for x in array]
    return new_array


def grid_column_swap(grid_columns, grid):
    try:
        for y in range(0, 9):
            grid[y*9+grid_columns[0]:y*9+grid_columns[0]+3], grid[y*9+grid_columns[1]:y*9+grid_columns[1]+3] \
                = grid[y*9+grid_columns[1]:y*9+grid_columns[1]+3], grid[y*9+grid_columns[0]:y*9+grid_columns[0]+3]
    except TypeError:
        grid = [element for element in grid]
        for y in range(0, 9):
            grid[y*9+grid_columns[0]:y*9+grid_columns[0]+3], grid[y*9+grid_columns[1]:y*9+grid_columns[1]+3] \
                = grid[y*9+grid_columns[1]:y*9+grid_columns[1]+3], grid[y*9+grid_columns[0]:y*9+grid_columns[0]+3]
        grid = "".join(grid)

    return grid


def grid_row_swap(grid_rows, grid):
    return rotation(270, grid_column_swap(grid_rows, rotation(90, grid)))
# </editor-fold>


def establish_connection(connection_address):
    db = mysql.connector.Connect(**connection_address)
    db.start_transaction(isolation_level='READ COMMITTED')
    cur = db.cursor(buffered=True)
    return [db, cur]


def test_grids(connection, table):
    db = connection[0]
    cur = connection[1]
    cur.execute("SELECT grid FROM " + table)
    uploaded_grids = cur.fetchall()
    uploaded_grids = [uploaded_grid[0] for uploaded_grid in uploaded_grids]
#    random.shuffle(uploaded_grids)
#    uploaded_grids = uploaded_grids[:300]
    column_swaps = [partial(grid_column_swap, z)
                    for z in itertools.permutations([x for x in range(0, 7, 3)], 3)]
    rotations = [partial(rotation, angle) for angle in [0, 90, 180, 270]]
    row_swaps = [partial(grid_column_swap, z)
                 for z in itertools.permutations([x for x in range(0, 7, 3)], 3)]

    number_swaps_indexes = []

    for row_swap_partial in row_swaps:
        for column_swap_partial in column_swaps:
            number_swaps_indexes += ([tuple(map(int, column_swap_partial(row_swap_partial(uploaded_grid[:9]))))
                                      for uploaded_grid in uploaded_grids])

    # number_swaps = [partial(set_numbers, number_swaps_index) for number_swaps_index
    #                 in list(set(tuple(number_swaps_indexes)))]

    number_swaps = [partial(set_numbers, number_swaps_index) for number_swaps_index
                    in (tuple(number_swaps_indexes))]

    number_swaps_per_grid = len(column_swaps) ^ 2
    while len(uploaded_grids) > 1:
        grid = uploaded_grids.pop(0)
        number_swaps = number_swaps[:number_swaps_per_grid]
        for number_swap_partial in number_swaps:
            for row_swap_partial in row_swaps:
                for column_swap_partial in column_swaps:
                    for rotation_partial in rotations:
                        if (row_swap_partial(column_swap_partial(rotation_partial(number_swap_partial(
                                grid)))) in uploaded_grids):
                            return True

    return False


print(str(test_grids(establish_connection(CONNECTION), TABLE)))
