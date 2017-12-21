#!/usr/bin/env python3

import sys
import time
import logging
import select
import tty
import json
import signal
import termios
import threading
import uuid

import ocr
import query

logging.basicConfig(
    format='[%(asctime)s](%(levelname)s) %(message)s', level=logging.INFO)

kResultsFolder = "results"
kImagesFolder = "images"


class MilliWatson:

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ocr = ocr.OCR()
        self.wb = query.WebQuery()
        self.data = {}
        self.running = False
        self.exiting = False

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGHUP, self.signal_handler)

        self.t = threading.Thread(target=self.getInput)
        self.t.setDaemon(True)
        self.t.start()

        # start main capture loop
        self.run_loop()

    def getInput(self):
        self.logger.info("Monitoring keyboard commands: c - capture")
        with NonBlockingConsole() as nbc:
            while not self.exiting:
                ch = nbc.get_data()
                if ch == 'c':  # fwd
                    self.logger.info("Capturing one...")
                    self.capture()
                    self.process_capture()
                if ch == 'a':
                    self.logger.info("Auto capture started")
                    self.running = True
                if ch == 's':
                    self.logger.info("Auto capture stopped")
                    self.running = False
                time.sleep(0.01)

    def run_loop(self):
        while not self.exiting:
            if self.running:
                self.capture()
                # check for validity here
            time.sleep(0.2)

    def capture(self):
        # this is setup for iPhoneX
        self.ocr.capture_screen(bbox=(0, 23, 405, 1000))

    def process_capture(self):
        id = uuid.uuid1()
        if not self.run_ocr(id):
            return False
        if not self.run_query(self.data):
            return False
        self.save_data(self.data)
        filename = kImagesFolder + "/capture_{}".format(id)
        self.ocr.save_image(filename)
        return True

    def run_ocr(self, id):
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
        in_string = in_string.replace("-", "")
        # remove special characters
        in_string = in_string.replace("|", "I")
        # convert all lower
        in_string = in_string.lower()
        # convert digits to text
        words = in_string.split(" ")
        words_no_digits = []
        for word in words:
            try:
                words_no_digits.append(int(word))
            except Exception as e:
                words_no_digits.append(word)
        return " ".join(words_no_digits)

    def run_query(self, data):
        if not self.wb.search_google(data['question']):
            return False
        counts = self.wb.answer_frequency(data['answers'])
        self.data['results'] = counts
        return True

    def show_data(self):
        print(self.data)

    def save_data(self, data):
        filename = kResultsFolder + "/results_{}.json".format(data['id'])
        with open(filename, 'w') as fp:
            json.dump(data, fp, indent=4)
        self.logger.info("Saved results to {}".format(filename))

    def signal_handler(self, s, f):
        self.logger.info("Exiting!")
        self.running = False
        self.exiting = True


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
