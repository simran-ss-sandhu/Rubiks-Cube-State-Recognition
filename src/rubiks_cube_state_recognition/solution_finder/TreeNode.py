from copy import deepcopy
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from rubiks_cube_state_recognition.cube_state.CubeState import CubeState


class TreeNode:
    def __init__(self, cube_state: "CubeState", path: list):
        self.cube_state = cube_state  # the cube state of the current tree node
        self.path = path  # the turn moves that were used to get to the current tree node from the root node
        self.children = []  # the children tree nodes of the current tree node

    def __create_child(self, turn_type: str):
        cube_state_copy = deepcopy(self.cube_state)  # creates copy so original cube state is not changed
        cube_state_copy.turn_face(turn_type)  # applies a cube face turn transformation to the cube state copy
        path_copy = [*self.path, turn_type]  # creates a copy so the current (original) tree node's path is not changed

        # adds cube state as a Tree_Node formatted child to children list
        self.children.append(TreeNode(cube_state=cube_state_copy, path=path_copy))

    def create_all_children(self, valid_next_moves: dict):
        # the last turn type used to get to the current tree node
        last_turn_type = self.path[-1]

        # applies all necessary turn transformations to generate all the children of the current tree node
        for turn_type in valid_next_moves[last_turn_type]:
            self.__create_child(turn_type)
