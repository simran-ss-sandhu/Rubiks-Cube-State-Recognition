from rubiks_cube_state_recognition.cube_capture.VideoFeed import VideoFeed
from rubiks_cube_state_recognition.cube_capture.Frame import Frame
from rubiks_cube_state_recognition.cube_capture.CubeFaceFinder import CubeFaceFinder
from rubiks_cube_state_recognition.cube_capture.ColourFinder import ColourFinder
from rubiks_cube_state_recognition.cube_state.CubeState import CubeFace, CubeState


class CubeStateFinder:
    def __init__(self):
        self.video_feed = VideoFeed(camera_index=0, delay_time=50, cancel_key=' ')  # Video_Feed instance
        self.frame_instance = Frame()  # Frame instance
        self.cube_face_finder = CubeFaceFinder()  # Cube_Face_Finder instance
        self.colour_finder = ColourFinder()  # Colour_Finder instance

        # the names of a cube face's tiles
        self.cube_face_tiles_names = ['tl', 'tm', 'tr',
                                      'ml', 'c', 'mr',
                                      'bl', 'bm', 'br']

        self.cube_face = None  # Square object that contains the coordinates of the current cube face
        self.cube_tile_images = None  # images of each cube tile on the current cube face
        self.cube_tile_colours = None  # colour state of each cube tile on the current cube face
        self.cube_state = CubeState()  # the colour state of the whole Rubik's cube

    def __split_cube_face(self):
        self.cube_tile_images = CubeFace()  # will store each cube tile's image
        cube_tile_length = self.cube_face.length / 3  # estimated cube tile length

        cube_face_tile_name_index = 0
        y_to_add = 0  # amount to add to the y coordinate of the cube face's top left vertex

        # finds every cube tile in the cube face and stores its image in 'cube_tile_images'
        for cube_face_row in range(3):

            # y coordinate of the current cube tile's top left vertex
            tile_tl_vertex_y_coord = int(self.cube_face.tl_vertex_coord[1] + y_to_add)

            # increased by one cube tile length to make the y coordinate of the next vertices go one cubie row lower
            y_to_add += cube_tile_length

            # y coordinate of the current cube tile's bottom right vertex
            tile_br_vertex_y_coord = int(self.cube_face.tl_vertex_coord[1] + y_to_add)

            x_to_add = 0  # amount to add to the x coordinate of the cube face's top left vertex

            for cube_face_column in range(3):
                # x coordinate of the current cube tile's top left vertex
                tile_tl_vertex_x_coord = int(self.cube_face.tl_vertex_coord[0] + x_to_add)

                # increased by one cube tile length to make the x coordinate of the next vertices go one cubie column to the right
                x_to_add += cube_tile_length

                # x coordinate of the current cube tile's bottom right vertex
                tile_br_vertex_x_coord = int(self.cube_face.tl_vertex_coord[0] + x_to_add)

                # applies a bilateral filter to the current cube tile image
                cube_tile_image = self.frame_instance.bilateral_frame[
                    tile_tl_vertex_y_coord:tile_br_vertex_y_coord,
                    tile_tl_vertex_x_coord:tile_br_vertex_x_coord]

                # stores the current cube tile image in the corresponding Cube_Face attribute
                self.cube_tile_images.__setattr__(self.cube_face_tiles_names[cube_face_tile_name_index],
                                                  cube_tile_image)

                # updates for the next cube tile that will be processed
                cube_face_tile_name_index += 1

    def __find_cube_face_state(self):
        self.cube_tile_colours = CubeFace()  # wil store the cube face's colour state

        # finds the dominant colour of each cube tile and stores it in 'cube_tile_colours'
        for cube_face_tile_name in self.cube_face_tiles_names:
            cube_tile_image = self.cube_tile_images.__getattribute__(
                cube_face_tile_name)  # the cube tile image in 'cube_tile_images'
            colour = self.colour_finder.dominant_colour_name(
                cube_tile_image)  # the most dominant colour in the cube tile image
            self.cube_tile_colours.__setattr__(cube_face_tile_name,
                                               colour)  # stores the colour in the appropriate 'cube_tile_colours' attribute

    def update_cube_state(self):
        """
        updates cube state in model using the current video frame
        """
        self.video_feed.update_frame()

        if self.video_feed.frame is None:
            return

        # analyses the video_Feed frame to find the rectangles in it
        frame_rectangles = self.frame_instance.find_rectangles(self.video_feed.frame)

        # analyses the rectangles in frame to find the most likely cube tiles
        cube_tiles = self.cube_face_finder.cube_tiles(frame_rectangles)

        # draws the cube tiles on the current frame
        self.video_feed.draw_squares(
            squares=cube_tiles,
            colour=(255, 255, 255),  # squares are drawn in white (BGR code)
            thickness=1)

        frame_dimensions = (self.video_feed.width, self.video_feed.height)

        # analyses the cube squares to find a cube face
        self.cube_face = self.cube_face_finder.cube_face(frame_dimensions)

        if self.cube_face is not None:  # if a cube face is found

            # draws the cube face on the current frame
            self.video_feed.draw_squares(
                squares=[self.cube_face],
                # all squares in a list are drawn (cube_face is the only square that needs to be drawn)
                colour=(0, 0, 255),  # squares are drawn in red (BGR code)
                thickness=2)  # will be thicker than the cube tiles to stand out more (more important)

            self.__split_cube_face()
            self.__find_cube_face_state()

            # attempts to update the recognised cube face's colour state in 'cube_state'
            self.cube_state.add_face(cube_face=self.cube_tile_colours)

        ##cv2.imshow('cubeState Test', self.video_feed.frame)  # updates the video feed frame in a window
