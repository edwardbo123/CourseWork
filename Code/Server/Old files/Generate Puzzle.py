import random
import itertools


# Sudoku grid 81 long
Sudoku_index = [x for x in range(0, 81)]


def round_(num, factor):
    return num - (num % factor)


def place_cell(c=0):
    global sudoku_grid
    column_number, row_number = divmod(c, 9)  # returns column,row
    numbers = [count for count in range(1, 10)]
    random.shuffle(numbers)
    for Number in numbers:
        if ((Number not in sudoku_grid[round_(c, 9):round_(c, 9)+9]) and
            (Number not in sudoku_grid[row_number::9]) and
           all(Number not in sudoku_grid[round_(row_number, 3)+((round_(column_number, 3)+count)*9):
                                         round_(row_number, 3)+3+((round_(column_number, 3)+count)*9)]
               for count in range(0, 3))):  # checks grid
            sudoku_grid[c] = Number
            if c+1 >= 81 or place_cell(c+1):
                return sudoku_grid
    else:
        sudoku_grid[c] = None
        return None


def generate_completed_grid():
    # use self recursion + and as grids are randomised use self recursion
    # i.e. if error back track until works, itertools.product, check against row,column,cell
    global sudoku_grid
    sudoku_grid = [None for _ in itertools.repeat(None, 81)]
    return place_cell()
"""
    sudoku_grid = [None for x in range(0,81)]
    for Number in range(1,10):
        row_number_list = [x for x in range(0,9)]
       column_number_list = [x for x in range(0,9)]
        while row_number_list:
           column_number = random.choice(column_number_list)   ## make more efficient by temp removing values temp
            if sudoku_grid[row_number_list[0]+column_number*9] == None:
                sudoku_grid[row_number_list[0]+column_number*9] = Number
                row_number_list.pop(0)
               column_number_list.remove(column_number)
            display_grid(sudoku_grid)
            ## this way can get stuck in infinite loop
    ##ways of doing this
    ## randomly fill a grid with 9 1's, 9 2's etc. and shuffle, then check for errors, if errors exist shuffle again
    ## or randomly fill in the grid with tiles that obey the rules if doesn't work, just restart
 source this http://codereview.stackexchange.com/questions/88849/sudoku-puzzle-generator
    ## first attempt
"""


# def save_to_file(filename, grid):
#    with open(filename, 'a', newline='') as csvfile:
#        top_writer = csv.writer(csvfile, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
#        top_writer.writerow([name]+[value])


global sudoku_grid
if __name__ == "__main__":
    while True:
#        sudoku_grid = generate_completed_grid()
        print(generate_completed_grid())
# write_to_file(sudoku_grid,Difficulty)

    
# order:
# generate grid seed
# upload seed
# check for dupes
# take seed down on main thing, generate grid based on difficuity (techniques used to backtrack determine difficulty)
# then upload scores with given difficuilty
# THIS PAPER MAKES ME HYPED http://zhangroup.aporc.org/images/files/Paper_3485.pdf    
# http://www.sudokuwiki.org/sudoku.htm
