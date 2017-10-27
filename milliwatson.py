#!/usr/bin/env python3

import os
import sys
import time
import logging
import select
import tty
import termios
import uuid
import json

import ocr
import query

logging.basicConfig(format='[%(asctime)s](%(levelname)s) %(message)s', level=logging.INFO)

kResultsFolder = "results"
kImagesFolder = "images"

class MilliWatson:

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ocr = ocr.OCR()
        self.wb = query.WebQuery()
        self.data = {}

        self.logger.info("Monitoring keyboard commands: c - capture")
        with NonBlockingConsole() as nbc:
            while True:
                ch = nbc.get_data()
                if ch == 'c':  # fwd
                    self.logger.info("Capturing...")
                    id = uuid.uuid1()
                    filename = kImagesFolder+"/capture_{}".format(id)
                    # Setup for left snap-aligned quicktime window of iPhone 6S screen capture
                    self.ocr.capture_screen(bbox=(0, 23, 494, 1000), save_filename=filename)
                    if not self.processImage(id):
                        continue
                    self.run_query(self.data)
                    self.save_data(self.data)

                time.sleep(0.01)

    def processImage(self, id):
        try:
            self.data['question'] = self.clense(self.ocr.get_question())
            self.data['answers'] = []
            self.data['answers'].append(self.clense(self.ocr.get_answer_A()))
            self.data['answers'].append(self.clense(self.ocr.get_answer_B()))
            self.data['answers'].append(self.clense(self.ocr.get_answer_C()))
            self.data['id'] = str(id)
            return True
        except Exception as e:
            self.logger.error("Error parsing image {}".format(e))
        return False

    def clense(self, in_string):
        # remove hyphens followed by spaces
        in_string = in_string.replace("- ","")
        # remove special characters
        in_string = in_string.replace("|","I")
        # convert all lower
        in_string = in_string.lower()
        # convert digits to text
        words = in_string.split(" ")
        words_no_digits = []
        for word in words:
            try:
                words_no_digits.append(int(word))
            except:
                words_no_digits.append(word)
        return " ".join(words_no_digits)

    def run_query(self, data):
        self.wb.search_google(data['question'])
        counts = self.wb.answer_frequency(data['answers'])
        self.data['results'] = counts

    def show_data(self):
        print(self.data)

    def save_data(self, data):
        filename = kResultsFolder+"/results_{}.json".format(data['id'])
        with open(filename, 'w') as fp:
            json.dump(data, fp, indent=4)
        self.logger.info("Saved results to {}".format(filename))


class NonBlockingConsole(object):

    def __enter__(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def get_data(self):
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            return sys.stdin.read(1)
        return False

if __name__ == "__main__":
    mW = MilliWatson()
