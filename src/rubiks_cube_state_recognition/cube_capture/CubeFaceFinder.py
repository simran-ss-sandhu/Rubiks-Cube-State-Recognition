from rubiks_cube_state_recognition.cube_capture.Rectangle import Rectangle, Square
from rubiks_cube_state_recognition.cube_capture.LinkedList import LinkedList, LlNode


class CubeFaceFinder:
    def __init__(self):
        # values are accepted if they are within 20% of each other
        self.lower_min_accuracy = 0.8
        self.upper_min_accuracy = 1.2

        # used in catchment box
        # cube tiles can only ever be 2 of their side length away from each other
        # 0.5 more of their side length is used to be more lenient
        self.side_length_multiplier = 2.5

        self.rectangles = None  # list of rectangle objects
        self.squares = None  # rectangles that have been input that are squares
        self.cube_squares = None  # linked list of squares likely to be cube tiles or faces

    def __is_accurate_ratio(self, ratio: float):
        # returns True if the ratio is between the lower_min_accuracy and upper_min_accuracy
        if self.lower_min_accuracy <= ratio:
            if ratio <= self.upper_min_accuracy:
                return True
        return False  # return False otherwise

    def __find_squares(self):
        # all rectangles that are squares (or almost one)
        self.squares = [Square(rectangle) for rectangle in self.rectangles if
                        self.__is_accurate_ratio(rectangle.aspect_ratio)]

    def __find_cube_squares(self):
        self.cube_squares = LinkedList()  # linked list of groups of squares that are each likely to a part of a Rubik's cube
        square_index = 0  # index of the current square

        # finds groups of squares that are close to each other by comparing every square
        for square in self.squares[:-1]:
            possible_cube_tiles = []  # squares close to the current square and of a similar size
            possible_cube_faces = []  # squares close to the current square and 9 times larger than the current square

            # creates a catchment box around the current square (squares within this box are close to the current square)
            cb_half_of_side_length = square.length * self.side_length_multiplier
            cb_tl_vertex_coord = [square.tl_vertex_coord[0] - cb_half_of_side_length,
                                  square.tl_vertex_coord[1] - cb_half_of_side_length]
            cb_br_vertex_coord = [square.br_vertex_coord[0] + cb_half_of_side_length,
                                  square.br_vertex_coord[1] + cb_half_of_side_length]
            catchment_box = Rectangle(cb_tl_vertex_coord, cb_br_vertex_coord)

            next_square_index = square_index + 1
            for next_square in self.squares[square_index + 1:]:  # only compares to squares before the current square
                if next_square.is_in_rectangle(catchment_box):  # if the current next square is near the current square
                    area_ratio = square.area / next_square.area

                    # the squares are of a similar size (possible cube tiles)
                    if self.__is_accurate_ratio(area_ratio):
                        possible_cube_tiles.append(next_square)
                        if not possible_cube_tiles:  # list is empty
                            possible_cube_tiles.append(square)

                    # the squares mya have a cube tile to cube face ratio
                    else:
                        # allows the ratio to be compared to 1 (to be used in the isAccurateRatio method)
                        normalised_ratio = area_ratio / 9

                        if self.__is_accurate_ratio(normalised_ratio):  # square is 9 times larger than next_square
                            if next_square.is_in_rectangle(square):  # next_square should be inside of square
                                possible_cube_faces.append(square)  # square could be a cube face
                                possible_cube_tiles.append(next_square)  # next_square could be a cube tile

                        else:
                            normalised_ratio_inverse = area_ratio * 9
                            if self.__is_accurate_ratio(
                                    normalised_ratio_inverse):  # next_square is 9 times larger than square
                                if square.is_in_rectangle(next_square):  # square should be inside of next_square
                                    possible_cube_faces.append(next_square)  # next_square could be a cube face
                                    possible_cube_tiles.append(square)  # square could be a cube tile

                next_square_index += 1  # updates index to another square in front of the current square

            # adds the possible cube squares to the linked list
            if possible_cube_tiles or possible_cube_faces:  # if one of the lists are not empty
                node = LlNode(possible_cube_tiles=possible_cube_tiles, possible_cube_faces=possible_cube_faces)
                self.cube_squares.insert_node(node)

            # current square has been compared to all other squares
            square_index += 1  # the next square (not next_square) in the list becomes the current square

    def cube_tiles(self, rectangles: list):
        self.rectangles = rectangles  # rectangles in the frame (for the 'find_squares' method)
        self.__find_squares()  # finds squares in rectangles
        self.__find_cube_squares()  # finds cube squares in the squares and stores these in a linked list
        if self.cube_squares.nodes:  # if there are nodes in the linked list
            index = self.cube_squares.start_pointer
            longest_node = self.cube_squares.nodes[index]  # first node
            return longest_node.possible_cube_tiles  # returns the first node (has the most cube tiles)
        return []  # else, there are no possible cube tiles for the current frame

    def cube_face(self, frame_dimensions: list):
        if self.cube_squares.nodes:  # there are nodes in the linked list
            current_node = self.cube_squares.nodes[self.cube_squares.start_pointer]  # first node

            # iterates through every node in the linked list
            while True:
                cube_tiles_side_length_sum = 0

                # initialises smallest and largest x and y values
                smallest_x, smallest_y = frame_dimensions  # smallest x and y values are set as high as possible, so it only can be lowered
                largest_x, largest_y = 0, 0  # largest x and y values are set as low as possible, so it can only raised

                # finds the smallest and largest x and y values out of all the cube tiles in the current node
                for cube_tile in current_node.possible_cube_tiles:
                    cube_tiles_side_length_sum += cube_tile.length  # used to find the average cube tile side length later

                    # x coordinate of the top left corner contains the smallest x coordinate
                    if cube_tile.tl_vertex_coord[0] < smallest_x:
                        smallest_x = cube_tile.tl_vertex_coord[0]

                    # y coordinate of the top left corner contains the smallest y coordinate
                    if cube_tile.tl_vertex_coord[1] < smallest_y:
                        smallest_y = cube_tile.tl_vertex_coord[1]

                    # x coordinate of the bottom right corner contains the largest x coordinate
                    if cube_tile.br_vertex_coord[0] > largest_x:
                        largest_x = cube_tile.br_vertex_coord[0]

                    # y coordinate of the bottom right corner contains the largest y coordinate
                    if cube_tile.br_vertex_coord[1] > largest_y:
                        largest_y = cube_tile.br_vertex_coord[1]

                # calculates the expected cube face side length using the average side length of all the cube tiles in the current node
                cube_tiles_avg_side_length = cube_tiles_side_length_sum / len(current_node.possible_cube_tiles)
                expected_cube_face_side_length = cube_tiles_avg_side_length * 3

                # calculates the height of a cube face that would be formed by the smallest and largest y values
                actual_cube_face_height = largest_y - smallest_y

                # calculates the ratio between the expected cube face height and the 'actual' cube face height
                heights_ratio = actual_cube_face_height / expected_cube_face_side_length

                if self.__is_accurate_ratio(
                        heights_ratio):  # the 'actual' cube face height is similar to what is expected

                    # calculates the width of a cube face that would be formed by the smallest and largest x values
                    actual_cube_face_width = largest_x - smallest_x

                    # calculates the ratio between the expected cube face width and the 'actual' cube face width
                    widths_ratio = actual_cube_face_width / expected_cube_face_side_length

                    # returns the formed cube face if it is similar to what would be expected
                    if self.__is_accurate_ratio(
                            widths_ratio):  # the 'actual' cube face width is similar to what is expected

                        # creates a Rectangle object of the formed cube face
                        square = Rectangle(
                            tl_vertex_coord=(smallest_x, smallest_y),
                            br_vertex_coord=(largest_x, largest_y))

                        return Square(square)  # returns the object (the cube face)

                # there are no more nodes to search through in the linked list
                if current_node.next_pointer is None:  # the current node is the last node in the linked list
                    break

                # there are more nodes in the linked list to search through
                else:
                    current_node = self.cube_squares.nodes[
                        current_node.next_pointer]  # current node becomes the next node in the linked list

        # at this point, there are no nodes in the linked list that contains a likely cube face (None is returned)
