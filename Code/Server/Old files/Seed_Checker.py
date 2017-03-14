import itertools


class Node:  # work on this

    def __init__(self, children):
        self.children = children

    def get_children(self):
        return self.children


def identical_trees(root1, root2):
    try:
        if root1.get_type() == root2.get_type() :
            for child1, child2 in itertools.product(root1.get_children(),root2.get_children()):
                if child1 == child2:
                    return True
                else:
                    if identical_trees(child1,child2):
                        return True
    except AttributeError:
        if root1 == root2:
            return True

