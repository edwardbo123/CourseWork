import Generate_Keys # sort this out
import Puzzle_Generator
def write_id(ID,string = ""): # lists aren't being added to print
    for child in ID.get_children():
        if child.__class__.__name__ != "Node":
##            print(child)
            string += str(child)
        else:
            print(child)
            write_id(child,string)
##    print(string)
    return str(string + "\n")

def read_id(ID):
    ID.find("\n") # work on this

ID = Generate_Keys.run(Puzzle_Generator.generate_completed_grid())
print(write_id(ID))
