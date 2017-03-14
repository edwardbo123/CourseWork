# Key Generator code
# work on verbose being global
import itertools


def rotation(array, rotation_angle, length):  # uses matrix rotation
    try:
        length = length[0]
    except (AttributeError, TypeError):
        pass
    if rotation_angle == 90:
        def rotate_to(x, y):
            return x, length-y
        
        rotated_array = turn(array, rotate_to, length)
    elif rotation_angle == 180:
        def rotate_to(x, y):
            return length-y, length-x

        rotated_array = turn(array, rotate_to, length)
    elif rotation_angle == 270:
        def rotate_to(x, y):
            return length-x, y

        rotated_array = turn(array, rotate_to, length)
    try:
        return rotated_array
        
    except NameError:
        return array


def turn(array, rotate_to, length):
    rotated_array = [_ for _ in itertools.repeat(None, (length+1)**2)]
    for index, index_value in enumerate(array):
        y, x = divmod(index, length+1)
        new_y, new_x = (rotate_to(x, y))
        new_index = new_y*(length+1)+new_x
        rotated_array[new_index] = index_value
    return rotated_array


def display(array):
    for x in range(9):
        print(array[x*9:(x+1)*9])


class Node:
    def __init__(self, children):
        self.children = children

    def get_children(self):
        return self.children


def generate_key(grid, verbose=False):
    full_list = []
    check_list = []
    for Index_Tile in range(0, 9):
        for Row in range(0, 3):
            for Tile_Row in range(3):
                check_list[Row*9+Tile_Row*3:Row*9+(Tile_Row+1)*3] = \
                    grid[(((Index_Tile//3)+Row)*9+Tile_Row*3+Index_Tile % 3)*3:
                         (((Index_Tile//3)+Row)*9+Tile_Row*3+1+Index_Tile % 3)*3]
        for Column in range(1, 3):
            for Tile_Row in range(3):
                check_list[27+(Column-1)*9+Tile_Row*3:27+(Column-1)*9+(Tile_Row+1)*3] = \
                    grid[((Index_Tile//3)*9+Tile_Row*3+(Index_Tile+Column) % 3)*3:
                         ((Index_Tile//3)*9+Tile_Row*3+1+(Index_Tile+Column) % 3)*3]
        check_lists = [check_list,
                       [check_list[9:18]+check_list[:9]+check_list[18:]][0],
                       [check_list[18:27]+check_list[:18]+check_list[27:]][0],
                       [check_list[27:36]+check_list[:27]+check_list[36:]][0],
                       [check_list[36:]+check_list[:36]][0]]
        tile_indexed = []
        for StartIndex in range(len(check_lists)):
            index = [x for x in range(1, 10)]
            for _ in itertools.repeat(None, 3):
                change_dict = {index[x]: x_value for x, x_value in enumerate(check_lists[StartIndex][:9])}
                tile_indexed.append([change_dict[x] for x in check_lists[StartIndex][9:]])
                index = rotation(index, 90, 2)
        full_list.append(tile_indexed)
    return full_list


def get_children(array, verbose=False):  # sort this out
    if verbose:
        print(array)
        print(all([isinstance(value, list) for value in array]))
        
    if all([isinstance(value, list) for value in array]):
        return Node([get_children(child, verbose) for child in array])

    else:
        return array  # completely breaks here any reason why?
'''
 this one works (maybe) tested a few and works with rotation/numbers changed (other transformations not tested)
    check_list = [[0 for x in range(9)]for y in range(9)]
    final_list = [0 for x in range(9)]
    for index,value in enumerate(grid):
        y,x = divmod(index,9)
        for test_no in range(4):
            if x == test_no or y == test_no or x == 8-test_no or y == 8-test_no:
                check_list[test_no][value-1] +=1
                break

    for index,count in enumerate(check_list):
        final_list[index] += count.count(2)
        final_list[index] += 2*count.count(3)
        final_list[index] += 3*count.count(4)

    return final_list

 Generates opposites switched ones for rotations, tested on two generated different values
    check_list = [[0 for x in range(9)]for y in range(2)]
    final_list = [0 for x in range(2)]
    for index,value in enumerate(grid):
        y,x = divmod(index,9)
        if x+y == 8:
            check_list[0][value-1] +=1
        if x==y:
            check_list[1][value-1] +=1
    for index,count in enumerate(check_list):
        final_list[index] += count.count(2)
        final_list[index] += 2*count.count(3)
        final_list[index] += 3*count.count(4)
    return final_list
'''


def run(grid, verbose=False):
    return get_children(generate_key(grid, verbose), verbose)


if __name__ == "__main__":
    while True:
        grid = list(eval(input("Meme ")))
        print(run(grid))
