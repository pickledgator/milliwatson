#!/usr/bin/env python3
from PIL import Image
import pytesseract
import os
import cv2
import pyscreenshot
import numpy

class MilliWatsonOCR:
    """OCR class that performs all cropping and OCR actions.
    Assumes that the image loaded is already cropped down to only the screen
    """
    def __init__(self):
        self.image_name = None
        self.image_data = None
        # self.question = []

    def load_image(self, image_name, show=False):
        """Loads the image into memory
        """
        self.image_name = image_name
        self.image_data = cv2.imread(self.image_name)
        if show:
            self.debug_image(self.image_name, self.image_data)

    def capture_screen(self, bbox=None, show=False, save_filename=None):
        """Capture screen using image as a PIL.Image
        """
        capture = pyscreenshot.grab(bbox)
        # convert to opencv for pre-processing
        self.image_data = pil2cv(capture)
        if show:
            self.debug_image("capture", self.image_data)
        if save_filename:
            cv2.imwrite(save_filename+".jpg", self.image_data)
            print("Saved capture as {}".format(save_filename+".jpg"))

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
        question_x = 25
        question_y = 205
        question_w = 700
        question_h = 280
        result = self.run_ocr_on_image_section(question_x, question_y, question_w, question_h)
        return result


    def get_answer_A(self):
        """Returns the detected text within the first answer section of the image
        """
        answer_a_x = 55
        answer_a_y = 510
        answer_a_w = 650
        answer_a_h = 120
        result = self.run_ocr_on_image_section(answer_a_x, answer_a_y, answer_a_w, answer_a_h)
        return result

    def get_answer_B(self):
        """Returns the detected text within the first answer section of the image
        """
        answer_b_y = 641
        answer_b_h = 760 - answer_b_y
        answer_b_x = 55
        answer_b_w = 650
        result = self.run_ocr_on_image_section(answer_b_x, answer_b_y, answer_b_w, answer_b_h)
        return result

    def get_answer_C(self):
        """Returns the detected text within the first answer section of the image
        """
        answer_c_y = 769
        answer_c_h = 890 - answer_c_y
        answer_c_x = 55
        answer_c_w = 650
        result = self.run_ocr_on_image_section(answer_c_x, answer_c_y, answer_c_w, answer_c_h)
        return result

    def crop(self,image,x,y,w,h,show=False):
        cropped = image[y:y+h, x:x+w]
        return cropped

    def debug_image(self, description, image):
        cv2.namedWindow(description,cv2.WINDOW_NORMAL)
        cv2.resizeWindow(description, 600,600)
        cv2.imshow(description, image)
        cv2.waitKey(5000)

    def run_ocr_on_image_section(self,x,y,w,h,show=False):
        """Runs OCR on a section of image and returns the string detected
        """
        cv_cropped = self.crop(self.image_data, x, y, w, h)
        cv_gray = cv2.cvtColor(cv_cropped, cv2.COLOR_BGR2GRAY)
        (thresh, cv_bw) = cv2.threshold(cv_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        if show:
            self.debug_image("debug",cv_bw)
        img = cv2pil(cv_bw)
        ret_string = pytesseract.image_to_string(img)
        ret_string = ret_string.replace("\n", " ")
        return ret_string


def pil2cv(pil_img):
    return cv2.cvtColor(numpy.array(pil_img), cv2.COLOR_RGB2BGR)

def cv2pil(cv_img):
    return Image.fromarray(cv_img)

def sanitize_file(path_name):
    # Makes sure that the path has
    return os.path.join(os.path.expanduser(path_name))

def main():
    import argparse
    arg_parser = argparse.ArgumentParser(
            description="Reads a single file and splits it into question and answer options")
    arg_parser.add_argument("--input_file", "-i", help="The input file")
    arg_parser.add_argument("--capture", "-c", action='store_true', help="Capture the screen")
    arg_parser.add_argument("--save", "-s", help="Save the image")
    args = arg_parser.parse_args()
    
    mW = MilliWatsonOCR()
    if args.input_file:
        input_file = sanitize_file(args.input_file)
        mW.load_image(input_file,show=False)
    if args.capture:
        filename = args.save if args.save else None
        mW.capture_screen(bbox=(0,23,494,1000), show=True, save_filename=filename)

    question = mW.get_question()
    print("Question: {}".format(question))

    answer_a_string = mW.get_answer_A()
    print("Option A: {}".format(answer_a_string))

    answer_b_string = mW.get_answer_B()
    print("Option B: {}".format(answer_b_string))

    answer_c_string = mW.get_answer_C()
    print("Option C: {}".format(answer_c_string))


if __name__ == "__main__":
    main()
