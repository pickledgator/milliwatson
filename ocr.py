#!/usr/bin/env python3
from PIL import Image
import pytesseract
import os
import cv2
import numpy
import logging

class OCR:
    """OCR class that performs all cropping and OCR actions.
    Assumes that the image loaded is already cropped down to only the screen
    """
    def __init__(self):
        self.image_name = None
        self.image_data = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.LEFT_ALIGN = 35
        self.WIDTH = 955 - self.LEFT_ALIGN
        # self.question = []

    def load_image(self, image_name, show=False):
        """Loads the image into memory
        """
        self.image_name = image_name
        self.image_data = Image.open(image_name)
        if show:
            self.image_data.show()

    def capture_screen(self, bbox=None, show=False):
        """Capture screen and save image as a PIL.Image
        """
        self.logger.info("Grabbing screen data")
        os.system("screencapture -R{},{},{},{} tmp.png".format(bbox[0],bbox[1],bbox[2],bbox[3]))
        self.image_data = Image.open("tmp.png")
        if show:
            self.image_data.show()

    def split_image(self):
        """Parses the image into four chunks.
        1: Question section
        2: Answer A
        3: Answer B
        4: Answer C
        """
        raise NotImplementedError
    
    def image(self):
        return self.image_data

    def name(self):
        return self.image_name

    def get_question(self):
        """Returns the detected text within the question section of the image
        """
        self.logger.info("Processing question")
        question_x = self.LEFT_ALIGN
        question_y = 270
        question_w = self.WIDTH
        question_h = 664 - question_y
        result = self.run_ocr_on_image_section(question_x, question_y, question_w, question_h, False)
        return result

    def get_answer_A(self):
        """Returns the detected text within the first answer section of the image
        """
        self.logger.info("Processing answer 1")
        answer_a_x = self.LEFT_ALIGN
        answer_a_y = 670
        answer_a_w = self.WIDTH
        answer_a_h = 825-answer_a_y
        result = self.run_ocr_on_image_section(answer_a_x, answer_a_y, answer_a_w, answer_a_h, False)
        return result

    def get_answer_B(self):
        """Returns the detected text within the first answer section of the image
        """
        self.logger.info("Processing answer 2")
        answer_b_y = 843
        answer_b_h = 996 - answer_b_y
        answer_b_x = self.LEFT_ALIGN
        answer_b_w = self.WIDTH
        result = self.run_ocr_on_image_section(answer_b_x, answer_b_y, answer_b_w, answer_b_h, False)
        return result

    def get_answer_C(self):
        """Returns the detected text within the first answer section of the image
        """
        self.logger.info("Processing answer 3")
        answer_c_y = 1013
        answer_c_h = 1167 - answer_c_y
        answer_c_x = self.LEFT_ALIGN
        answer_c_w = self.WIDTH
        result = self.run_ocr_on_image_section(answer_c_x, answer_c_y, answer_c_w, answer_c_h, False)
        return result

    def save_image(self, save_filename):
        self.image_data.save(save_filename+".png")
        self.logger.info("Saved capture as {}".format(save_filename+".png"))

    def run_ocr_on_image_section(self,x,y,w,h,show=False):
        """Runs OCR on a section of image and returns the string detected
        """
        cropped = self.image_data.crop((x, y, x+w, y+h))
        gray = cropped.convert('L')
        img = gray.point(lambda x: 0 if x<200 else 255, '1')
        if show:
            img.show()
        ret_string = pytesseract.image_to_string(img)
        ret_string = ret_string.replace("\n", " ")
        return ret_string

def sanitize_file(path_name):
    # Makes sure that the path has
    return os.path.join(os.path.expanduser(path_name))

def main():
    import argparse
    arg_parser = argparse.ArgumentParser(
            description="Reads a single file and splits it into question and answer options")
    arg_parser.add_argument("--input_file", "-i", help="The input file", default="capture_1.jpg")
    arg_parser.add_argument("--capture", "-c", action='store_true', help="Capture the screen")
    arg_parser.add_argument("--save", "-s", help="Save the image")
    args = arg_parser.parse_args()

    ocr = OCR()
    if args.input_file:
        input_file = sanitize_file(args.input_file)
        ocr.load_image(input_file,show=True)
    if args.capture:
        ocr.capture_screen(bbox=(0,23,494,1000), show=True)
    if args.save:
        ocr.save_image(args.save)

    question = ocr.get_question()
    print("Question: {}".format(question))

    answer_a_string = ocr.get_answer_A()
    print("Option A: {}".format(answer_a_string))

    answer_b_string = ocr.get_answer_B()
    print("Option B: {}".format(answer_b_string))

    answer_c_string = ocr.get_answer_C()
    print("Option C: {}".format(answer_c_string))


if __name__ == "__main__":
    main()
