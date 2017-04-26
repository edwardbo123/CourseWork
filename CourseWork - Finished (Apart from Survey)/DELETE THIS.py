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