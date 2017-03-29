import itertools
import random

# noinspection PyUnresolvedReferences
import MySQLdb

# <editor-fold desc="Connection info">
HOST = "localhost"
UNIX_SOCKET = '/tmp/mysql.sock'
USER = 'Server'
PASSWORD = "Lemon26"
DB = 'SudokuDB'
TABLE = "Sudoku_seeds"
CONNECTION = (HOST, UNIX_SOCKET, USER, PASSWORD, DB, TABLE)


# </editor-fold>
# TODO throw a try except error if no server up
# <editor-fold desc="Initialise the class I use for Trees, used to represent the ID.">


class Node:  # This is a pseudo Tree class, where the only nodes that have data are the leaf nodes,
    # this will be used for the ID of the sudoku grids
    def __init__(self, children):  # TODO Could replace with just lists
        self.children = children

    def get_children(self):  # This will return all of this node's child nodes
        return self.children

    @staticmethod
    def get_type():  # This function will test (when comparing two Trees)
        # if the current object is a node class or a list
        return True


def identical_trees(root1, root2):  # This will check if the two nodes have identical children and
    # thus are identical Sudoku problems
    try:  # TODO re-write this could replace entire thing by just checking 1 value against the list
        if root1.get_type() == root2.get_type():  # If the two objects are part of the Node class,
            #  if not trigger an AttributeError
            for child1, child2 in itertools.product(root1.get_children(), root2.get_children()):
                # Checks if they share the same children
                if child1 == child2:
                    return True
                else:
                    if identical_trees(child1, child2):
                        return True
    except AttributeError:
        if root1 == root2:
            return True


# </editor-fold>

# <editor-fold desc="Code for interacting with the server">


# TODO handle multiple HighScores > 5
def set_cursor(connection):
    conn = MySQLdb.connect(host=connection[0], unix_socket=connection[1],
                           user=connection[2], passwd=connection[3], db=connection[4])
    return conn.cursor()


def upload_seed(cursor, key, grid, table):
    # TODO convert grid into an int and make sure write_key has a good output
    cursor.execute("INSERT INTO " + table + "(seedTree, grid) VALUES ([" + write_key(key) + "],[" + grid + "]")


def write_key(key, string=""):
    for child in key.get_children():
        if child.__class__.__name__ != "Node":
            string += str(child)
        else:
            write_key(child, string)
    return str(string + "\n")


def read_id(key):
    key.find("\n")  # TODO work on this


def get_keys(cursor):
    yield read_id(cursor.execute("SELECT seedTree FROM " + TABLE))


def check_keys(generator, key):
    for gen_id in generator:
        if identical_trees(gen_id, key):
            return True
    else:
        return False


def upload_key(key, grid, connection):
    cursor = set_cursor(connection)
    table = connection[5]
    if not check_keys(get_keys(cursor), key):
        upload_seed(cursor, key, grid, table)


# </editor-fold>

# <editor-fold desc="Generate seed code. Seen in the file of the same name.">


def round_(num, factor):
    return num - (num % factor)


def place_cell(sudoku_grid, c=0):
    column_number, row_number = divmod(c, 9)  # returns column,row
    numbers = [count for count in range(1, 10)]
    random.shuffle(numbers)
    for Number in numbers:
        if ((Number not in sudoku_grid[round_(c, 9):round_(c, 9) + 9]) and
                (Number not in sudoku_grid[row_number::9]) and
                all(Number not in sudoku_grid[round_(row_number, 3) + ((round_(column_number, 3) + count) * 9):
                    round_(row_number, 3) + 3 + ((round_(column_number, 3) + count) * 9)]
                    for count in range(0, 3))):  # checks grid
            sudoku_grid[c] = Number
            if c + 1 >= 81 or place_cell(sudoku_grid, c + 1):
                return sudoku_grid
    else:
        sudoku_grid[c] = None
        return None


def generate_completed_grid():
    sudoku_grid = [None for _ in itertools.repeat(None, 81)]
    return place_cell(sudoku_grid)


# </editor-fold>

# <editor-fold desc="Generate Keys code. Seen in the file of the same name.">


def rotation(array, rotation_angle, length):  # uses matrix rotation
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
    rotated_array = [_ for _ in itertools.repeat(None, (length + 1) ** 2)]
    for index, index_value in enumerate(array):
        y, x = divmod(index, length + 1)
        new_y, new_x = (rotate_to(x, y))
        new_index = new_y * (length + 1) + new_x
        rotated_array[new_index] = index_value
    return rotated_array


def display(array):
    for x in range(9):
        print(array[x * 9:(x + 1) * 9])


def generate_key(grid):
    full_list = []
    check_list = []
    for Index_Tile in range(0, 9):
        for Row in range(0, 3):
            for Tile_Row in range(3):
                check_list[Row * 9 + Tile_Row * 3:Row * 9 + (Tile_Row + 1) * 3] = \
                    grid[(((Index_Tile // 3) + Row) * 9 + Tile_Row * 3 + Index_Tile % 3) * 3:
                         (((Index_Tile // 3) + Row) * 9 + Tile_Row * 3 + 1 + Index_Tile % 3) * 3]
        for Column in range(1, 3):
            for Tile_Row in range(3):
                check_list[27 + (Column - 1) * 9 + Tile_Row * 3:27 + (Column - 1) * 9 + (Tile_Row + 1) * 3] = \
                    grid[((Index_Tile // 3) * 9 + Tile_Row * 3 + (Index_Tile + Column) % 3) * 3:
                         ((Index_Tile // 3) * 9 + Tile_Row * 3 + 1 + (Index_Tile + Column) % 3) * 3]
        check_lists = [check_list,
                       [check_list[9:18] + check_list[:9] + check_list[18:]][0],
                       [check_list[18:27] + check_list[:18] + check_list[27:]][0],
                       [check_list[27:36] + check_list[:27] + check_list[36:]][0],
                       [check_list[36:] + check_list[:36]][0]]
        tile_indexed = []
        for StartIndex in range(len(check_lists)):
            index = [x for x in range(1, 10)]
            for _ in itertools.repeat(None, 3):
                change_dict = {index[x]: x_value for x, x_value in enumerate(check_lists[StartIndex][:9])}
                tile_indexed.append([change_dict[x] for x in check_lists[StartIndex][9:]])
                # noinspection PyTypeChecker
                index = rotation(index, 90, 2)
        full_list.append(tile_indexed)
    return full_list


def get_children(array, verbose=False):
    if verbose:
        print(array)
        print(all([isinstance(value, list) for value in array]))

    if type(array[0]) == list:
        return Node([get_children(child, verbose) for child in array])

    else:
        return array


def generate_seed(grid, verbose=False):
    return get_children(generate_key(grid), verbose)


# </editor-fold>

# <editor-fold desc="Runs the code.">


def run_server(connection):
    grid = generate_completed_grid()
    upload_key(generate_seed(grid), grid, connection)


if __name__ == "main":
    while True:
        run_server(CONNECTION)

# </editor-fold>

# <editor-fold desc="Old code for running the server.">
'''
# client sends a message "Puzzle" to this ip (encryption)
# add code to queue
# This code responds with a seed (and seed index) from a file
# client sends a file received message, timeouts exist.
# Close connection

# client sends "High score, seed index, Difficulty" to this ip (encryption)
# add info to queue
# server sends received, timeout exists back to client ip
# client closes connection

import socket
# import os
import threading
# import pickle
# import random
from threading import Thread
clients = set()
clients_lock = threading.Lock()


def get_puzzle():
    """
    Reads Puzzle file
    gets largest index
    generate random number between 0 and max index
    Returns: Puzzle from index + index which it is from

    """
    pass


def add_high_score(score, index):
    """
    Reads Puzzle file
    find corresponding ID
    write high score to collection of high scores
    strips high score
    generate random number between 0 and max index

    """


def listener(client, address):
    print("Accepted connection from: ", address)
    with clients_lock:  # client
        clients.add(client)
    try: 
        while True:
            data = client.recv(buff)
            if not data:
                break
            elif data == "Puzzle":  # maybe encryption or something
                client.sendall("Puzzle " + get_puzzle)

                # send puzzle + ID
                # waits for message back
                # then close
            elif "High score" in data:  # maybe encryption or something
                # Receive data
                add_high_score(get_puzzle())
                client.sendall("RECEIVED")
#                with clients_lock:
#
#                    for c in clients:
#                        c.sendall(data)
    finally:  # change this
        with clients_lock:
            clients.remove(client)
            client.close()

host, port, buff = "10.0.72.191", 6060, 128

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(3)

th = []
print("Server is listening for connections...")
while True:
    client, address = s.accept()
    th.append(Thread(target=listener, args=(client, address)).start())  # this is a queue
s.close()
'''
# </editor-fold>
