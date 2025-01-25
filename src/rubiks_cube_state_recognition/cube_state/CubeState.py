import logging
from copy import deepcopy
from rubiks_cube_state_recognition.cube_state.CubiesState import CornerCubiesState, EdgeCubiesState

logging.basicConfig(level=logging.INFO, format="|%(asctime)s|%(name)s|%(levelname)s| %(message)s")

# maps the first character of the turn type to its cube face attribute name
TURN_TYPE_TO_FACE_NAME = {'U': 'w_face',
                          'D': 'y_face',
                          'F': 'r_face',
                          'B': 'o_face',
                          'L': 'g_face',
                          'R': 'b_face'}

# maps the cube face name to information of the cube face on the left/bottom/right/top of it
LEFT_FACE_INFO = {'w_face': {'face_name': 'g_face',  # name of the cube face
                             'closest_cube_tiles': 'top_row'},  # the row/column closest to the key cube face
                  'g_face': {'face_name': 'o_face',
                             'closest_cube_tiles': 'right_column'},
                  'r_face': {'face_name': 'g_face',
                             'closest_cube_tiles': 'right_column'},
                  'b_face': {'face_name': 'r_face',
                             'closest_cube_tiles': 'right_column'},
                  'o_face': {'face_name': 'b_face',
                             'closest_cube_tiles': 'right_column'},
                  'y_face': {'face_name': 'g_face',
                             'closest_cube_tiles': 'bottom_row'}}
BOTTOM_FACE_INFO = {'w_face': {'face_name': 'r_face',
                               'closest_cube_tiles': 'top_row'},
                    'g_face': {'face_name': 'y_face',
                               'closest_cube_tiles': 'left_column'},
                    'r_face': {'face_name': 'y_face',
                               'closest_cube_tiles': 'top_row'},
                    'b_face': {'face_name': 'y_face',
                               'closest_cube_tiles': 'right_column'},
                    'o_face': {'face_name': 'y_face',
                               'closest_cube_tiles': 'bottom_row'},
                    'y_face': {'face_name': 'o_face',
                               'closest_cube_tiles': 'bottom_row'}}
RIGHT_FACE_INFO = {'w_face': {'face_name': 'b_face',
                              'closest_cube_tiles': 'top_row'},
                   'g_face': {'face_name': 'r_face',
                              'closest_cube_tiles': 'left_column'},
                   'r_face': {'face_name': 'b_face',
                              'closest_cube_tiles': 'left_column'},
                   'b_face': {'face_name': 'o_face',
                              'closest_cube_tiles': 'left_column'},
                   'o_face': {'face_name': 'g_face',
                              'closest_cube_tiles': 'left_column'},
                   'y_face': {'face_name': 'b_face',
                              'closest_cube_tiles': 'bottom_row'}}
TOP_FACE_INFO = {'w_face': {'face_name': 'o_face',
                            'closest_cube_tiles': 'top_row'},
                 'g_face': {'face_name': 'w_face',
                            'closest_cube_tiles': 'left_column'},
                 'r_face': {'face_name': 'w_face',
                            'closest_cube_tiles': 'bottom_row'},
                 'b_face': {'face_name': 'w_face',
                            'closest_cube_tiles': 'right_column'},
                 'o_face': {'face_name': 'w_face',
                            'closest_cube_tiles': 'top_row'},
                 'y_face': {'face_name': 'r_face',
                            'closest_cube_tiles': 'bottom_row'}}

# maps the row/column name to the names of cube tiles in that row/column
CUBE_TILES_INFO = {'left_column': ['tl', 'ml', 'bl'],
                   'bottom_row': ['bl', 'bm', 'br'],
                   'right_column': ['br', 'mr', 'tr'],
                   'top_row': ['tr', 'tm', 'tl']}


class CubeFace:
    def __init__(self):
        self.tl = None  # state (colour/image) of the top left cube tile
        self.tm = None  # state (colour/image) of the top middle cube tile
        self.tr = None  # state (colour/image) of the top right cube tile
        self.ml = None  # state (colour/image) of the middle left cube tile
        self.c = None  # state (colour/image) of the centre cube tile
        self.mr = None  # state (colour/image) of the middle right cube tile
        self.bl = None  # state (colour/image) of the bottom left cube tile
        self.bm = None  # state (colour/image) of the bottom middle cube tile
        self.br = None  # state (colour/image) of the bottom right cube tile

    def is_fully_recognised(self):
        # the instance's whole cube face state
        cube_face = [self.tl, self.tm, self.tr,
                     self.ml, self.c, self.mr,
                     self.bl, self.bm, self.br]

        if None in cube_face:  # a cube tile does not have a colour state
            return False  # the cube face has not been fully recognised
        return True  # the cube has been fully recognised (every cube tile has a colour state)


class CubeState:
    def __init__(self):
        self.r_face = None  # Cube_Face instance for the red cube face
        self.o_face = None  # Cube_Face instance for the orange cube face
        self.y_face = None  # Cube_Face instance for the yellow cube face
        self.g_face = None  # Cube_Face instance for the green cube face
        self.b_face = None  # Cube_Face instance for the blue cube face
        self.w_face = None  # Cube_Face instance for the white cube face

    def add_face(self, cube_face: CubeFace):
        # adds the cube face to the appropriate attribute
        if cube_face.is_fully_recognised():  # if every cube tile has been assigned a colour state
            cube_face_name = cube_face.c + '_face'  # the cube face colour is determined by the center cube tile
            self.__setattr__(cube_face_name, cube_face)  # updates the appropriate cube face attribute

            logging.info(
                "recognised cube face state:\n"
                +f"{cube_face.tl}  {cube_face.tm}  {cube_face.tr}\n"
                + f"{cube_face.ml}  {cube_face.c}  {cube_face.mr}\n"
                + f"{cube_face.bl}  {cube_face.bm}  {cube_face.br}")

    def turn_face(self, turn_type: str):
        turning_face_name = TURN_TYPE_TO_FACE_NAME[turn_type[0]]  # the attribute name of the face that is to be turned
        turning_face_state = self.__getattribute__(
            turning_face_name)  # the Cube_Face state of the face that is to be turned

        # cube face information for the cube faces on the left, top, right and below the cube face that will be turned
        left_face_info = LEFT_FACE_INFO[turning_face_name]
        top_face_info = TOP_FACE_INFO[turning_face_name]
        right_face_info = RIGHT_FACE_INFO[turning_face_name]
        bottom_face_info = BOTTOM_FACE_INFO[turning_face_name]

        # the cube tiles on the row or column closest to the turning face for the cube faces specified
        left_face_cube_tiles_names = CUBE_TILES_INFO[left_face_info['closest_cube_tiles']]
        bottom_face_cube_tiles_names = CUBE_TILES_INFO[bottom_face_info['closest_cube_tiles']]
        right_face_cube_tiles_names = CUBE_TILES_INFO[right_face_info['closest_cube_tiles']]
        top_face_cube_tiles_names = CUBE_TILES_INFO[top_face_info['closest_cube_tiles']]

        # the Cube_Face state of the cube faces on the left, top, right and below the cube face that will be turned
        left_face_state = self.__getattribute__(left_face_info['face_name'])
        top_face_state = self.__getattribute__(top_face_info['face_name'])
        right_face_state = self.__getattribute__(right_face_info['face_name'])
        bottom_face_state = self.__getattribute__(bottom_face_info['face_name'])

        # determines the number of times the turning cube face needs to be turned clockwise
        if len(turn_type) == 1:
            number_of_clockwise_turns = 1
        elif turn_type[1] == '2':
            number_of_clockwise_turns = 2
        elif turn_type[1] == "'":
            number_of_clockwise_turns = 3
        else:
            logging.error("'turn_type' format is incorrect")

        # turns cube face the calculated number of times
        for turn_number in range(number_of_clockwise_turns):

            # moves the cube tiles only on the turning cube face to the correct turned position
            # turning face corner cube tiles
            temp_tile = turning_face_state.tl
            turning_face_state.tl = turning_face_state.bl
            turning_face_state.bl = turning_face_state.br
            turning_face_state.br = turning_face_state.tr
            turning_face_state.tr = temp_tile
            # turning face edge cube tiles
            temp_tile = turning_face_state.ml
            turning_face_state.ml = turning_face_state.bm
            turning_face_state.bm = turning_face_state.mr
            turning_face_state.mr = turning_face_state.tm
            turning_face_state.tm = temp_tile

            # creates a copy of the cube face on the left on the cube face that is being turned
            temp_left_face_state = deepcopy(left_face_state)

            # the appropriate cube tiles from the bottom cube face are moved to the left cube face
            for tile_to_replace_name, tile_replacer_name in zip(left_face_cube_tiles_names,
                                                                bottom_face_cube_tiles_names):
                tile_replacer_state = bottom_face_state.__getattribute__(tile_replacer_name)
                left_face_state.__setattr__(tile_to_replace_name, tile_replacer_state)

            # the appropriate cube tiles from the right cube face are moved to the bottom cube face
            for tile_to_replace_name, tile_replacer_name in zip(bottom_face_cube_tiles_names,
                                                                right_face_cube_tiles_names):
                tile_replacer_state = right_face_state.__getattribute__(tile_replacer_name)
                bottom_face_state.__setattr__(tile_to_replace_name, tile_replacer_state)

            # the appropriate cube tiles from the top cube face are moved to the right cube face
            for tile_to_replace_name, tile_replacer_name in zip(right_face_cube_tiles_names, top_face_cube_tiles_names):
                tile_replacer_state = top_face_state.__getattribute__(tile_replacer_name)
                right_face_state.__setattr__(tile_to_replace_name, tile_replacer_state)

            # the appropriate cube tiles from the copy of the left cube face are moved to the top cube face
            for tile_to_replace_name, tile_replacer_name in zip(top_face_cube_tiles_names, left_face_cube_tiles_names):
                tile_replacer_state = temp_left_face_state.__getattribute__(tile_replacer_name)
                top_face_state.__setattr__(tile_to_replace_name, tile_replacer_state)

    def __colour_count_is_valid(self):
        # initialises the number of cube tiles found for each colour
        r_count = 0
        o_count = 0
        y_count = 0
        g_count = 0
        b_count = 0
        w_count = 0

        # counts the number of cube tiles found in the cube state for each colour
        for cube_face in [self.r_face, self.o_face, self.y_face, self.g_face, self.b_face, self.w_face]:
            if cube_face.is_fully_recognised():  # if every cube tile has a colour assigned to it

                # the colours of all the cube tiles in the current cube face
                cube_face_colours = [cube_face.tl, cube_face.tm, cube_face.tr,
                                     cube_face.ml, cube_face.c, cube_face.mr,
                                     cube_face.bl, cube_face.bm, cube_face.br]

                # adds the number of red cube tiles in the current cube face
                r_count += cube_face_colours.count('r')

                if r_count > 9:  # impossible for there to be more than 9 red cube tiles
                    return False

                # adds the number of orange cube tiles in the current cube face
                o_count += cube_face_colours.count('o')

                if o_count > 9:  # impossible for there to be more than 9 orange cube tiles
                    return False

                # adds the number of yellow cube tiles in the current cube face
                y_count += cube_face_colours.count('y')

                if y_count > 9:  # impossible for there to be more than 9 yellow cube tiles
                    return False

                # adds the number of green cube tiles in the current cube face
                g_count += cube_face_colours.count('g')

                if g_count > 9:  # impossible for there to be more than 9 green cube tiles
                    return False

                # adds the number of blue cube tiles in the current cube face
                b_count += cube_face_colours.count('b')

                if b_count > 9:  # impossible for there to be more than 9 blue cube tiles
                    return False

                # adds the number of white cube tiles in the current cube face
                w_count += cube_face_colours.count('w')

                if w_count > 9:  # impossible for there to be more than 9 white cube tiles
                    return False

            # there cannot be exactly 9 cube tiles of each colour if there is a cube face which isn't fully recognised
            else:
                return False

        # checks if there are exactly 9 cube tiles of each colour
        for colour_count in [r_count, o_count, y_count, g_count, b_count, w_count]:
            if colour_count != 9:
                return False

        # all checks suggest that the colour count is valid
        return True

    def is_valid(self):
        if None not in [self.r_face, self.o_face, self.y_face, self.g_face, self.b_face,
                        self.w_face]:  # every face has been identified check

            if self.__colour_count_is_valid():  # colour count check
                logging.debug('colour count is valid')

                corner_cubies_state = CornerCubiesState(cube_state=self)
                if corner_cubies_state.is_valid():  # valid corner cubies check
                    logging.debug('corner cubies are valid')

                    edge_cubies_state = EdgeCubiesState(cube_state=self)
                    if edge_cubies_state.is_valid():  # valid edge cubies check
                        logging.debug('edge cubies are valid')
                        return True  # all the checks has passed (the cube state is valid)

        # if True has not been returned, one of the checks didn't pass (the cube state isn't valid)
        return False

    def is_solved(self):
        faces_states = [self.w_face, self.r_face, self.g_face, self.b_face, self.o_face, self.y_face]
        faces_colours = ['w', 'r', 'g', 'b', 'o', 'y']

        # iterates through the state of every cube face and determines whether the whole face is composed of the correct colour
        for face_state, face_colour in zip(faces_states, faces_colours):
            for tile_name in ['tl', 'tm', 'tr', 'ml', 'c', 'mr', 'bl', 'bm', 'br']:
                if face_state.__getattribute__(
                        tile_name) != face_colour:  # tile doesn't have the same colour as the cube face color
                    return False  # the Rubik's cube is not solved
        return True

    # part of subgroup 2 criteria
    def __corners_are_oriented(self):
        # upper and down cube faces corner tiles states
        u_and_d_tiles_states = [self.w_face.tl, self.w_face.tr, self.w_face.br, self.w_face.bl,
                                self.y_face.tl, self.y_face.tr, self.y_face.br, self.y_face.bl]

        # if the corner tile on the U or D face is not a U or D colour, the corner cubie with that tile is not oriented
        for tile_state in u_and_d_tiles_states:
            if (tile_state != 'w') and (tile_state != 'y'):
                return False

        # all the corner cubies are oriented.
        return True

    # part of subgroup 3 criteria
    def __corners_are_in_correct_orbit(self):
        # checks if on each cube face, the corner tiles have the same colour.
        for face_state in [self.w_face, self.y_face, self.r_face, self.o_face, self.g_face, self.b_face]:
            if not (face_state.tl == face_state.tr == face_state.bl == face_state.br):
                return False  # the cube face corner tiles are not the same colour

        # each cube face is such that the corner tiles on the face are the same colour
        return True

    def subgroup_number(self):
        # subgroup 1 check
        edge_cubies_state = EdgeCubiesState(self)
        if edge_cubies_state.is_correctly_oriented():

            # subgroup 2 checks
            if self.__corners_are_oriented():
                if edge_cubies_state.has_correct_m_slice():

                    # subgroup 3 check
                    if self.__corners_are_in_correct_orbit():
                        # subgroup 3 criteria has been met.
                        return 3

                    # subgroup 3 criteria is not met. But, subgroup 2 criteria has been met.
                    return 2

            # 'subgroup 2' criteria is not met. But, 'subgroup 1' criteria has been met.
            return 1

        # does not meet any subgroup criteria and so must be in subgroup 0
        return 0
