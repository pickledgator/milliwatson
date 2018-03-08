#!/usr/bin/env python3

import configparser
from PIL import Image
from PIL import ImageDraw
import pytesseract
import os
import cv2
import logging

logging.basicConfig(format='(%(levelname)s) %(message)s', level=logging.INFO)


class OCR:
    """OCR class that performs all cropping and OCR actions.
    Assumes that the image loaded is already cropped down to only the screen.
    Cropping boundaries are currently hard-coded for use on an iPhoneX
    """

    def __init__(self, config_file):
        self.image_name = None
        self.cv_image_data = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Loading config file: {}".format(config_file))
        config_parse = configparser.ConfigParser()
        config_parse.read(config_file)
        self.config = dict(config_parse['DEFAULT'])
        # ensure all values are ints
        self.config = dict((k, int(v)) for k, v in self.config.items())
        # All text boxes have the same left alignment
        self.LEFT_ALIGN = 27
        # All text boxes have the same right alignment
        self.WIDTH = 785 - self.LEFT_ALIGN
        # All answer boxes have the same height
        self.ANSWER_HEIGHT = 120

    def load_image(self, image_name, show=True):
        """Loads the image into memory
        """
        self.image_name = image_name
        self.image_data = Image.open(image_name)

    def draw_bounds(self, x, y, w, h):
        image_draw = ImageDraw.Draw(self.image_data)
        image_draw.rectangle([x, y, x + w, y + h], outline="red")

    def capture_screen(self, show=False):
        """Capture screen and save image as a PIL.Image
        """
        self.logger.info("Grabbing screen data")
        # use Applescript to find the windowid param to pass to screencapture
        # TODO(curtismuntz): Figure out similar tool for Ubuntu/android
        os.system(
            "screencapture -l$(osascript -e 'tell app \"QuickTime Player\" to id of window 1') tmp.png")
        self.image_data = Image.open("tmp.png")
        if show:
            self.image_data.show()

    def split_image(self, show=False):
        """Parses the image into four chunks.
        1: Question section
        2: Answer A
        3: Answer B
        4: Answer C
        """
        question = self.get_question(show)
        answer_a = self.get_answer_A(show)
        answer_b = self.get_answer_B(show)
        answer_c = self.get_answer_C(show)
        return question, answer_a, answer_b, answer_c

    def image(self):
        """Returns the image data
        """
        return self.image_data

    def name(self):
        """Returns the name of the image stored within the OCR class
        """
        return self.image_name

    def get_question(self, show=False):
        """Returns the detected text within the question section of the image
        """
        self.logger.info("Processing question")
        x = self.config['horizontal_padding'] + \
            self.config['question_left_margin']
        y = self.config['question_top_margin'] + \
            self.config['vertical_padding']  # 270
        w = self.config['capture_width'] - self.config['horizontal_padding'] - \
            self.config['question_right_margin'] - \
            self.config['question_left_margin'] - \
            self.config['horizontal_padding']
        h = self.config['question_height']
        self.draw_bounds(x, y, w, h)
        result = self.run_ocr_on_image_section(x, y, w, h, show)
        return result

    def get_answer_A(self, show=False):
        """Returns the detected text within the first answer section of the image
        """
        self.logger.info("Processing answer 1")
        x = self.config['horizontal_padding'] + \
            self.config['answer_left_margin']
        y = self.config['vertical_padding'] + self.config['question_top_margin'] + \
            self.config['question_height'] + \
            self.config['answer_first_top_margin']
        w = self.config['capture_width'] - self.config['horizontal_padding'] - \
            self.config['answer_right_margin'] - \
            self.config['answer_left_margin'] - \
            self.config['horizontal_padding']
        h = self.config['answer_height']
        self.draw_bounds(x, y, w, h)
        result = self.run_ocr_on_image_section(x, y, w, h, show)
        return result

    def get_answer_B(self, show=False):
        """Returns the detected text within the second answer section of the image
        """
        self.logger.info("Processing answer 2")
        x = self.config['horizontal_padding'] + \
            self.config['answer_left_margin']
        y = self.config['vertical_padding'] + self.config['question_top_margin'] + \
            self.config['question_height'] + \
            self.config['answer_first_top_margin'] + \
            1 * self.config['answer_height']
        w = self.config['capture_width'] - self.config['horizontal_padding'] - \
            self.config['answer_right_margin'] - \
            self.config['answer_left_margin'] - \
            self.config['horizontal_padding']
        h = self.config['answer_height']
        self.draw_bounds(x, y, w, h)
        result = self.run_ocr_on_image_section(x, y, w, h, show)
        return result

    def get_answer_C(self, show=False):
        """Returns the detected text within the third answer section of the image
        """
        self.logger.info("Processing answer 3")
        x = self.config['horizontal_padding'] + \
            self.config['answer_left_margin']
        y = self.config['vertical_padding'] + self.config['question_top_margin'] + \
            self.config['question_height'] + \
            self.config['answer_first_top_margin'] + \
            2 * self.config['answer_height']
        w = self.config['capture_width'] - self.config['horizontal_padding'] - \
            self.config['answer_right_margin'] - \
            self.config['answer_left_margin'] - \
            self.config['horizontal_padding']
        h = self.config['answer_height']
        self.draw_bounds(x, y, w, h)
        result = self.run_ocr_on_image_section(x, y, w, h, show)
        return result

    def save_image(self, save_filename):
        self.image_data.save(save_filename + ".png")
        self.logger.info("Saved capture as {}".format(save_filename + ".png"))

    def crop(self, image, x, y, w, h, show=False):
        """Returns a cropped image

        Args:
            image: an opencv image
            x: The minimum x pixel to be cropped
            y: The minimum y pixel to be cropped
            w: The width of the crop (x max - x min)
            h: The height of the crop (y max - y min)

        Returns:
            cropped: an opencv image that has been cropped to the desired dims
        """
        cropped = image[y:y + h, x:x + w]
        return cropped

    def debug_image(self, description, image, wait=5000):
        """Displays an image for debug purposes

        Args:
            description: string to title the display window
            image: opencv image to display
        """
        cv2.namedWindow(description, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(description, 600, 600)
        cv2.imshow(description, image)
        cv2.waitKey(wait)

    def run_ocr_on_image_section(self, x, y, w, h, show=False):
        """Runs OCR on a section of image and returns the string detected
        """
        cropped = self.image_data.crop((x, y, x + w, y + h))
        gray = cropped.convert('L')
        img = gray.point(lambda x: 0 if x < 200 else 255, '1')
        # if show:
        #     img.show()
        ret_string = pytesseract.image_to_string(img)
        ret_string = ret_string.replace("\n", " ")
        return ret_string


def sanitize_file(file_name):
    """ Some basic file name sanitization
    """
    return os.path.expanduser(file_name)


def main():
    import argparse
    arg_parser = argparse.ArgumentParser(
        description="Reads a single file and splits it\
         into question and answer options")
    arg_parser.add_argument("--input_file", "-i", help="The input file")
    arg_parser.add_argument("--config_file", "-f",
                            help="The phone config file (default: iphone_x_macpro_2880x1800)",
                            default="configs/iphone_x_macpro_2880x1800")
    arg_parser.add_argument("--capture", "-c", action='store_true',
                            help="Capture the screen")
    arg_parser.add_argument("--save", "-s", help="Save the image")
    arg_parser.add_argument("--display", "-d", action='store_true',
                            help="Display the image")
    args = arg_parser.parse_args()

    # verify config file exists
    if not os.path.exists(args.config_file):
        print("Must provide valid phone config file (-f)")
        exit(-1)

    ocr = OCR(args.config_file)
    if args.input_file:
        input_file = sanitize_file(args.input_file)
        ocr.load_image(input_file, show=True)
    if args.capture:
        ocr.capture_screen(show=True)
    if args.save:
        ocr.save_image(args.save)

    question, a_str, b_str, c_str = ocr.split_image(args.display)
    ocr.image_data.show()

    print("Question: {}".format(question))
    print("Option A: {}".format(a_str))
    print("Option B: {}".format(b_str))
    print("Option C: {}".format(c_str))


if __name__ == "__main__":
    main()
