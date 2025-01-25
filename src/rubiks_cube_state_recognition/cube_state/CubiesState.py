from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from rubiks_cube_state_recognition.cube_state.CubeState import CubeState

# the index for each corner cubie
CORNER_CUBIE_STATE_TO_INDEX = {('b', 'o', 'w'): 0,  # bow corner cubie index
                               ('b', 'o', 'y'): 1,  # boy corner cubie index
                               ('b', 'r', 'w'): 2,  # brw corner cubie index
                               ('b', 'r', 'y'): 3,  # bry corner cubie index
                               ('g', 'o', 'w'): 4,  # gow corner cubie index
                               ('g', 'o', 'y'): 5,  # goy corner cubie index
                               ('g', 'r', 'w'): 6,  # grw corner cubie index
                               ('g', 'r', 'y'): 7}  # gry corner cubie index

# the orientation index for each corner cubie
CORNER_CUBIE_STATE_TO_ORIENTATION_INDEX = {  # bwo corner cubie orientation indexes
    ('b', 'w', 'o'): 0,  # 1st orientation
    ('w', 'o', 'b'): 1,  # 2nd orientation
    ('o', 'b', 'w'): 2,  # 3rd orientation

    # boy corner cubie orientation indexes
    ('b', 'o', 'y'): 0,
    ('o', 'y', 'b'): 1,
    ('y', 'b', 'o'): 2,

    # brw corner cubie orientation indexes
    ('b', 'r', 'w'): 0,
    ('r', 'w', 'b'): 1,
    ('w', 'b', 'r'): 2,

    # byr corner cubie orientation indexes
    ('b', 'y', 'r'): 0,
    ('y', 'r', 'b'): 1,
    ('r', 'b', 'y'): 2,

    # gow corner cubie orientation indexes
    ('g', 'o', 'w'): 0,
    ('o', 'w', 'g'): 1,
    ('w', 'g', 'o'): 2,

    # gyo corner cubie orientation indexes
    ('g', 'y', 'o'): 0,
    ('y', 'o', 'g'): 1,
    ('o', 'g', 'y'): 2,

    # gwr corner cubie orientation indexes
    ('g', 'w', 'r'): 0,
    ('w', 'r', 'g'): 1,
    ('r', 'g', 'w'): 2,

    # gry corner cubie orientation indexes
    ('g', 'r', 'y'): 0,
    ('r', 'y', 'g'): 1,
    ('y', 'g', 'r'): 2}

# the index for each edge cubie
EDGE_CUBIE_STATE_TO_INDEX = {('b', 'o'): 0,  # bo edge cubie index
                             ('b', 'r'): 1,  # br edge cubie index
                             ('b', 'w'): 2,  # bw edge cubie index
                             ('b', 'y'): 3,  # by edge cubie index
                             ('g', 'o'): 4,  # go edge cubie index
                             ('g', 'r'): 5,  # gr edge cubie index
                             ('g', 'w'): 6,  # gw edge cubie index
                             ('g', 'y'): 7,  # gy edge cubie index
                             ('o', 'w'): 8,  # ow edge cubie index
                             ('o', 'y'): 9,  # oy edge cubie index
                             ('r', 'w'): 10,  # rw edge cubie index
                             ('r', 'y'): 11}  # ry edge cubie index

# the orientation index for each edge cubie
EDGE_CUBIE_STATE_TO_ORIENTATION_INDEX = {  # bo edge cubie orientation indexes
    ('b', 'o'): 0,  # 1st orientation
    ('o', 'b'): 1,  # 2nd orientation

    # br edge cubie orientation indexes
    ('b', 'r'): 0,
    ('r', 'b'): 1,

    # bw edge cubie orientation indexes
    ('b', 'w'): 0,
    ('w', 'b'): 1,

    # by edge cubie orientation indexes
    ('b', 'y'): 0,
    ('y', 'b'): 1,

    # go edge cubie orientation indexes
    ('g', 'o'): 0,
    ('o', 'g'): 1,

    # gr edge cubie orientation indexes
    ('g', 'r'): 0,
    ('r', 'g'): 1,

    # gw edge cubie orientation indexes
    ('g', 'w'): 0,
    ('w', 'g'): 1,

    # gy edge cubie orientation indexes
    ('g', 'y'): 0,
    ('y', 'g'): 1,

    # ow edge cubie orientation indexes
    ('o', 'w'): 0,
    ('w', 'o'): 1,

    # oy edge cubie orientation indexes
    ('o', 'y'): 0,
    ('y', 'o'): 1,

    # rw edge cubie orientation indexes
    ('r', 'w'): 0,
    ('w', 'r'): 1,

    # ry edge cubie orientation indexes
    ('r', 'y'): 0,
    ('y', 'r'): 1}


class __CubiesState:
    def __init__(self, valid_ordered_cubie_names: list):
        self.valid_ordered_cubie_names = valid_ordered_cubie_names  # ordered cubie names (the target)
        self.ordered_cubie_state_names = None  # ordered cubie names of the current cube state

    def sort_cubie_state_names(self):
        self.ordered_cubie_state_names = []

        for cubie_name in self.valid_ordered_cubie_names:  # iterates through the valid cubie names
            cubie_state = list(
                self.__getattribute__(cubie_name))  # converts cubie state tuple to list (so it can be sorted)
            cubie_state.sort()  # sorts the cubie state (to get the cubie name)

            # adds the ordered cubie name (cubie state joined) to the 'ordered_cubie_state_names' list
            self.ordered_cubie_state_names.append(''.join(cubie_state))

    def is_valid(self):
        self.sort_cubie_state_names()  # uses the sortCubieStateNames method to find 'ordered_cubie_state_names'
        self.ordered_cubie_state_names.sort()  # sorts the list so everything is in alphabetical order

        # if 'ordered_cubie_state_names' is the same as 'valid_ordered_cubie_names', the cubie states is valid
        if self.ordered_cubie_state_names == self.valid_ordered_cubie_names:
            return True

        # True is not returned and so the cubie states are not valid
        return False


class CornerCubiesState(__CubiesState):
    def __init__(self, cube_state: "CubeState"):
        super().__init__(['bow', 'boy', 'brw', 'bry',
                          'gow', 'goy', 'grw', 'gry'])

        # attribute name = cubie name. The tuple = cubie state
        self.bow = (cube_state.b_face.tr,
                    cube_state.w_face.tr,
                    cube_state.o_face.tl)  # blue-orange-white corner cubie state
        self.boy = (cube_state.b_face.br,
                    cube_state.o_face.bl,
                    cube_state.y_face.br)  # blue-orange-yellow corner cubie state
        self.brw = (cube_state.b_face.tl,
                    cube_state.r_face.tr,
                    cube_state.w_face.br)  # blue-red-white corner cubie state
        self.bry = (cube_state.b_face.bl,
                    cube_state.y_face.tr,
                    cube_state.r_face.br)  # blue-red-yellow corner cubie state
        self.gow = (cube_state.g_face.tl,
                    cube_state.o_face.tr,
                    cube_state.w_face.tl)  # green-orange-white corner cubie state
        self.goy = (cube_state.g_face.bl,
                    cube_state.y_face.bl,
                    cube_state.o_face.br)  # green-orange-yellow corner cubie state
        self.grw = (cube_state.g_face.tr,
                    cube_state.w_face.bl,
                    cube_state.r_face.tl)  # green-red-white corner cubie state
        self.gry = (cube_state.g_face.br,
                    cube_state.r_face.bl,
                    cube_state.y_face.tl)  # green-red-yellow corner cubie state

    def get_permutations(self):  # corner cubies state as numbers
        self.sort_cubie_state_names()  # sorts the cubie state names (so it can )
        cubie_positions_permutation = []  # permutation of the positions of the cubies
        cubie_orientations_permutation = []  # permutation of the orientations of the cubies
        for cubie_state, cubie_name in zip(self.ordered_cubie_state_names[:-1],
                                           self.valid_ordered_cubie_names[:-1]):  # ignores last elements
            # finds the index of the cubie at the cubie_name position and adds it to the appropriate permutation
            cubie_positions_permutation.append(CORNER_CUBIE_STATE_TO_INDEX[tuple(cubie_state)])

            # finds the orientation index of the cubie at the cubie_name position and adds it to the appropriate permutation
            cubie_orientations_permutation.append(
                CORNER_CUBIE_STATE_TO_ORIENTATION_INDEX[self.__getattribute__(cubie_name)])

        return cubie_positions_permutation, cubie_orientations_permutation  # returns the permutations


class EdgeCubiesState(__CubiesState):
    def __init__(self, cube_state):
        super().__init__(['bo', 'br', 'bw', 'by',
                          'go', 'gr', 'gw', 'gy',
                          'ow', 'oy', 'rw', 'ry'])

        # attribute name = cubie name. The tuple = cubie state
        self.bo = (cube_state.b_face.mr, cube_state.o_face.ml)  # blue-orange edge cubie state
        self.br = (cube_state.b_face.ml, cube_state.r_face.mr)  # blue-red edge cubie state
        self.bw = (cube_state.b_face.tm, cube_state.w_face.mr)  # blue-white edge cubie state
        self.by = (cube_state.b_face.bm, cube_state.y_face.mr)  # blue-yellow edge cubie state
        self.go = (cube_state.g_face.ml, cube_state.o_face.mr)  # green-orange edge cubie state
        self.gr = (cube_state.g_face.mr, cube_state.r_face.ml)  # green-red edge cubie state
        self.gw = (cube_state.g_face.tm, cube_state.w_face.ml)  # green-white edge cubie state
        self.gy = (cube_state.g_face.bm, cube_state.y_face.ml)  # green-yellow edge cubie state
        self.ow = (cube_state.o_face.tm, cube_state.w_face.tm)  # orange-white edge cubie state
        self.oy = (cube_state.o_face.bm, cube_state.y_face.bm)  # orange-yellow edge cubie state
        self.rw = (cube_state.r_face.tm, cube_state.w_face.bm)  # red-white edge cubie state
        self.ry = (cube_state.r_face.bm, cube_state.y_face.tm)  # red-yellow edge cubie state

    def get_permutations(self):  # edge cubies state as numbers
        self.sort_cubie_state_names()  # uses the sortCubieStateNames method to find 'ordered_cubie_state_names'

        # permutation of the positions of the cubies (split in 2 for each of the edge pattern databases)
        cubie_positions_permutation_1 = []
        cubie_positions_permutation_2 = []

        # permutation of the orientations of the cubies (split in 2 for each of the edge pattern databases)
        cubie_orientations_permutation_1 = []
        cubie_orientations_permutation_2 = []

        # 1st to 6th edge cubies: add to first permutation
        for cubie_state, cubie_name in zip(self.ordered_cubie_state_names[0:6], self.valid_ordered_cubie_names[0:6]):
            # finds the index of the cubie at the cubie_name position and adds it to the appropriate permutation
            cubie_positions_permutation_1.append(EDGE_CUBIE_STATE_TO_INDEX[tuple(cubie_state)])

            # finds the orientation index of the cubie at the cubie_name position and adds it to the appropriate permutation
            cubie_orientations_permutation_1.append(
                EDGE_CUBIE_STATE_TO_ORIENTATION_INDEX[self.__getattribute__(cubie_name)])

        # 7th edge cubie: add to both permutations
        cubie_state = self.ordered_cubie_state_names[6]
        cubie_name = self.valid_ordered_cubie_names[6]

        # finds the index of the cubie at the cubie_name position and adds it to the appropriate permutations
        position_index = EDGE_CUBIE_STATE_TO_INDEX[tuple(cubie_state)]
        cubie_positions_permutation_1.append(position_index)
        cubie_positions_permutation_2.append(position_index)

        # finds the orientation index of the cubie at the cubie_name position and adds it to the appropriate permutations
        orientation_index = EDGE_CUBIE_STATE_TO_ORIENTATION_INDEX[self.__getattribute__(cubie_name)]
        cubie_orientations_permutation_1.append(orientation_index)
        cubie_orientations_permutation_2.append(orientation_index)

        # 8th to 12th edge cubies: add to second permutation
        for cubie_state, cubie_name in zip(self.ordered_cubie_state_names[7:], self.valid_ordered_cubie_names[7:]):
            cubie_positions_permutation_2.append(EDGE_CUBIE_STATE_TO_INDEX[tuple(cubie_state)])
            cubie_orientations_permutation_2.append(
                EDGE_CUBIE_STATE_TO_ORIENTATION_INDEX[self.__getattribute__(cubie_name)])

        return (cubie_positions_permutation_1, cubie_orientations_permutation_1, cubie_positions_permutation_2,
                cubie_orientations_permutation_2)  # returns the permutations

    def is_correctly_oriented(self):
        # checks if F/B layers are oriented
        for edge_cubie_state in [self.ow, self.oy, self.rw, self.ry]:
            if ('o' in edge_cubie_state) or ('r' in edge_cubie_state):
                if edge_cubie_state[0] not in ['o', 'r']:
                    return False
            elif edge_cubie_state[0] in ['b', 'g']:
                return False
        for edge_cubie_state in [self.bo, self.br, self.go, self.gr]:
            if ('o' in edge_cubie_state) or ('r' in edge_cubie_state):
                if edge_cubie_state[1] not in ['o', 'r']:
                    return False
            elif edge_cubie_state[1] in ['b', 'g']:
                return False

        # checks if middle layer is orientated
        for edge_cubie_state in [self.bw, self.by, self.gw, self.gy]:
            if ('o' in edge_cubie_state) or ('r' in edge_cubie_state):
                if edge_cubie_state[0] in ['o', 'r']:
                    return False
            elif edge_cubie_state[0] not in ['b', 'g']:
                return False

        return True

    def has_correct_m_slice(self):
        self.sort_cubie_state_names()  # makes every cubie state name in alphabetical order
        middle_layer_edges = self.ordered_cubie_state_names[8:12]

        # determines if the middle layer has an unwanted edge cubie
        for edge_cubie_state in middle_layer_edges:
            if edge_cubie_state not in ['ow', 'oy', 'rw', 'ry']:
                return False

        # the middle layer contains the required edge cubies
        return True
