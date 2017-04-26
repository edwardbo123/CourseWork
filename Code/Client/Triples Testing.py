def triples(iter_through):
    """
    The triples function identifies cases where a set of three digits can only be located in three tiles or a set of
    three tiles must contain an arrangement of a set of three digits.
    """
    indexes, value = "", ""
    for index, appearances in enumerate(iter_through):
        if len(appearances) == 3:
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
                print(iter_through)
                print(appearances)
                print(appearances_of_appearances)
                print(subsets)
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
                                for other_index in range(0, 2)]

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

# [[3, 4], [4, 5], [3, 4, 5], [], [], [3, 4, 5], [], [], []] is bad i.e. should not return anything
print(triples([[3, 4], [4, 5], [3, 4, 5], [], [], [3, 4, 5], [], [], []]))