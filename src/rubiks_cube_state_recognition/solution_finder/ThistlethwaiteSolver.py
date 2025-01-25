from time import perf_counter
from copy import deepcopy
import logging
from rubiks_cube_state_recognition.pattern_database_creator.IndexCalculator import IndexCalculator
from rubiks_cube_state_recognition.solution_finder.TreeNode import TreeNode
from rubiks_cube_state_recognition.cube_state.CubiesState import CornerCubiesState, EdgeCubiesState
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from rubiks_cube_state_recognition.cube_state.CubeState import CubeState

logging.basicConfig(level=logging.INFO, format="|%(asctime)s|%(name)s|%(levelname)s| %(message)s")

# All possible moves (Excluding only previous and opposite turns).
G0_VALID_NEXT_MOVES = {
    None: ['U', "U'", 'U2', 'D', "D'", 'D2', 'F', "F'", 'F2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
    'U': ['D', "D'", 'D2', 'F', "F'", 'F2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
    "U'": ['D', "D'", 'D2', 'F', "F'", 'F2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
    'U2': ['D', "D'", 'D2', 'F', "F'", 'F2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
    'D': ['F', "F'", 'F2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
    "D'": ['F', "F'", 'F2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
    'D2': ['F', "F'", 'F2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
    'F': ['U', "U'", 'U2', 'D', "D'", 'D2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
    "F'": ['U', "U'", 'U2', 'D', "D'", 'D2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
    'F2': ['U', "U'", 'U2', 'D', "D'", 'D2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
    'B': ['U', "U'", 'U2', 'D', "D'", 'D2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
    "B'": ['U', "U'", 'U2', 'D', "D'", 'D2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
    'B2': ['U', "U'", 'U2', 'D', "D'", 'D2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
    'L': ['U', "U'", 'U2', 'D', "D'", 'D2', 'F', "F'", 'F2', 'B', "B'", 'B2', 'R', "R'", 'R2'],
    "L'": ['U', "U'", 'U2', 'D', "D'", 'D2', 'F', "F'", 'F2', 'B', "B'", 'B2', 'R', "R'", 'R2'],
    'L2': ['U', "U'", 'U2', 'D', "D'", 'D2', 'F', "F'", 'F2', 'B', "B'", 'B2', 'R', "R'", 'R2'],
    'R': ['U', "U'", 'U2', 'D', "D'", 'D2', 'F', "F'", 'F2', 'B', "B'", 'B2'],
    "R'": ['U', "U'", 'U2', 'D', "D'", 'D2', 'F', "F'", 'F2', 'B', "B'", 'B2'],
    'R2': ['U', "U'", 'U2', 'D', "D'", 'D2', 'F', "F'", 'F2', 'B', "B'", 'B2']}

# Further excludes U, U', D, D'
G1_VALID_NEXT_MOVES = {None: ['U2', 'D2', 'F', "F'", 'F2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       'U': ['D2', 'F', "F'", 'F2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       "U'": ['D2', 'F', "F'", 'F2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       'U2': ['D2', 'F', "F'", 'F2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       'D': ['F', "F'", 'F2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       "D'": ['F', "F'", 'F2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       'D2': ['F', "F'", 'F2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       'F': ['U2', 'D2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       "F'": ['U2', 'D2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       'F2': ['U2', 'D2', 'B', "B'", 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       'B': ['U2', 'D2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       "B'": ['U2', 'D2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       'B2': ['U2', 'D2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       'L': ['U2', 'D2', 'F', "F'", 'F2', 'B', "B'", 'B2', 'R', "R'", 'R2'],
                       "L'": ['U2', 'D2', 'F', "F'", 'F2', 'B', "B'", 'B2', 'R', "R'", 'R2'],
                       'L2': ['U2', 'D2', 'F', "F'", 'F2', 'B', "B'", 'B2', 'R', "R'", 'R2'],
                       'R': ['U2', 'D2', 'F', "F'", 'F2', 'B', "B'", 'B2'],
                       "R'": ['U2', 'D2', 'F', "F'", 'F2', 'B', "B'", 'B2'],
                       'R2': ['U2', 'D2', 'F', "F'", 'F2', 'B', "B'", 'B2']}

# Further excludes F, F', B, B'
G2_VALID_NEXT_MOVES = {None: ['U2', 'D2', 'F2', 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       'U': ['D2', 'F2', 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       "U'": ['D2', 'F2', 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       'U2': ['D2', 'F2', 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       'D': ['F2', 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       "D'": ['F2', 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       'D2': ['F2', 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       'F': ['U2', 'D2', 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       "F'": ['U2', 'D2', 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       'F2': ['U2', 'D2', 'B2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       'B': ['U2', 'D2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       "B'": ['U2', 'D2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       'B2': ['U2', 'D2', 'L', "L'", 'L2', 'R', "R'", 'R2'],
                       'L': ['U2', 'D2', 'F2', 'B2', 'R', "R'", 'R2'],
                       "L'": ['U2', 'D2', 'F2', 'B2', 'R', "R'", 'R2'],
                       'L2': ['U2', 'D2', 'F2', 'B2', 'R', "R'", 'R2'],
                       'R': ['U2', 'D2', 'F2', 'B2'],
                       "R'": ['U2', 'D2', 'F2', 'B2'],
                       'R2': ['U2', 'D2', 'F2', 'B2']}

# Further excludes L, L', R, R'
G3_VALID_NEXT_MOVES = {None: ['U2', 'D2', 'F2', 'B2', 'L2', 'R2'],
                       'U': ['D2', 'F2', 'B2', 'L2', 'R2'],
                       "U'": ['D2', 'F2', 'B2', 'L2', 'R2'],
                       'U2': ['D2', 'F2', 'B2', 'L2', 'R2'],
                       'D': ['F2', 'B2', 'L2', 'R2'],
                       "D'": ['F2', 'B2', 'L2', 'R2'],
                       'D2': ['F2', 'B2', 'L2', 'R2'],
                       'F': ['U2', 'D2', 'B2', 'L2', 'R2'],
                       "F'": ['U2', 'D2', 'B2', 'L2', 'R2'],
                       'F2': ['U2', 'D2', 'B2', 'L2', 'R2'],
                       'B': ['U2', 'D2', 'L2', 'R2'],
                       "B'": ['U2', 'D2', 'L2', 'R2'],
                       'B2': ['U2', 'D2', 'L2', 'R2'],
                       'L': ['U2', 'D2', 'F2', 'B2', 'R2'],
                       "L'": ['U2', 'D2', 'F2', 'B2', 'R2'],
                       'L2': ['U2', 'D2', 'F2', 'B2', 'R2'],
                       'R': ['U2', 'D2', 'F2', 'B2'],
                       "R'": ['U2', 'D2', 'F2', 'B2'],
                       'R2': ['U2', 'D2', 'F2', 'B2']}


class ThistlethwaiteSolver:
    def __init__(self):
        self.corner_cubies_index_calculator = IndexCalculator(
            number_of_cubies=8,  # there are 8 corner cubies
            lehmer_bases=[5040, 720, 120, 24, 6, 2, 1],  # element = (8-1-index)!
            orientation_bases=[1, 3, 9, 27, 81, 243, 729, 2187])  # element= 3**index)
        self.edge_cubies_index_calculator = IndexCalculator(
            number_of_cubies=12,  # there are 12 edge cubies
            lehmer_bases=[332640, 30240, 3024, 336, 42, 6, 1],  # element = (12-1-index)P(7-1-index)
            orientation_bases=[1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048])  # element = 2**index)
        self.min_group_search_time = 30  # the minimum time (seconds) before moving to a new group
        self.search_start_time = None  # the start time of a tree search

        self.solution = None  # list of the turn moves required to solve the Rubik's cube
        self.g3_achieved = None  # whether group 3 has been achieved in the search (True/False)
        self.g2_achieved = None  # whether group 2 has been achieved in the search (True/False)
        self.g1_achieved = None  # whether group 2 has been achieved in the search (True/False)

        self.visited_nodes = None  # stores the hash indexes of the nodes visited in the tree search
        self.node_queues = None  # multiple list queues for the nodes that need to be processed at each depth
        self.valid_next_moves = None  # the valid next moves dictionary currently being used
        self.current_depth = None  # the current depth in the tree iterative-deepening search
        self.next_depth = None  # the depth after current depth (current depth + 1)

        self.next_group_found = None  # whether one of the next groups have been found (True/False)
        self.next_group_root_node = None  # the node that is a part of the found next group
        self.next_group_valid_next_moves = None  # the valid next moves for the found next group

    def __initialise_tree(self, root_node: object):
        # creates node_queues
        self.node_queues = {0: [root_node]}
        for depth in range(1, 52):
            self.node_queues[depth] = []

        # initialises the current and next depths
        self.current_depth = 0
        self.next_depth = 1

    def __process_node(self, node: TreeNode):
        if node.cube_state.is_solved():
            self.solution = node.path[1:]
            logging.info('solved')
            return

        # calculates the hash index for the corner cubies
        corner_cubies_state = CornerCubiesState(node.cube_state)
        corner_positions_permutation, corner_orientations_permutation = corner_cubies_state.get_permutations()
        corners_hash_index = self.corner_cubies_index_calculator.calculate_hash_index(
            corner_positions_permutation,
            corner_orientations_permutation)

        # calculates the hash indexes for the edge cubies
        edge_cubies_state = EdgeCubiesState(node.cube_state)
        edge_positions_permutation_1, edge_orientations_permutation_1, edge_positions_permutation_2, edge_orientations_permutation_2 = edge_cubies_state.get_permutations()
        edges_hash_index_1 = self.edge_cubies_index_calculator.calculate_hash_index(
            edge_positions_permutation_1,
            edge_orientations_permutation_1)
        edges_hash_index_2 = self.edge_cubies_index_calculator.calculate_hash_index(
            edge_positions_permutation_2,
            edge_orientations_permutation_2)

        # stops children generation of node if it has already been searched previously
        if corners_hash_index in self.visited_nodes['corners']:
            if edges_hash_index_1 in self.visited_nodes['edges_1']:
                if edges_hash_index_2 in self.visited_nodes['edges_2']:
                    return

        # checks the group number of the node to try and move it into a better new group
        if not self.g3_achieved:  # if not already in the best group
            node_group = node.cube_state.subgroup_number()  # calculates the group number of the node

            # makes preparation for a tree search only from the group 3 node
            if node_group == 3:
                logging.info("Group 3 achieved")  # for testing purposes
                self.next_group_root_node = deepcopy(node)  # stores a copy of the node to prepare for the new search
                self.next_group_valid_next_moves = G3_VALID_NEXT_MOVES  # prepares the valid next move for the new search
                self.next_group_found = True

                # all 3 groups have been achieved
                self.g3_achieved = True
                self.g2_achieved = True
                self.g1_achieved = True

            # makes preparation for a tree search only from the group 2 node
            elif (not self.g2_achieved) and (node_group == 2):
                logging.info("Group 2 achieved")  # for testing purposes
                self.next_group_root_node = deepcopy(node)
                self.next_group_valid_next_moves = G2_VALID_NEXT_MOVES
                self.next_group_found = True

                # first 2 groups have been achieved
                self.g2_achieved = True
                self.g1_achieved = True

            # makes preparation for a tree search only from the group 1 node
            elif (not self.g1_achieved) and (node_group == 1):
                logging.info("Group 1 achieved")  # for testing purposes
                self.next_group_root_node = deepcopy(node)
                self.next_group_valid_next_moves = G1_VALID_NEXT_MOVES
                self.next_group_found = True
                self.g1_achieved = True  # the first group has been achieved

        node_copy = deepcopy(
            node)  # creates copy of the node so the children generation doesn't increase the size of the current node queue
        node_copy.create_all_children(self.valid_next_moves)  # children generation

        # marks the node as visited
        if not self.next_group_found:  # if next group found, it is necessary that the node and next nodes are searched again
            self.visited_nodes['corners'].add(corners_hash_index)
            self.visited_nodes['edges_1'].add(edges_hash_index_1)
            self.visited_nodes['edges_2'].add(edges_hash_index_2)

        # adds the children to the next depth node processing queue
        self.node_queues[self.next_depth].extend(node_copy.children)

    def solve(self, cube_state: "CubeState"):
        self.solution = None
        self.g3_achieved = False
        self.g2_achieved = False
        self.g1_achieved = False
        self.valid_next_moves = G0_VALID_NEXT_MOVES

        self.visited_nodes = {'corners': set(),
                              'edges_1': set(),
                              'edges_2': set()}

        root_node = TreeNode(cube_state=cube_state, path=[None])
        self.__initialise_tree(root_node)

        self.search_start_time = perf_counter()  # the time that the search started

        while self.current_depth <= 51:
            for node in self.node_queues[self.current_depth]:
                time_since_start = perf_counter() - self.search_start_time  # the time since the search started

                # focuses the search on a node that's in a higher group if found.
                # this can only happen if enough time has passed since the beginning of the search
                # (to try and find the highest group before focusing on it)
                if (time_since_start > self.min_group_search_time) and self.next_group_found:
                    logging.info('moving to new group')  # for testing purposes
                    self.next_group_found = False  # resets its value
                    self.valid_next_moves = self.next_group_valid_next_moves  # updates the valid next moves for the new group
                    self.search_start_time = perf_counter()  # resets its value (new search has started)
                    self.__initialise_tree(
                        root_node=self.next_group_root_node)  # initialises a new tree for the new search
                    self.__process_node(self.next_group_root_node)  # processes the root node in the new group
                    break
                if self.solution is not None:
                    break
                self.__process_node(node)

            if self.solution is None:  # no solution has been found
                logging.info(f'No solution at depth {self.current_depth}')  # for testing
                del (self.node_queues[self.current_depth])  # removes the processed queue to save memory

                # updates the depth attributes for the processing at the next depth
                self.current_depth = self.next_depth
                self.next_depth += 1

            # the solution has been found. The loop breaks as there is no need to
            else:
                break

        return self.solution
