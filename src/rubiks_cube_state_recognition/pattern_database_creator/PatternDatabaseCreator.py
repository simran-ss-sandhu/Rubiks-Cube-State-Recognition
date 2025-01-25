import sqlite3 as sqlite
from rubiks_cube_state_recognition.pattern_database_creator.PDNode import PDNode
from rubiks_cube_state_recognition.pattern_database_creator.IndexCalculator import IndexCalculator
from rubiks_cube_state_recognition.cube_state.CubeState import CubeFace, CubeState
from rubiks_cube_state_recognition.cube_state.CubiesState import CornerCubiesState, EdgeCubiesState


class PatternDatabaseInteractor:
    def __init__(self):
        self.connection = sqlite.connect(
            'pattern_database.db')  # returns connection object that allows interaction with the database
        self.cursor = self.connection.cursor()  # instance that allows the execution of SQL statements
        self.current_depth = None  # the current depth in the tree consisting of PD_Node's

        # creates the tables for each cubie group
        # index = hash index
        # depth = smallest depth to achieve index in tree = the min number of moves needed to solve the cube state with that index
        self.cursor.execute('''CREATE TABLE if not exists "corner_cubies"(
                                    "index"	INTEGER NOT NULL,
                                    "depth"	INTEGER NOT NULL,
                                    PRIMARY KEY("index"))''')
        self.cursor.execute('''CREATE TABLE if not exists "edge_cubies_1"(
                                    "index"	INTEGER NOT NULL,
                                    "depth"	INTEGER NOT NULL,
                                    PRIMARY KEY("index"))''')
        self.cursor.execute('''CREATE TABLE if not exists "edge_cubies_2"(
                                    "index"	INTEGER NOT NULL,
                                    "depth"	INTEGER NOT NULL,
                                    PRIMARY KEY("index"))''')
        self.commit()

    def __fetch_depth(self, table_name: str, index: int):
        # returns the search result for the depth in records in a specific table with a specific index
        sql = f'''SELECT "depth" FROM "{table_name}" WHERE "index" = {index}'''
        self.cursor.execute(sql)
        depth = self.cursor.fetchall()
        return depth  # returns the found depths

    def __insert_record(self, table_name: str, index: int):
        # inserts the index and depth to the appropriate table
        sql = f'INSERT INTO {table_name} VALUES ({index}, {self.current_depth})'
        self.cursor.execute(sql)

    def did_add_record(self, table_name: str, index: int):
        if self.__fetch_depth(table_name, index):  # if a depth has been fetched
            return False

        # inserts the record if there is no record with the new index
        else:
            self.__insert_record(table_name, index)
            return True

    def commit(self):
        # makes database changes visible to all applications using the database (permanently writes)
        self.connection.commit()

    def close(self):
        # closes the connection to the database
        self.connection.close()


class PatternDatabaseCreator:
    def __init__(self):
        self.pattern_database = PatternDatabaseInteractor()
        self.corner_cubies_index_calculator = IndexCalculator(
            number_of_cubies=8,
            lehmer_bases=[5040, 720, 120, 24, 6, 2, 1],  # element = (8-1-index)!
            orientation_bases=[1, 3, 9, 27, 81, 243, 729, 2187])  # element= 3**index
        self.edge_cubies_index_calculator = IndexCalculator(
            number_of_cubies=12,
            lehmer_bases=[332640, 30240, 3024, 336, 42, 6, 1],  # element = (12-1-index)P(7-1-index)
            orientation_bases=[1, 2, 4, 8, 16, 32, 64,
                               128, 256, 512, 1024, 2048])  # element = 2**index

        # creates a Cube_State object of the solved Rubik's cube state
        solved_cube_state = CubeState()
        for colour in ['w', 'g', 'r', 'b', 'o', 'y']:
            cube_face = CubeFace()
            cube_face_tiles_names = ['tl', 'tm', 'tr',
                                     'ml', 'c', 'mr',
                                     'bl', 'bm', 'br']
            for cube_face_tile_name in cube_face_tiles_names:
                cube_face.__setattr__(cube_face_tile_name, colour)
            solved_cube_state.__setattr__(colour + '_face', cube_face)

        root_tree_node = PDNode(cube_state=solved_cube_state, last_turn=None)

        # initialises the node processing queues
        self.node_queues = {0: [root_tree_node]}  # places the root node at depth 0 (as expected for a tree)
        for depth in range(1, 13):  # creates 13 queues for each tree depth. Every state can be achieved
            self.node_queues[depth] = []

        # initialises the tree depth variables (for tracking)
        self.current_depth = 0  # the tree is generated from the root and so the current depth is initialised to 0
        self.pattern_database.current_depth = self.current_depth  # links the two attributes together
        self.next_depth = 1  # current depth + 1

    def __process_node(self, node: PDNode):
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

        # adds children to the processing queue for the next depth if the record is added to the corner_cubies table
        if self.pattern_database.did_add_record('corner_cubies', corners_hash_index):
            self.pattern_database.did_add_record('edge_cubies_1', edges_hash_index_1)
            self.pattern_database.did_add_record('edge_cubies_2', edges_hash_index_2)
            node.create_children()  # creates children for the current node
            self.node_queues[self.next_depth].extend(
                node.children)  # adds the children to the next depth's processing queue

    def generate(self):
        while self.current_depth <= 12:
            # processes nodes in the node processing queue at the current depth
            for node in self.node_queues[self.current_depth]:
                self.__process_node(node)
                del (self.node_queues[self.current_depth][
                    0])  # removes the node at the front of the processed queue to save memory

            # makes database record insertions visible to all applications using the database (permanently writes)
            self.pattern_database.commit()

            # updates the depth attributes to prepare the processing at the next depth
            self.current_depth = self.next_depth
            self.pattern_database.current_depth = self.current_depth
            self.next_depth += 1

        # closes the connection to the database once all possible cube states have been analysed.
        self.pattern_database.close()


pattern_database_creator = PatternDatabaseCreator()
pattern_database_creator.generate()
