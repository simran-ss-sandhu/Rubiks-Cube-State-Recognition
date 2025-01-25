from copy import deepcopy
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from rubiks_cube_state_recognition.cube_state.CubeState import CubeState

# the possible turning moves that can be made after the turn type specified by the key
VALID_NEXT_MOVES = {
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


class PDNode:
    def __init__(self, cube_state: "CubeState", last_turn: str):
        self.cube_state = cube_state
        self.last_turn = last_turn  # the last turn made to get to the cube state
        self.children = []  # the children of the cube state (the cube states that can reached within one turn)

    def __create_child(self, turn_type: str):
        cube_state_copy = deepcopy(self.cube_state)  # copy of the cube_state
        cube_state_copy.turn_face(turn_type)  # applies turn transformation

        # adds cube state as a PD_Node formatted child to children list
        self.children.append(PDNode(cube_state=cube_state_copy, last_turn=turn_type))

    def create_children(self):
        # gets list of the turn types that can be applied to the current cube state
        valid_next_moves = VALID_NEXT_MOVES[self.last_turn]

        # creates the children of the current cube state
        for turn_type in valid_next_moves:
            self.__create_child(turn_type)
