class Rectangle:
    def __init__(self, tl_vertex_coord: list, br_vertex_coord: list):  # coordinates format = (x, y)
        self.tl_vertex_coord = tl_vertex_coord  # the coordinate of the top left vertex of the rectangle
        self.br_vertex_coord = br_vertex_coord  # the coordinates of the bottom right vertex of the rectangle
        self.width = self.br_vertex_coord[0] - self.tl_vertex_coord[0]  # width = largest_x - smallest_x
        self.height = self.br_vertex_coord[1] - self.tl_vertex_coord[1]  # height = largest_y - smallest_y
        self.aspect_ratio = self.width / self.height  # an aspect ratio of 1 means that the rectangle is a square


class Square:
    def __init__(self, rectangle: Rectangle):
        self.tl_vertex_coord = rectangle.tl_vertex_coord
        self.br_vertex_coord = rectangle.br_vertex_coord
        self.length = (rectangle.width + rectangle.height) / 2  # the average length of the rectangle's width and length
        self.area = self.length ** 2

    def is_in_rectangle(self, outer_rectangle: Rectangle):
        x_is_within_tl = outer_rectangle.tl_vertex_coord[0] < self.tl_vertex_coord[0]
        y_is_within_tl = outer_rectangle.tl_vertex_coord[1] < self.tl_vertex_coord[1]

        # If the square's top left corner is within the rectangle's top left corner
        if x_is_within_tl and y_is_within_tl:

            x_is_within_br = (self.br_vertex_coord[0] < outer_rectangle.br_vertex_coord[0])
            y_is_within_br = (self.br_vertex_coord[1] < outer_rectangle.br_vertex_coord[1])

            # If the square's bottom right corner is within the rectangle's bottom right corner
            if x_is_within_br and y_is_within_br:
                return True  # the square is within both corners of the rectangle

        return False  # the square is not within the rectangle if True is not returned
