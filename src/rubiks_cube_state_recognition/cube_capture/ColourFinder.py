import cv2  # imports OpenCV
import numpy as np  # imports numpy for array manipulation


class Colour:
    def __init__(self, colour: str, minimum_hue: int, maximum_hue: int):
        self.colour = colour  # colour name
        self.minimum_hue = minimum_hue  # the minimum hue required for the colour
        self.maximum_hue = maximum_hue  # the maximum hue allowed for the colour


class ColourFinder:
    def __init__(self):
        self.colours = [
            Colour('r', 177.5, 6.24),  # red object. Special case -> (larger than 177.5) or (between 0 and 5)
            Colour('o', 6.26, 22.74),  # orange object
            Colour('y', 22.76, 35.24),  # yellow object
            Colour('g', 35.26, 90.24),  # green object
            Colour('b', 90.26, 120)]  # blue object
        self.non_white_min_saturation = 127.5  # the minimum saturation required for a colour to not be white
        self.non_white_min_brightness = 127.5  # the maximum brightness allowed for a colour to not be white
        self.white_max_saturation = 70  # the maximum saturation allowed for a colour to be white
        self.white_min_brightness = 120  # the minimum brightness required for a colour to be white
        self.frame = None
        self.dominant_HSB = None  # the most dominant colour in frame

    def __find_dominant_hsb(self):
        hsb_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)  # converts every pixel to a HSB colour format from BGR

        # converts the array to a float32 datatype (required for k-means clustering)
        pixels = np.float32(
            hsb_frame.reshape(
                -1,  # reshapes the frame with as many elements as required
                3))  # reshapes the frame so that every pixel (an array) contains 3 elements

        # data clustering to split the pixels into different colour groups
        labels, palette = cv2.kmeans(
            data=pixels,  # the data to apply the k-means clustering operation on
            K=6,  # the number of clusters to split the data by (number of colours)
            bestLabels=None,
            criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1),  # the algorithm's iteration termination criteria
            attempts=10,  # the number of times the algorithm is executed using different initial labellings
            flags=cv2.KMEANS_RANDOM_CENTERS)[1:]  # method for how initial centers are taken

        counts = np.unique(labels, return_counts=True)[1]  # array of the number of times every label in labels is repeated
        max_count_index = np.argmax(counts)  # index of the largest element in the counts array
        self.dominant_HSB = palette[max_count_index].astype(int)  # the most dominant (repeated) HSB colour

    def __find_hsb_colour_name(self):
        hue, saturation, brightness = self.dominant_HSB  # splits the HSB array into separate variables

        # checks for red, orange, yellow, green and blue colours
        if (saturation >= self.non_white_min_saturation) and (brightness >= self.non_white_min_brightness):  # the brightness and saturation don't satisfy the ranges for grey/black

            # special case check for the colour red
            if (hue >= self.colours[0].minimum_hue) or (hue <= self.colours[0].maximum_hue):  # the hue is within the red hue range
                return 'r'

            # check for orange, yellow, green and blue
            for colour_instance in self.colours[1:]:
                if (hue >= colour_instance.minimum_hue) and (hue <= colour_instance.maximum_hue):  # the hue is within the colour instance's hue range
                    return colour_instance.colour  # the colour instance's colour name is returned

        # checks for white if the checks for the other colours fail
        if (saturation <= self.white_max_saturation) and (brightness >= self.white_min_brightness):
            return 'w'

        # if the checks for red, orange, yellow, green, blue and white fail,
        #   it is unlikely for the dominant HSB colour to be any useful colour
        # 'None' is returned

    def dominant_colour_name(self, frame: list):
        self.frame = frame
        self.__find_dominant_hsb()
        return self.__find_hsb_colour_name()
