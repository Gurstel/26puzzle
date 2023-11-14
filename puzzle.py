# Omar Shalaby
# CS 4613
# Project 1: 26-Puzzle Problem

from queue import PriorityQueue
import copy
import os

# Node object that has a state, parent, action, path cost from a root node, the estimated heurstic cost to the goal node,
# and specific to the puzzle, where it's empty position (marked by a "0") is for  easier computations in node expansion
class Node:
    def __init__(self, state, empty_pos, parent, action, path_cost, heuristic_cost):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.heuristic_cost = heuristic_cost
        self.empty_pos = empty_pos

    # A node is considered less than another node if f(n) of the node is less than that of the other node
    def __lt__(self, other):
        return (self.path_cost + self.heuristic_cost) < (
            other.path_cost + other.heuristic_cost
        )


# This function takes in an initial state, goal state, and the initial states empty position
# and performs A* search to find the most cost optimal path from the initial state to the goal state
def astar(initial_state, goal_state, empty_pos):
    root_node = Node(
        initial_state, empty_pos, None, None, 0, heuristic(initial_state, goal_state)
    )
    frontier = PriorityQueue()
    frontier.put(root_node)
    reached = set()
    reached.add(root_node)
    while not frontier.empty():
        node = frontier.get()
        if node.state == goal_state:
            return node, len(reached)
        for child in expand(node, goal_state):
            if child not in reached:
                frontier.put(child)
                reached.add(child)
    return None, len(reached)


# This function takes in a node and the goal state and returns all possible
# and legal child nodes branching from the given node. It tries all possible actions
# and if an action is legal, creates the child node and computes the heuristic to the goal state
def expand(node, goal_state):
    children = []
    moves = {
        "D": (1, 0, 0),
        "U": (-1, 0, 0),
        "S": (0, 1, 0),
        "N": (0, -1, 0),
        "E": (0, 0, 1),
        "W": (0, 0, -1),
    }
    cur_state = node.state
    x, y, z = node.empty_pos
    for move in moves:
        deltaX, deltaY, deltaZ = moves[move]
        newX, newY, newZ = x + deltaX, y + deltaY, z + deltaZ
        if isValidMove(
            newX, newY, newZ
        ):  # If it is a valid mvoe, create the child node
            child_state = copy.deepcopy(cur_state)
            temp = child_state[x][y][z]
            child_state[x][y][z] = child_state[newX][newY][newZ]
            child_state[newX][newY][newZ] = temp
            child = Node(
                child_state,
                (newX, newY, newZ),
                node,
                move,
                1 + node.path_cost,
                heuristic(child_state, goal_state),
            )
            children.append(child)
    return children


# Takes in an x-position, y-position, and z-position and returns if
# that position is valid on the board.
def isValidMove(x, y, z):
    return 0 <= x and x < 3 and 0 <= y and y < 3 and 0 <= z and z < 3


# Calculates the sum of manhattan distances of each tile from its goal position and
# returns the manhattan distance for the heuristic cost.
def heuristic(initial_state, goal_state):
    heuristic_cost = 0
    # This nested for-loop goes through the 3-d array and checks if the initial state is the
    # same of that at the goal state at a certain position. If not, it goes through the 3-d array of the goal state
    # and finds where the intial state and goal state both have a certain value, and computes the manhattan distance between
    # these two points
    for i in range(3):
        for j in range(3):
            for k in range(3):
                # Do not include the empty space in the heurisitic
                if initial_state[i][j][k] == 0:
                    continue
                if initial_state[i][j][k] != goal_state[i][j][k]:
                    for x in range(3):
                        for y in range(3):
                            for z in range(3):
                                if initial_state[i][j][k] == goal_state[x][y][z]:
                                    heuristic_cost += (
                                        abs(i - x) + abs(j - y) + abs(k - z)
                                    )
    return heuristic_cost


# This function uses the text given in the input file and parses it to create the initial and goal state
# It returns the data structures representing those states
# as well as where the empty position is in the initial state
def create_initial_and_goal_state(file):
    initial_state = [[]]
    goal_state = [[]]
    num_filled = 0
    with open(file) as f:
        # Goes through each line
        for line in f:
            # If the number of 3x3 tiles filled
            # hasn't reached 3 yet, then we are still
            # filling the initial tile
            if num_filled < 3:
                if line.strip() == "":
                    initial_state.append([])
                    num_filled += 1
                else:
                    # Creates a list of the integers on the given line and appends it to the lastly
                    # filled "z" axis
                    new_line = list(map(int, line.split()))
                    initial_state[-1].append(new_line)
                    # Checks if there is a 0 in this row and if so creates
                    # an indicator for where the empty position is
                    if 0 in new_line:
                        empty_pos = (
                            len(initial_state) - 1,
                            len(initial_state[-1]) - 1,
                            new_line.index(0),
                        )
            else:
                if line.strip() == "":
                    goal_state.append([])
                else:
                    goal_state[-1].append(list(map(int, line.split())))
    # This gets rid of an extra array that was created during intial construction
    initial_state.remove([])
    return initial_state, goal_state, empty_pos


# This function takes in the goal node found, an empty array 'actions', an empty array 'f_values'
# and an array filled with one integer '0'. It goes through the solution path recursively and fills
# in the respective arrays
def solution_path(solution, actions, f_values, depth):
    # Recursive case, go to the parent of the node, then append the action at the current
    # node and increase depth.
    if solution.parent != None:
        solution_path(solution.parent, actions, f_values, depth)
        actions.append(solution.action)
        depth[0] += 1
    f_values.append(solution.path_cost + solution.heuristic_cost)


# This function creates the output file. It takes in the file name in order to create a .txt file
# that will correspond in name to that of the input file. It also takes in the initial state and goal state
# to write into the file. It also takes in the array actions, f_values, and depth to write onto the file
# It also takes an integer nodes_generated to write into the file.
def create_output(file_name, initial, goal, actions, f_values, depth, nodes_generated):
    with open(file_name, "w") as file:
        # Writes the initial state
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    file.write(str(initial[i][j][k]) + " ")
                file.write("\n")
            file.write("\n")

        # Writes the goal state
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    file.write(str(goal[i][j][k]) + " ")
                file.write("\n")
            file.write("\n")

        file.write(str(depth))
        file.write("\n")
        file.write(str(nodes_generated))
        file.write("\n")
        file.write(" ".join(actions))
        file.write("\n")
        for value in f_values:
            file.write(str(value) + " ")


# Allows users to enter in the text file they want to solve
# if the text file exists. User can type 'quit' to quit the program
def main():
    while True:
        file_name = input("Enter the name of the text file: ")

        if file_name == "quit":
            break
        elif os.path.isfile(file_name):
            initial, end, empty_pos = create_initial_and_goal_state(file_name)
            solution, nodes_generated = astar(initial, end, empty_pos)
            actions = []
            f_values = []
            depth = [0]
            solution_path(solution, actions, f_values, depth)
            create_output(
                "solution_" + file_name,
                initial,
                end,
                actions,
                f_values,
                depth[0],
                nodes_generated,
            )
        else:
            print("File does not exist. Please enter a valid file name.")


if __name__ == "__main__":
    main()


# To get files this is what the interpreter looked like:

# Enter the name of the text file: Input1.txt
# Enter the name of the text file: Input2.txt
# Enter the name of the text file: Input3.txt
# Enter the name of the text file: quit
