import cv2
import numpy as np  # for efficient array manipulation
from rubiks_cube_state_recognition.cube_capture.Rectangle import Rectangle
from rubiks_cube_state_recognition.cube_capture.VideoFeed import VideoFeed


class Frame:
    def __init__(self):
        self.frame = None  # the frame to modify
        self.filtered_frame = None  # the frame with filters applied to it

        # bilateral settings
        self.d = 10
        self.sigma_values = 255
        self.bilateral_frame = None  # frame with the bilateral filter on it

        # threshold settings
        self.adaptive_method = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
        self.threshold_type = cv2.THRESH_BINARY_INV  # causes processed pixels to be converted to black or white
        self.block_size = 53  # the size of the block of frame pixels that are compared to each other
        self.c = 7  # constant to subtract from the calculated threshold values

        self.large_contours = None
        self.min_contour_area = 700  # the minimum area of a contour needed to be returned

        self.rectangles = None  # contours as rectangles

    # null function that is needed as a function for OpenCV's trackbars
    # when the trackbar slider is moved, this function is called
    def __nothing(self, null):
        pass

    def calibrate_filters(self, video_feed: VideoFeed):
        video_feed.choose_frame()

        # temporary (until GUI is made)
        cv2.namedWindow('sliders')  # creates window for setting trackbars

        # creates trackbar for d setting
        cv2.createTrackbar(
            'd',  # trackbar name
            'sliders',  # window it belongs to
            self.d,  # initial trackbar value
            25,  # maximum trackbar value (range: 0 -> value)
            self.__nothing)  # function that is run when trackbar slider is moved

        # creates trackbar for the sigma_values setting
        cv2.createTrackbar(
            'sigma_values',
            'sliders',
            self.sigma_values,
            255,
            self.__nothing)

        # creates trackbar for the block_size setting
        cv2.createTrackbar(
            'block_size',
            'sliders',
            self.block_size,
            200,
            self.__nothing)

        # creates trackbar for the c setting
        cv2.createTrackbar(
            'c',
            'sliders',
            self.c,
            30,
            self.__nothing)

        while not video_feed.break_condition_met():  # keeps window open until the cancel key is pressed two times in a row

            # updates the attributes with the value in their corresponding trackbar in the sliders window
            self.sigma_values = cv2.getTrackbarPos(trackbarname='sigma_values', winname='sliders')
            self.c = cv2.getTrackbarPos(trackbarname='c', winname='sliders')

            # validates d trackbar slider input
            d_input = cv2.getTrackbarPos(trackbarname='d', winname='sliders')
            if d_input > 0:
                self.d = d_input

            # validates block_size trackbar slider input
            block_size_input = cv2.getTrackbarPos(trackbarname='block_size', winname='sliders')
            if (block_size_input % 2 == 1) and (block_size_input > 1):
                self.block_size = block_size_input

            self.frame = video_feed.frame
            self.__find_filtered_frame()  # filters chosen frame with changed setting
            cv2.imshow(winname='filtered_frame', mat=self.filtered_frame)  # shows the updated filtered frame
        cv2.destroyAllWindows()  # closes all open windows

    def __find_filtered_frame(self):  # applies bilateral filter and then greyscale filter and then adaptive thresholding
        self.bilateral_frame = cv2.bilateralFilter(self.frame, self.d, self.sigma_values,
                                                   self.sigma_values)  # applies bilateral filter to original frame
        greyscale_frame = cv2.cvtColor(self.bilateral_frame,
                                       cv2.COLOR_BGR2GRAY)  # converts bilaterally filtered frame to greyscale
        adaptive_threshold_frame = cv2.adaptiveThreshold(
            greyscale_frame,
            255,  # maximum threshold value
            self.adaptive_method,
            self.threshold_type,
            self.block_size,
            self.c)
        self.filtered_frame = adaptive_threshold_frame

    def __find_large_contours(self):
        contours, _ = cv2.findContours(
            self.filtered_frame,
            cv2.RETR_TREE,  # contour mode
            cv2.CHAIN_APPROX_NONE)  # contour method

        # creates list with contours larger than the minimum contour area attribute
        self.large_contours = [contour for contour in contours if cv2.contourArea(contour) > self.min_contour_area]

    def __find_rectangles_in_contours(self):
        self.rectangles = []  # every contour represented as a rectangle
        for contour in self.large_contours:

            # find the coordinates of the (approximate) vertices in the contour shape
            vertices = cv2.approxPolyDP(
                curve=contour,

                # the higher the value, the more a curve is approximated (fewer vertices)
                epsilon=0.01 * cv2.arcLength(  # arc length = perimeter of the contour
                    curve=contour,
                    closed=True),  # all contour points are connected (closed)

                # all contour points are connected
                closed=True)

            # finds the smallest x and y values in the vertices coordinates
            smallest_x, smallest_y = np.amin(a=vertices, axis=0)[0]

            # finds the largest x and y values in the vertice coordinates
            largest_x, largest_y = np.amax(a=vertices, axis=0)[0]

            if (smallest_x != largest_x) and (
                    smallest_y != largest_y):  # if the smallest and largest coordinates aren't the same
                tl_vertex_coord = (smallest_x, smallest_y)  # top left vertex coordinate
                br_vertex_coord = (largest_x, largest_y)  # bottom right vertex coordinate
                rectangle = Rectangle(tl_vertex_coord,
                                      br_vertex_coord)  # uses rectangle module I have created to work out rectangle attributes (width, height, etc.)
                self.rectangles.append(rectangle)

    def find_rectangles(self, frame: list):
        self.frame = frame  # the frame that will be processed
        self.__find_filtered_frame()
        self.__find_large_contours()
        self.__find_rectangles_in_contours()
        return self.rectangles
