import cv2


class VideoFeed:
    def __init__(self, camera_index: int, delay_time: int, cancel_key: int):
        self.camera_index = camera_index  # the chosen camera (0 is default)
        self.video_capture = cv2.VideoCapture(camera_index)  # assigns variable to the selected camera
        self.width = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))  # the width of the frames retrieved from video_capture
        self.height = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))  # the height of the frames retrieved from video_capture
        self.delay_time = delay_time  # the delay time in between frames in milliseconds
        self.cancel_key = ord(cancel_key)  # the key in unicode required to break the loop and stop the video feed
        self.frame = None

    def update_frame(self):
        _, self.frame = self.video_capture.read()  # captures frame from video_capture

    # returns True when the cancel key is pressed twice in a row
    def break_condition_met(self):
        key = cv2.waitKey(self.delay_time) & 0xFF
        if key == self.cancel_key:
            key = cv2.waitKey(0) & 0xFF  # pauses the frame until another key is pressed
            if key == self.cancel_key:  # stops the video feed, causing the value of self.frame to be the chosen frame
                return True
        return False

    def choose_frame(self):
        while not self.break_condition_met():
            self.update_frame()
            cv2.imshow(winname='chosen_frame', mat=self.frame)  # shows frame in window, temporary (until GUI is made)

    def draw_squares(self, squares: list, colour: list, thickness: int):

        # draws every square in the squares list
        for square in squares:
            cv2.rectangle(
                img=self.frame,  # rectangle is drawn onto the frame
                pt1=square.tl_vertex_coord,  # rectangle from top left vertex
                pt2=square.br_vertex_coord,  # to bottom right vertex
                color=colour,  # the colour of the rectangle
                thickness=thickness)  # the thickness of the rectangle sides
